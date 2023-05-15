from pyclbr import Function
import json
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnParameter,
    Aws,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as target,
    aws_sqs as sqs,
    aws_lambda_event_sources as source,
    aws_iam as _iam,
    aws_opensearchservice,
    aws_secretsmanager,
    aws_ec2
)

class SmartSearchStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Part 1. Create OpenSearch
        ops_domain_name = 'smart-search'
        master_user_secret = aws_secretsmanager.Secret(self, "OpenSearchMasterUserSecret",          
          generate_secret_string=aws_secretsmanager.SecretStringGenerator(
            secret_string_template=json.dumps({"username": "admin"}),
            generate_string_key="password",
            # Master password must be at least 8 characters long and contain at least one uppercase letter,
            # one lowercase letter, one number, and one special character.
            password_length=8
        )
        )
        ops_domain = aws_opensearchservice.Domain(self, "OpenSearch",
        domain_name=ops_domain_name,
        version=aws_opensearchservice.EngineVersion.OPENSEARCH_1_3,
        capacity={
            "master_nodes": 0,
            "master_node_instance_type": "m5.xlarge.search",
            "data_nodes": 1,
            "data_node_instance_type": "m5.xlarge.search"
        },
        ebs={
            "volume_size": 10,
            "volume_type": aws_ec2.EbsDeviceVolumeType.GP3
        },
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
        use_unsigned_basic_auth=True,
        removal_policy=cdk.RemovalPolicy.DESTROY # default: cdk.RemovalPolicy.RETAIN
        )
        cdk.Tags.of(ops_domain).add('Name', 'smartsearch-ops')

        # self.sg_search_client = sg_use_opensearch
        self.search_domain_endpoint = ops_domain.domain_endpoint
        self.search_domain_arn = ops_domain.domain_arn

        host_endpoint = cdk.CfnOutput(self, 'OPSDomainEndpoint', value=self.search_domain_endpoint, export_name='OPSDomainEndpoint')
        cdk.CfnOutput(self, 'OPSDashboardsURL', value=f"{self.search_domain_endpoint}/_dashboards/", export_name='OPSDashboardsURL')
        
        #Part 2. Create Lambda Functions

        #2.1 role and policy (smartsearch knn doc,opensearch-search-knn)
        knn_doc_policy_statement = _iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'es:ESHttpPost' ,
                ],
            resources=['*'] # 可根据需求进行更改
        )
        knn_doc_lambda_role = _iam.Role(
            self, 'knn_doc_lambda_role_Role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        knn_doc_lambda_role.add_to_policy(knn_doc_policy_statement)
        knn_lambda_role =knn_doc_lambda_role

        # role and policy (insert feedback)
        fb_policy_statement = _iam.PolicyStatement(
            actions=[
                'dynamodb:*' ,
                ],
            resources=['*'] # 可根据需求进行更改
        )
        fb_lambda_role = _iam.Role(
            self, 'fb_lambda_role_Role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        fb_lambda_role.add_to_policy(fb_policy_statement)
        # role and policy (opensearch-lambda-post_selection)
        ps_policy_statement = _iam.PolicyStatement(
            actions=[
                'lambda:InvokeFunctionUrl' ,
                'lambda:InvokeFunction',
                'lambda:InvokeAsync'
                ],
            resources=['*'] # 可根据需求进行更改
        )
        ps_lambda_role = _iam.Role(
            self, 'ps_lambda_role_Role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        ps_lambda_role.add_to_policy(ps_policy_statement)

        # role and policy (open-search_xgb_train_deploy)
        xgb_policy_statement = _iam.PolicyStatement(
            actions=[
                'ecr:*' ,
                ],
            resources=['*'] # 可根据需求进行更改
        )
        xgb_lambda_role = _iam.Role(
            self, 'xgb_lambda_role_Role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        xgb_lambda_role.add_to_policy(xgb_policy_statement)

        #define lambda function, knn_fad role is not defined by guideline
        
        # self.opensearch_search_knn_lambda = self.define_lambda_function('opensearch-search-knn',knn_lambda_role)
        # self.opensearch_search_knn_faq_lambda = self.define_lambda_function('opensearch-search-knn-faq',knn_lambda_role)
        # self.opensearch_lambda_insert_feedback_lambda = self.define_lambda_function('opensearch-lambda-insert_feedback',fb_lambda_role)
        # self.opensearch_lambda_post_selection_lambda = self.define_lambda_function('opensearch-lambda-post_selection',ps_lambda_role)
        # self.open_search_xgb_train_deploy_lambda = self.define_lambda_function('open-search_xgb_train_deploy',xgb_lambda_role)
        # self.opensearch_search_knn_doc_lambda = self.define_lambda_function('opensearch-search-knn-doc',knn_doc_lambda_role)

        self.opensearch_search_knn_lambda = self.define_lambda_cfnfunction('opensearch-search-knn',knn_lambda_role.role_arn)
        self.opensearch_search_knn_faq_lambda = self.define_lambda_cfnfunction('opensearch-search-knn-faq',knn_lambda_role.role_arn)
        self.opensearch_lambda_insert_feedback_lambda = self.define_lambda_cfnfunction('opensearch-lambda-insert_feedback',fb_lambda_role.role_arn)
        self.opensearch_lambda_post_selection_lambda = self.define_lambda_cfnfunction('opensearch-lambda-post_selection',ps_lambda_role.role_arn)
        self.open_search_xgb_train_deploy_lambda = self.define_lambda_cfnfunction('open-search_xgb_train_deploy',xgb_lambda_role.role_arn)
        self.opensearch_search_knn_doc_lambda = self.define_lambda_cfnfunction('opensearch-search-knn-doc',knn_doc_lambda_role.role_arn)
        #add depends on lambda 
        #self.opensearch_search_knn_doc_lambda.add_dependency(host_endpoint)

        #add parameter into lambda environment
        # self.opensearch_search_knn_doc_lambda.add_environment("username", username.value_as_string)
        # self.opensearch_search_knn_doc_lambda.add_environment("password", password.value_as_string)
        self.opensearch_search_knn_doc_lambda.add_environment("host",self.search_domain_endpoint)
      

    def define_lambda_function(self, function_name,role):
        lambda_function = _lambda.Function(
            self, function_name,
            function_name = function_name,
            runtime = _lambda.Runtime.PYTHON_3_9,
            role = role,
            code = _lambda.Code.from_asset('../lambda/'+function_name),
            handler = 'lambda_function' + '.lambda_handler',
            timeout = Duration.seconds(10),
            reserved_concurrent_executions=100,
        )
        return lambda_function
    
    def define_lambda_cfnfunction(self, function_name,role):
        lambda_function = _lambda.CfnFunction(
            self, function_name,
            function_name = function_name,
            runtime = 'python3.9',
            role = role,
            code = _lambda.Code.from_asset('../lambda/'+function_name),
            handler = 'lambda_function' + '.lambda_handler',
            timeout = 10,
            reserved_concurrent_executions=100,
        )
        return lambda_function
