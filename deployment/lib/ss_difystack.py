from constructs import Construct

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)


class DifyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve default VPC
        vpc = ec2.Vpc.from_lookup(self, 'VPC', is_default=True)

        # Create a new security group
        security_group = ec2.SecurityGroup(
            self, 'DifySecurityGroup',
            vpc=vpc,
            allow_all_outbound=True,
        )
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'Allow HTTP access')

        # Define the user data script
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            '#!/bin/bash\n\n'
            'yum install git docker -y && '
            'systemctl start docker && '
            'systemctl enable docker && '
            'curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && '
            'chmod +x /usr/local/bin/docker-compose && '
            'git clone https://github.com/langgenius/dify.git && '
            'cd dify/docker && '
            'docker-compose up -d'
        )

        # Create EC2 instance to install Dify
        cfn_installation_instance = ec2.Instance(
            self, 'DifyInstallationInstance',
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.C7A, ec2.InstanceSize.XLARGE),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            security_group=security_group,
            user_data=user_data
        )

        CfnOutput(
            self, 'DifyHost',
            value=f'http://{cfn_installation_instance.instance_public_ip}',
            export_name='DifyHost'
        )
