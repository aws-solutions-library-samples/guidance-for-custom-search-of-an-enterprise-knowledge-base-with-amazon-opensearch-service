import json

import aws_cdk as cdk

from aws_cdk import (
  Stack,
  aws_ec2,
  aws_iam as _iam,
  aws_opensearchservice,
  aws_secretsmanager
)
from constructs import Construct

class OpenSearchStack(Stack):

  def __init__(self, scope: Construct, construct_id: str , **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)


    ops_domain_name = 'smartsearch'

    master_user_secret = aws_secretsmanager.Secret(self, "OpenSearchMasterUserSecret",
      generate_secret_string=aws_secretsmanager.SecretStringGenerator(
        secret_string_template=json.dumps({"username": "admin"}),
        generate_string_key="password",
        # Master password must be at least 8 characters long and contain at least one uppercase letter,
        # one lowercase letter, one number, and one special character.
        password_length=12
      ),
      secret_name = "opensearch-master-user1"
    )

    #XXX: aws cdk elastsearch example - https://github.com/aws/aws-cdk/issues/2873
    # You should camelCase the property names instead of PascalCase
    ops_domain = aws_opensearchservice.Domain(self, "OpenSearch",
      domain_name=ops_domain_name,
      #XXX: Supported versions of OpenSearch and Elasticsearch
      # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html#choosing-version
      version=aws_opensearchservice.EngineVersion.OPENSEARCH_2_9,
      #XXX: Amazon OpenSearch Service - Current generation instance types
      # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/supported-instance-types.html#latest-gen
      # access_policies=[_iam.PolicyStatement(
      #           actions=[
      #             "es:Describe*",
      #             "es:List*",
      #             "es:Get*",
      #             "es:ESHttp*"], 
      #           resources=['*'] # 可根据需求进行更改
      #       ),],
      capacity={
        "master_nodes": 0,
        "master_node_instance_type": "m5.large.search",
        "data_nodes": 1,
        "data_node_instance_type": "m5.large.search"
      },
      ebs={
        "volume_size": 20,
        "volume_type": aws_ec2.EbsDeviceVolumeType.GP3
      },
      #XXX: az_count must be equal to vpc subnets count.
      # zone_awareness={
      #   "availability_zone_count": 2,
      #   "enabled": True
      # },
      fine_grained_access_control=aws_opensearchservice.AdvancedSecurityOptions(
        master_user_name=master_user_secret.secret_value_from_json("username").unsafe_unwrap(),
        master_user_password=master_user_secret.secret_value_from_json("password")
      ),
      # Enforce HTTPS is required when fine-grained access control is enabled.
      enforce_https=True,
      # Node-to-node encryption is required when fine-grained access control is enabled
      node_to_node_encryption=True,
      # Encryption-at-rest is required when fine-grained access control is enabled.
      encryption_at_rest={
        "enabled": True
      },
      use_unsigned_basic_auth=True,   #default: False
      # security_groups=[sg_opensearch_cluster],
      #XXX: For domains running OpenSearch or Elasticsearch 5.3 and later, OpenSearch Service takes hourly automated snapshots
      # Only applies for Elasticsearch versions below 5.3
      # automated_snapshot_start_hour=17, # 2 AM (GTM+9)
      # vpc=vpc,
      #XXX: az_count must be equal to vpc subnets count.
      # vpc_subnets=[aws_ec2.SubnetSelection(one_per_az=True, subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS)],
      removal_policy=cdk.RemovalPolicy.DESTROY # default: cdk.RemovalPolicy.RETAIN
    )
    cdk.Tags.of(ops_domain).add('Name', 'smartsearch-ops')

    # self.sg_search_client = sg_use_opensearch
    self.search_domain_endpoint = ops_domain.domain_endpoint
    self.search_domain_arn = ops_domain.domain_arn

    cdk.CfnOutput(self, 'OPSDomainEndpoint1', value=self.search_domain_endpoint, export_name='OPSDomainEndpoint1')
    cdk.CfnOutput(self, 'OPSDashboardsURL1', value=f"{self.search_domain_endpoint}/_dashboards/", export_name='OPSDashboardsURL1')