from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_efs as efs,
    App, CfnOutput, Duration, Stack
)

app = App()
name = "llmEcs"
stack = Stack(app, name)

vpc = ec2.Vpc(
            stack, "Vpc",
            cidr="10.0.0.0/16",
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="PublicSubnet",
                    cidr_mask=24,
                )
            ],
      gateway_endpoints={
        "S3": ec2.GatewayVpcEndpointOptions(
          service=ec2.GatewayVpcEndpointAwsService.S3
        )
      }
        )

cluster = ecs.Cluster(
    stack, name,
    vpc=vpc
)
ebs_volume = [ec2.BlockDevice(device_name="/dev/xvda", volume=ec2.BlockDeviceVolume.ebs(volume_size=100, volume_type=ec2.EbsDeviceVolumeType.GP3))]
efs_file_system = efs.FileSystem(
            stack, "llmFileSystem",
            vpc=vpc,
            throughput_mode=efs.ThroughputMode.BURSTING
        )

commands = '''
sudo su
yum -q update -y
yum -q install python3.7 -y
yum -q install -y wget
yum -q install -y unzip

cd /home/ec2-user
wget -q https://bootstrap.pypa.io/get-pip.py
su -c "python3.7 get-pip.py --user" -s /bin/sh ec2-user
su -c "/home/ec2-user/.local/bin/pip3 install boto3 --user" -s /bin/sh ec2-user

curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

echo 'alias aws2=/usr/local/bin/aws' >> .bash_profile

'''
user_data = ec2.UserData.for_linux()
user_data.add_commands(commands)

ec2_role = iam.Role(stack, "llmRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
ec2_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
launch_template = ec2.LaunchTemplate(
            stack,
            "LaunchTemplate",
            block_devices=ebs_volume,
            instance_type=ec2.InstanceType("g5.2xlarge"),
            key_name="ohio20",  # needs to be created manually
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.GPU), # custom ECS AMI created manually via https://github.com/aws/amazon-ecs-ami
            security_group=ec2.SecurityGroup(stack, "llmSecurityGroup", vpc=vpc),
            role=ec2_role,
            user_data=user_data,
        )
launch_template.connections.allow_to_default_port(efs_file_system)
launch_template.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
efs_file_system.connections.allow_default_port_from_any_ipv4()


asg = autoscaling.AutoScalingGroup(
    stack, "DefaultAutoScalingGroup",
    launch_template=launch_template,
    vpc=vpc,
)

capacity_provider = ecs.AsgCapacityProvider(stack, "AsgCapacityProvider",
    auto_scaling_group=asg,
    enable_managed_termination_protection=False,
    enable_managed_scaling=True,
    enable_managed_draining=False

)

cluster.add_asg_capacity_provider(capacity_provider)

task_role = iam.Role(
    stack, "ecsTaskRole",
    assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
)
task_managed_policy_names = ["AmazonEC2ContainerRegistryFullAccess", 
                        "AmazonECS_FullAccess",
                        "CloudWatchLogsFullAccess",
                        "AmazonS3FullAccess"
                        ]
for policy in task_managed_policy_names:
    task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(policy))


execution_role = iam.Role(
    stack, "ecsExecutionRole",
    assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
)

execution_managed_policy_names = ["AmazonEC2ContainerRegistryFullAccess", 
                        "AmazonECS_FullAccess",
                        "CloudWatchLogsFullAccess",
                        "AmazonS3FullAccess"
                        ]

for policy in execution_managed_policy_names:
    execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(policy))



# Create Task Definition
task_definition = ecs.Ec2TaskDefinition(
    stack, "TaskDef",
    task_role=task_role,
    execution_role=execution_role,
    network_mode=ecs.NetworkMode.AWS_VPC,
    volumes=[
                ecs.Volume(
                    name="llmEfs",
                    efs_volume_configuration=ecs.EfsVolumeConfiguration(
                        file_system_id=efs_file_system.file_system_id,
                        root_directory="/"
                    ),
                )
            ],
    )

container = task_definition.add_container(
    "llm",
    image=ecs.ContainerImage.from_registry("310850127430.dkr.ecr.us-west-2.amazonaws.com/llm-api:pytorch"), #####需要提前build
    cpu=4096,
    memory_limit_mib=12288,
    essential=True,
    command=["python","api/server.py"],
    environment={
                'EMBEDDING_NAME': 'checkpoints/m3e-base', #############
                'MODEL_PATH': 'checkpoints/Baichuan2-13B-Chat', #################
                'MODEL_NAME': 'baichuan2-13b-chat',
                'PORT': '8000',
                'LOAD_IN_8BIT': 'true',
            },

    health_check=ecs.HealthCheck(
        command=["CMD-SHELL", "true"],
        interval=Duration.minutes(3),
        retries=5,
        start_period=Duration.minutes(5),
        timeout=Duration.seconds(10)),

    gpu_count=1, 

    logging=ecs.AwsLogDriver(
                stream_prefix="llmapi", 
            ),
)
container.add_mount_points(ecs.MountPoint(container_path="/workspace", source_volume="llmEfs",read_only=False))
container.add_ulimits(ecs.Ulimit(soft_limit=67108864, hard_limit=67108864, name=ecs.UlimitName.STACK))
container.add_ulimits(ecs.Ulimit(soft_limit=-1, hard_limit=-1, name=ecs.UlimitName.MEMLOCK))


port_mapping = ecs.PortMapping(
    container_port=8000,
    host_port=8000,
    protocol=ecs.Protocol.TCP
)

container.add_port_mappings(port_mapping)

service = ecs.Ec2Service(
    stack, "Service",
    cluster=cluster,
    task_definition=task_definition,
    desired_count=1,
    circuit_breaker=ecs.DeploymentCircuitBreaker(
        enable=False,
    )
)


lb = elbv2.ApplicationLoadBalancer(
    stack, "LB",
    vpc=vpc,
    internet_facing=True
)

listener = lb.add_listener(
    "PublicListener",
    port=80,
    open=True
)


asg.connections.allow_from(lb, port_range=ec2.Port.tcp_range(32768, 65535), description="allow incoming traffic from ALB")

health_check = elbv2.HealthCheck(
    interval=Duration.seconds(20),
    path="/",
    timeout=Duration.seconds(5),
    unhealthy_threshold_count=10,
    healthy_threshold_count=2,
    healthy_http_codes="400-499"
)

# Attach ALB to ECS Service
listener.add_targets(
    "ECS",
    port=80,
    targets=[service],
    health_check=health_check,
)

CfnOutput(
    stack, "LoadBalancerDNS",
    value="http://"+lb.load_balancer_dns_name
)

app.synth()
