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
    Duration

)
import os


class SmartSearchQaStack(Stack):

    def __init__(self, scope: Construct, id: str, host: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # get the opensearch index
        index = self.node.try_get_context("index")
        embedding_endpoint_name = self.node.try_get_context("embedding_endpoint_name")
        llm_embedding_name = self.node.try_get_context("llm_embedding_name")
        language = self.node.try_get_context("language")
        
        search_engine_opensearch = self.node.try_get_context("search_engine_opensearch")
        search_engine_kendra = self.node.try_get_context("search_engine_kendra")
        search_engine_zilliz = self.node.try_get_context("search_engine_zilliz")
        zilliz_endpoint = self.node.try_get_context("zilliz_endpoint")
        zilliz_token = self.node.try_get_context("zilliz_token")

        # configure the lambda role
        _langchain_processor_role_policy = iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'lambda:AWSLambdaBasicExecutionRole',
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
        
        langchain_processor_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonKendraFullAccess")
        )

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
            reserved_concurrent_executions=100
        )
        langchain_processor_qa_function.add_environment("host", host)
        langchain_processor_qa_function.add_environment("index", index)
        langchain_processor_qa_function.add_environment("language", language)
        langchain_processor_qa_function.add_environment("embedding_endpoint_name", embedding_endpoint_name)
        langchain_processor_qa_function.add_environment("llm_embedding_name", llm_embedding_name)
        langchain_processor_qa_function.add_environment("search_engine_opensearch", str(search_engine_opensearch))
        langchain_processor_qa_function.add_environment("search_engine_kendra", str(search_engine_kendra))
        langchain_processor_qa_function.add_environment("search_engine_zilliz", str(search_engine_zilliz))
        langchain_processor_qa_function.add_environment("zilliz_endpoint", str(zilliz_endpoint))
        langchain_processor_qa_function.add_environment("zilliz_token", str(zilliz_token))

        qa_api = apigw.RestApi(self, 'smart-search-qa-api',
                               default_cors_preflight_options=apigw.CorsOptions(
                                   allow_origins=apigw.Cors.ALL_ORIGINS,
                                   allow_methods=apigw.Cors.ALL_METHODS
                               ),
                               endpoint_types=[apigw.EndpointType.REGIONAL]
                               )

        langchain_processor_qa_resource = qa_api.root.add_resource(
            'langchain_processor_qa',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
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
                                    partition_key=dynamodb.Attribute(name="session-id",
                                                                     type=dynamodb.AttributeType.STRING)
                                    )

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
        langchain_processor_qa_function.add_environment("dynamodb_table_name", chat_table.table_name)
