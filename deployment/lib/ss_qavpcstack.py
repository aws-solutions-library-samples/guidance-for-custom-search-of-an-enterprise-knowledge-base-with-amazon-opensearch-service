from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    aws_ec2,
    Duration

)
import os


class SmartSearchQaVPCStack(Stack):

    def __init__(self, scope: Construct, id: str, ops_endpoint: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # get the opensearch index
        index = self.node.try_get_context("index")
        embedding_endpoint_name = self.node.try_get_context("embedding_endpoint_name")
        llm_embedding_name = self.node.try_get_context("llm_embedding_name")
        language = self.node.try_get_context("language")
        
        # configure the lambda role
        _langchain_processor_role_policy = iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'lambda:AWSLambdaBasicExecutionRole',
                'ec2:CreateNetworkInterface',
                'ec2:DescribeNetworkInterfaces',
                'ec2:DeleteNetworkInterface',
                'secretsmanager:SecretsManagerReadWrite'
            ],
            resources=['*']  # 可根据需求进行更改
        )
        langchain_processor_role = iam.Role(
            self, 'langchain_processor_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        langchain_processor_role.add_to_policy(_langchain_processor_role_policy)

        langchain_processor_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        
        langchain_processor_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        )

        langchain_processor_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        
        # To support VPC deployment by sf 
        vpc_name = self.node.try_get_context('vpc_name')
        if vpc_name != "undefined":
            subnet_name = self.node.try_get_context("subnet_name")
            subnet_id = self.node.try_get_context("subnet_id")
            zone_id = self.node.try_get_context("zone_id")
            private_subnet = aws_ec2.Subnet.from_subnet_attributes(self,subnet_name, availability_zone = zone_id, subnet_id = subnet_id)
            vpc_subnets_selection = aws_ec2.SubnetSelection(subnets = [private_subnet])
        else: 
            private_subnet = vpc.select_subnets(subnet_name='Private')
            vpc_subnets_selection = aws_ec2.SubnetSelection(subnets = [private_subnet])
        # End of VPC deployment  

        # add langchain processor for smart query and answer
        function_name_qa = 'langchain_processor_qa'
        langchain_processor_qa_function = _lambda.Function(
            self, function_name_qa,
            function_name=function_name_qa,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=langchain_processor_role,
            code=_lambda.Code.from_asset('../lambda/' + function_name_qa),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            vpc = vpc,
            vpc_subnets = vpc_subnets_selection,
            reserved_concurrent_executions=100
        )
        langchain_processor_qa_function.add_environment("host",ops_endpoint)
        langchain_processor_qa_function.add_environment("index",index)
        langchain_processor_qa_function.add_environment("language",language)
        langchain_processor_qa_function.add_environment("embedding_endpoint_name",embedding_endpoint_name)
        langchain_processor_qa_function.add_environment("llm_embedding_name",llm_embedding_name)
        
        
        qa_api = apigw.RestApi( self,'smart-search-qa-api', 
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            ),
            endpoint_types=[apigw.EndpointType.REGIONAL]
        )
        
        langchain_processor_qa_resource = qa_api.root.add_resource(
            'langchain_processor_qa',            
            default_cors_preflight_options= apigw.CorsOptions(
            allow_methods=['GET', 'OPTIONS'],
            allow_origins= apigw.Cors.ALL_ORIGINS)
        )
    
        langchain_processor_qa_integration = apigw.LambdaIntegration(
                langchain_processor_qa_function,
                proxy=True,
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code="200",
                        response_parameters={
                            'method.response.header.Access-Control-Allow-Origin': "'*'"
                        }
                    )
                ]
        )

        langchain_processor_qa_resource.add_method(
            'GET', 
            langchain_processor_qa_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

        chat_table = dynamodb.Table(self, "chat_session_table", 
            partition_key=dynamodb.Attribute(name="session-id", type=dynamodb.AttributeType.STRING)
        );
        
        dynamodb_role = iam.Role(
            self, 'dynamodb_role',
            assumed_by=iam.ServicePrincipal('dynamodb.amazonaws.com')
        )
        dynamodb_role_policy = iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                's3:AmazonS3FullAccess',
                'lambda:AWSLambdaBasicExecutionRole',
            ],
            effect=iam.Effect.ALLOW,
            resources=['*']
        )
        dynamodb_role.add_to_policy(dynamodb_role_policy)
        chat_table.grant_read_write_data(dynamodb_role)
        langchain_processor_qa_function.add_environment("dynamodb_table_name",chat_table.table_name)
