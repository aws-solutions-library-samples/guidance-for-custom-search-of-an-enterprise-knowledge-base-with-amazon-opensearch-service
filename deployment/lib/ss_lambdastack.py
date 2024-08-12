from pyclbr import Function
import json
from constructs import Construct

from lib.ss_osstack import OpenSearchStack
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnParameter,
    Aws,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as _iam,
    aws_sqs as sqs,
    aws_glue as glue,
    aws_s3_deployment as s3deploy,
    ContextProvider,
    RemovalPolicy
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration
from aws_cdk import aws_apigatewayv2_alpha as apigwv2
from aws_cdk.aws_lambda_event_sources import DynamoEventSource
from aws_cdk.aws_lambda_event_sources import SqsEventSource
import os

binary_media_types = ["multipart/form-data"]


class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, search_engine_key: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # get value from opensearch stack
        if self.node.try_get_context("search_engine_opensearch"):
            host = "https://" + search_engine_key + "/"
        else:
            host = search_engine_key

        # get CloudFormation parameter

        func_selection = self.node.try_get_context("selection")

        self.langchain_processor_qa_layer = _lambda.LayerVersion(
            self, 'QALambdaLayer',
            code=_lambda.Code.from_asset('../lambda/langchain_processor_layer'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='QA Library'
        )

        print("These functions are selected (configuration is in cdk.json context 'selection'):  ", func_selection)
        
        if 'text_qa' in func_selection:
            text_qa_func = self.create_text_qa_func(search_engine_key=search_engine_key)
            
        if 'multi_modal_qa' in func_selection:
            multi_modal_qa_func = self.create_multi_modal_qa_func(search_engine_key=search_engine_key)

        # Create Lambda Function for Content Moderation
        content_moderation_func = self.create_content_moderation_func()

            
        # api gateway resource
        api = apigw.RestApi(self, 'smartsearch-api',
                            # default_cors_preflight_options=apigw.CorsOptions(
                            #     allow_origins=apigw.Cors.ALL_ORIGINS,
                            #     allow_methods=apigw.Cors.ALL_METHODS
                            # ),
                            endpoint_types=[apigw.EndpointType.REGIONAL],
                            binary_media_types=binary_media_types
                            )

        websocket_table = dynamodb.Table(self, "websocket",
                                         partition_key=dynamodb.Attribute(name="id",
                                                                          type=dynamodb.AttributeType.STRING),
                                         removal_policy=RemovalPolicy.DESTROY
                                         )

        _websocket_policy = _iam.PolicyStatement(
            actions=[
                'lambda:*',
                'apigateway:*',
                'dynamodb:*',
                'logs:*',
            ],
            resources=['*']  
        )
        websocket_role = _iam.Role(
            self, 'websocket_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        websocket_role.add_to_policy(_websocket_policy)

        websocket_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )

        table_name = websocket_table.table_name

        connect_function_name = 'websocket_connect'
        websocketconnect = _lambda.Function(
            self, connect_function_name,
            function_name=connect_function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=websocket_role,
            code=_lambda.Code.from_asset('../lambda/' + connect_function_name),
            handler='lambda_function' + '.lambda_handler',
        )
        websocketconnect.add_environment("TABLE_NAME", table_name)

        disconnect_function_name = 'websocket_disconnect'
        websocketdisconnect = _lambda.Function(
            self, disconnect_function_name,
            function_name=disconnect_function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=websocket_role,
            code=_lambda.Code.from_asset('../lambda/' + disconnect_function_name),
            handler='lambda_function' + '.lambda_handler',
        )
        websocketdisconnect.add_environment("TABLE_NAME", table_name)

        default_function_name = 'websocket_default'
        websocketdefault = _lambda.Function(
            self, default_function_name,
            function_name=default_function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=websocket_role,
            code=_lambda.Code.from_asset('../lambda/' + disconnect_function_name),
            handler='lambda_function' + '.lambda_handler',
        )
        websocketdefault.add_environment("TABLE_NAME", table_name)

        search_function_name = 'websocket_search'
        websocketsearch = _lambda.Function(
            self, search_function_name,
            function_name=search_function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=websocket_role,
            code=_lambda.Code.from_asset('../lambda/' + search_function_name),
            handler='lambda_function' + '.lambda_handler',
        )
        websocketsearch.add_environment("TABLE_NAME", table_name)
        websocketsearch.add_environment("DIR_NAME", "search")

        #publish a new version
        # version = _lambda.Version(
        #     self, "websocketsearchVersion",
        #     lambda_=websocketsearch,
        #     description="v1"
        # )

        # create an alias and provision concurrency=1
        # websocketsearchAlias = _lambda.Alias(
        #     self, "websocketsearchAlias",
        #     alias_name="prod",
        #     version=version,
        #     provisioned_concurrent_executions=1
        # )

        web_socket_api = apigwv2.WebSocketApi(self, "websocketapi")
        apigwv2.WebSocketStage(self, "prod",
                               web_socket_api=web_socket_api,
                               stage_name="prod",
                               auto_deploy=True
                               )
        web_socket_api.add_route("search",
                                 integration=WebSocketLambdaIntegration("SearchIntegration", websocketsearch)
                                 )
        web_socket_api.add_route("$connect",
                                 integration=WebSocketLambdaIntegration("SearchIntegration", websocketconnect)
                                 )
        web_socket_api.add_route("$disconnect",
                                 integration=WebSocketLambdaIntegration("SearchIntegration", websocketdisconnect)
                                 )
        web_socket_api.add_route("$default",
                                 integration=WebSocketLambdaIntegration("SearchIntegration", websocketdefault)
                                 )

        
        # cfn output
        CN_SUFFIX = ".cn" if "cn-" in os.getenv('AWS_REGION') else ""
        web_socket_url = f"wss://{web_socket_api.api_id}.execute-api.{os.getenv('AWS_REGION')}.amazonaws.com{CN_SUFFIX}/prod"
        cdk.CfnOutput(self, 'web_socket_api', value=web_socket_url, export_name='WebSocketApi')

        chat_table = self.create_chat_talbe()
            
        if 'text_qa' in func_selection and text_qa_func is not None:
            text_qa_func.add_environment("api_gw", web_socket_api.api_id)
            self.create_apigw_resource_method_for_text_qa(
                api=api,
                text_qa_function=text_qa_func,
                chat_table=chat_table
            )

        if 'multi_modal_qa' in func_selection and multi_modal_qa_func is not None:
            multi_modal_qa_func.add_environment("api_gw", web_socket_api.api_id)
            self.create_apigw_resource_method_for_multi_modal_qa(
                api=api,
                multi_modal_qa_function=multi_modal_qa_func,
                chat_table=chat_table
            )

        self.create_file_upload_prerequisites(api, search_engine_key)

        self.create_apigw_resource_method_for_content_moderation(
            api=api,
            func=content_moderation_func
        )
        self.create_knowledge_base_handler(api, search_engine_key)

        self.apigw = api

    def create_chat_talbe(self):
        chat_table = dynamodb.Table(self, "ChatSessionRecord",
                                    partition_key=dynamodb.Attribute(name="session-id",
                                                                     type=dynamodb.AttributeType.STRING),
                                    removal_policy=RemovalPolicy.DESTROY
                                    )

        dynamodb_role = _iam.Role(
            self, 'dynamodb_role',
            assumed_by=_iam.ServicePrincipal('dynamodb.amazonaws.com')
        )
        dynamodb_role_policy = _iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                's3:AmazonS3FullAccess',
                'lambda:AWSLambdaBasicExecutionRole',
            ],
            effect=_iam.Effect.ALLOW,
            resources=['*']
        )
        dynamodb_role.add_to_policy(dynamodb_role_policy)
        chat_table.grant_read_write_data(dynamodb_role)
        return chat_table
        

    def create_apigw_resource_method_for_content_moderation(self, api, func):

        content_moderation_resource = api.root.add_resource(
            'content_moderation_check',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        content_moderation_integraion = apigw.LambdaIntegration(
            func,
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

        content_moderation_resource.add_method(
            'GET',
            content_moderation_integraion,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

    def define_lambda_function(self, function_name, role, timeout=10):
        lambda_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=role,
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.seconds(timeout),
            reserved_concurrent_executions=20
        )
        return lambda_function
        

    def create_text_qa_func(self, search_engine_key):

        index = self.node.try_get_context("index")
        embedding_endpoint_name = self.node.try_get_context("embedding_endpoint_name")
        llm_endpoint_name = self.node.try_get_context("llm_endpoint_name")
        language = self.node.try_get_context("language")
        search_engine_opensearch = self.node.try_get_context("search_engine_opensearch")
        search_engine_kendra = self.node.try_get_context("search_engine_kendra")
        search_engine_zilliz = self.node.try_get_context("search_engine_zilliz")
        zilliz_endpoint = self.node.try_get_context("zilliz_endpoint")
        zilliz_token = self.node.try_get_context("zilliz_token")
        bedrock_aws_region = self.node.try_get_context('bedrock_aws_region')

        # configure the lambda role
        if search_engine_kendra:
            _text_role_policy = _iam.PolicyStatement(
                actions=[
                    'sagemaker:InvokeEndpointAsync',
                    'sagemaker:InvokeEndpoint',
                    'lambda:AWSLambdaBasicExecutionRole',
                    'secretsmanager:SecretsManagerReadWrite',
                    'kendra:DescribeIndex',
                    'kendra:Query',
                    'execute-api:*',  ##############
                    'bedrock:*'
                ],
                resources=['*']  # 可根据需求进行更改
            )
        else:
            _text_role_policy = _iam.PolicyStatement(
                actions=[
                    'sagemaker:InvokeEndpointAsync',
                    'sagemaker:InvokeEndpoint',
                    'lambda:AWSLambdaBasicExecutionRole',
                    'secretsmanager:SecretsManagerReadWrite',
                    'es:ESHttpPost',
                    'bedrock:*',
                    'execute-api:*'  ##############

                ],
                resources=['*']  # 可同时使用opensearch、kendra和zilliz
            )
        text_role = _iam.Role(
            self, 'text_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        text_role.add_to_policy(_text_role_policy)

        text_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaRole")
        )

        text_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        text_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        )

        text_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        if self.node.try_get_context('search_engine_kendra'):
            text_role.add_managed_policy(
                _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonKendraFullAccess")
            )

        # add langchain processor for smart query and answer
        function_name_qa = 'text_qa'
        text_qa_function = _lambda.Function(
            self, function_name_qa,
            function_name=function_name_qa,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=text_role,
            layers=[self.langchain_processor_qa_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name_qa),
            handler='lambda_function' + '.lambda_handler',
            memory_size=256,
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=50
        )
        text_qa_function.add_environment("host", search_engine_key) 
        text_qa_function.add_environment("index", index)
        text_qa_function.add_environment("language", language)
        text_qa_function.add_environment("embedding_endpoint_name", embedding_endpoint_name)
        text_qa_function.add_environment("llm_endpoint_name", llm_endpoint_name)
        text_qa_function.add_environment("search_engine_opensearch", str(search_engine_opensearch))
        text_qa_function.add_environment("search_engine_kendra", str(search_engine_kendra))
        text_qa_function.add_environment("search_engine_zilliz", str(search_engine_zilliz))
        text_qa_function.add_environment("zilliz_endpoint", str(zilliz_endpoint))
        text_qa_function.add_environment("zilliz_token", str(zilliz_token))
        if bedrock_aws_region:
            text_qa_function.add_environment("bedrock_aws_region", str(bedrock_aws_region))

        #publish a new version
        version = _lambda.Version(
            self, "TextQAVersion",
            lambda_=text_qa_function,
            description="v1"
        )

        # create an alias and provision concurrency=1
        # alias = _lambda.Alias(
        #     self, "TextQAAlias",
        #     alias_name="prod",
        #     version=version,
        #     provisioned_concurrent_executions=1
        # )

        return text_qa_function

    def create_multi_modal_qa_func(self, search_engine_key):

        index = self.node.try_get_context("index")
        embedding_endpoint_name = self.node.try_get_context("embedding_endpoint_name")
        llm_endpoint_name = self.node.try_get_context("llm_endpoint_name")
        language = self.node.try_get_context("language")
        search_engine_opensearch = self.node.try_get_context("search_engine_opensearch")
        search_engine_kendra = self.node.try_get_context("search_engine_kendra")
        search_engine_zilliz = self.node.try_get_context("search_engine_zilliz")
        zilliz_endpoint = self.node.try_get_context("zilliz_endpoint")
        zilliz_token = self.node.try_get_context("zilliz_token")
        bedrock_aws_region = self.node.try_get_context('bedrock_aws_region')

        # configure the lambda role
        if search_engine_kendra:
            _multi_modal_role_policy = _iam.PolicyStatement(
                actions=[
                    'sagemaker:InvokeEndpointAsync',
                    'sagemaker:InvokeEndpoint',
                    'lambda:AWSLambdaBasicExecutionRole',
                    'secretsmanager:SecretsManagerReadWrite',
                    'kendra:DescribeIndex',
                    'kendra:Query',
                    'execute-api:*',  ##############
                    'bedrock:*'
                ],
                resources=['*']  # 可根据需求进行更改
            )
        else:
            _multi_modal_role_policy = _iam.PolicyStatement(
                actions=[
                    'sagemaker:InvokeEndpointAsync',
                    'sagemaker:InvokeEndpoint',
                    'lambda:AWSLambdaBasicExecutionRole',
                    'secretsmanager:SecretsManagerReadWrite',
                    'es:ESHttpPost',
                    'bedrock:*',
                    'execute-api:*'  ##############

                ],
                resources=['*']  # 可同时使用opensearch、kendra和zilliz
            )
        multi_modal_role = _iam.Role(
            self, 'multi_modal_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        multi_modal_role.add_to_policy(_multi_modal_role_policy)

        multi_modal_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaRole")
        )

        multi_modal_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        multi_modal_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        )

        multi_modal_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        if self.node.try_get_context('search_engine_kendra'):
            multi_modal_role.add_managed_policy(
                _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonKendraFullAccess")
            )

        # add langchain processor for smart query and answer
        function_name_qa = 'multi_modal_qa'
        multi_modal_qa_function = _lambda.Function(
            self, function_name_qa,
            function_name=function_name_qa,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=multi_modal_role,
            layers=[self.langchain_processor_qa_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name_qa),
            handler='lambda_function' + '.lambda_handler',
            memory_size=256,
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=50
        )
        multi_modal_qa_function.add_environment("host", search_engine_key) 
        multi_modal_qa_function.add_environment("index", index)
        multi_modal_qa_function.add_environment("language", language)
        multi_modal_qa_function.add_environment("embedding_endpoint_name", embedding_endpoint_name)
        multi_modal_qa_function.add_environment("llm_endpoint_name", llm_endpoint_name)
        multi_modal_qa_function.add_environment("search_engine_opensearch", str(search_engine_opensearch))
        multi_modal_qa_function.add_environment("search_engine_kendra", str(search_engine_kendra))
        multi_modal_qa_function.add_environment("search_engine_zilliz", str(search_engine_zilliz))
        multi_modal_qa_function.add_environment("zilliz_endpoint", str(zilliz_endpoint))
        multi_modal_qa_function.add_environment("zilliz_token", str(zilliz_token))
        if bedrock_aws_region:
            multi_modal_qa_function.add_environment("bedrock_aws_region", str(bedrock_aws_region))

        #publish a new version
        version = _lambda.Version(
            self, "MultiModalQAVersion",
            lambda_=multi_modal_qa_function,
            description="v1"
        )

        # create an alias and provision concurrency=1
        # alias = _lambda.Alias(
        #     self, "MultiModalQAAlias",
        #     alias_name="prod",
        #     version=version,
        #     provisioned_concurrent_executions=1
        # )

        return multi_modal_qa_function



    def create_apigw_resource_method_for_text_qa(self, api, text_qa_function, chat_table):

        text_qa_resource = api.root.add_resource(
            'text_qa',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        text_qa_integration = apigw.LambdaIntegration(
            text_qa_function,
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

        text_qa_resource.add_method(
            'GET',
            text_qa_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
        
        text_qa_resource.add_method(
            'POST',
            text_qa_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

        text_qa_function.add_environment("dynamodb_table_name", chat_table.table_name)
        cdk.CfnOutput(self, 'text_chat_table_name', value=chat_table.table_name, export_name='TextChatTableName')


    def create_apigw_resource_method_for_multi_modal_qa(self, api, multi_modal_qa_function, chat_table):

        multi_modal_qa_resource = api.root.add_resource(
            'multi_modal_qa',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        multi_modal_qa_integration = apigw.LambdaIntegration(
            multi_modal_qa_function,
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

        multi_modal_qa_resource.add_method(
            'GET',
            multi_modal_qa_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
        
        multi_modal_qa_resource.add_method(
            'POST',
            multi_modal_qa_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

        multi_modal_qa_function.add_environment("dynamodb_table_name", chat_table.table_name)
        cdk.CfnOutput(self, 'multi_modal_chat_table_name', value=chat_table.table_name, export_name='MultiModalChatTableName')


    def create_apigw_resource_method_for_endpoint_list(self, api, endpoint_list_function):

        endpoint_list_resource = api.root.add_resource(
            'endpoint_list',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        endpoint_list_integration = apigw.LambdaIntegration(
            endpoint_list_function,
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

        endpoint_list_resource.add_method(
            'GET',
            endpoint_list_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

    def create_file_upload_prerequisites(self, api, search_engine_key):
        # Now hardcode for testing first
        ACCOUNT = os.getenv('AWS_ACCOUNT_ID', '')
        REGION = os.getenv('AWS_REGION', '')
        bucket_for_uploaded_files = "intelligent-search-data-bucket" + "-" + ACCOUNT + "-" + REGION
        execution_role_name = self.node.try_get_context("execution_role_name") + REGION
        index = self.node.try_get_context("index")
        language = self.node.try_get_context("language")
        embedding_endpoint_name = self.node.try_get_context("embedding_endpoint_name")
        search_engine_opensearch = self.node.try_get_context("search_engine_opensearch")
        search_engine_zilliz = self.node.try_get_context("search_engine_zilliz")
        zilliz_endpoint = self.node.try_get_context("zilliz_endpoint")
        zilliz_token = self.node.try_get_context("zilliz_token")
        CN_SUFFIX = "-cn" if "cn-" in REGION else ""

        """
        1. Create S3 bucket for storing uploaded files
        """

        _bucket_name = bucket_for_uploaded_files

        _bucket = s3.Bucket(self,
                            id=_bucket_name,
                            bucket_name=_bucket_name,
                            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                            encryption=s3.BucketEncryption.S3_MANAGED,
                            enforce_ssl=True,
                            versioned=False,
                            removal_policy=RemovalPolicy.DESTROY
                            )
        
        _bucket.add_cors_rule(
            allowed_headers=["*"],
            allowed_methods=[
                             s3.HttpMethods.GET,
                             s3.HttpMethods.PUT,
                             s3.HttpMethods.POST
                             ],
            allowed_origins=["*"]
            )

        self.bucket = _bucket
        
        """
        2. Create Execution Role for Uploading file to S3
        IAM RoleName: custom-role-document-ai-upload-to-s3
        """
        _role_name = execution_role_name
        _inline_policies = {
            "AllowS3UploadPermission": _iam.PolicyDocument(
                statements=[
                    _iam.PolicyStatement(
                        actions=[
                            "s3:PutObject",
                        ],
                        resources=[f"arn:aws{CN_SUFFIX}:s3:::{_bucket_name}/*"]),
                ]
            ),
            "AllowLogCreation": _iam.PolicyDocument(
                statements=[
                    _iam.PolicyStatement(
                        actions=[
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:DescribeLogGroups",
                            "logs:DescribeLogStreams",
                            "logs:PutLogEvents",
                            "logs:GetLogEvents",
                            "logs:FilterLogEvents"
                        ],
                        resources=["*"]),
                ])
        }

        _execution_role = _iam.Role(self,
                                    id=_role_name,
                                    role_name=_role_name,
                                    assumed_by=_iam.ServicePrincipal("apigateway.amazonaws.com"),
                                    description="Execution role for uploading file from APIGW to S3 directly.",
                                    inline_policies=_inline_policies
                                    )

        """
        3. Create Lambda for processing file and save to ES
        """
        function_name = 'langchain_processor_dataload'

        _data_load_role_policy = _iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                's3:AmazonS3FullAccess',
                'lambda:AWSLambdaBasicExecutionRole',
                'secretsmanager:SecretsManagerReadWrite',
                'bedrock:*'
            ],
            resources=['*']  # 可根据需求进行更改
        )
        data_load_role = _iam.Role(
            self, 'data_load_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        data_load_role.add_to_policy(_data_load_role_policy)

        data_load_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        data_load_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        )

        data_load_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )

        data_load_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=data_load_role,
            layers=[self.langchain_processor_qa_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=20
        )
        data_load_function.add_environment("host", search_engine_key)
        data_load_function.add_environment("index", index)
        data_load_function.add_environment("language", language)
        data_load_function.add_environment("embedding_endpoint_name", embedding_endpoint_name)
        data_load_function.add_environment("search_engine_opensearch", str(search_engine_opensearch))
        data_load_function.add_environment("search_engine_zilliz", str(search_engine_zilliz))
        data_load_function.add_environment("zilliz_endpoint", str(zilliz_endpoint))
        data_load_function.add_environment("zilliz_token", str(zilliz_token))

        """
        4. Update S3 file notification with Lambda
          prefix is {BUCKET_NAME}/source_data/
        """
        _bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(data_load_function),
            s3.NotificationKeyFilter(
                prefix="source_data/",
            ),
        )

        """
        5. Create S3-based API Gateway
        """
        # Create Resources in below structure
        # /{bucket}/{prefix}/{sub_prefix}/{filename}
        file_upload_root = api.root.add_resource(path_part="file_upload")
        bucket_resource = file_upload_root.add_resource(path_part="{bucket}")
        prefix_resource = bucket_resource.add_resource(path_part="{prefix}")
        sub_prefix_resource = prefix_resource.add_resource(path_part="{sub_prefix}")
        filename_resource = sub_prefix_resource.add_resource(
            path_part="{filename}",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['PUT', 'POST', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS
            )
        )

        # Create S3 Integration for APIGw
        request_parameters = {
            "method.request.path.bucket": True,  # True if param is mandatory
            "method.request.path.filename": True,  # True if param is mandatory
            "method.request.path.prefix": True,  # True if param is mandatory
            "method.request.path.sub_prefix": True  # True if param is mandatory
        }

        request_parameters_in_integration_options = {
            "integration.request.path.bucket": "method.request.path.bucket",
            "integration.request.path.key": "method.request.path.filename",
            "integration.request.path.prefix": "method.request.path.prefix",
            "integration.request.path.sub_prefix": "method.request.path.sub_prefix",
        }

        """
        6. Create Lambda for list all sagemaker endpoint  for front-end
        """
        function_name = 'endpoint_list'

        _endpoint_list_role_policy = _iam.PolicyStatement(
            actions=[
                's3:AmazonS3FullAccess',
                'lambda:AWSLambdaBasicExecutionRole',
                'secretsmanager:SecretsManagerReadWrite'
            ],
            resources=['*']  # 可根据需求进行更改
        )
        endpoint_list_role = _iam.Role(
            self, 'endpoint_list_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        endpoint_list_role.add_to_policy(_data_load_role_policy)

        endpoint_list_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        endpoint_list_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerReadOnly")
        )


        endpoint_list_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=endpoint_list_role,
            #layers=[self.langchain_processor_qa_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=20
        )

        self.create_apigw_resource_method_for_endpoint_list(
            api=api,
            endpoint_list_function=endpoint_list_function
        )

        # Create Integration Options
        """
        Covering:
        1. Content Handling : Default passthrough, if not specify
        2. URL Path Parameters
        3. Credential Role
        """
        _s3_apigw_put_integration_options = apigw.IntegrationOptions(
            request_parameters=request_parameters_in_integration_options,
            credentials_role=_execution_role,
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        "method.response.header.Access-Control-Allow-Origin": "'*'",
                        "method.response.header.Access-Control-Allow-Methods": "'PUT,POST,OPTIONS'",
                    },
                    response_templates={
                        "application/json": ""

                    }
                )
            ]
        )

        s3_apigw_integration = apigw.AwsIntegration(
            service="s3",
            path="{bucket}/{prefix}/{sub_prefix}/{key}",
            region=os.getenv('region'),
            integration_http_method="PUT",
            options=_s3_apigw_put_integration_options
        )

        filename_resource.add_method(
            http_method='PUT',
            integration=s3_apigw_integration,
            request_parameters=request_parameters,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True,
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                    },
                )
            ]
        )

    def create_content_moderation_func(self):
        _api_url_suffix = "_cn" if 'cn-' in os.getenv('AWS_REGION', '') else ""
        content_moderation_api = self.node.try_get_context(f"content_moderation_api{_api_url_suffix}")
        # content_moderation_token = self.node.try_get_context("content_moderation_account_token_in_base64")
        content_moderation_result_table = self.node.try_get_context("content_moderation_result_table")

        _content_moderation_role_policy = _iam.PolicyStatement(
            actions=[
                'lambda:AWSLambdaBasicExecutionRole',
                'secretsmanager:GetSecretValue',
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
            ],
            resources=['*']
        )

        content_moderation_role = _iam.Role(
            self, 'content_moderation_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        content_moderation_role.add_to_policy(_content_moderation_role_policy)

        content_moderation_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        # add langchain processor for smart query and answer
        function_name_content_moderation = 'content_moderation'
        content_moderation_func = _lambda.Function(
            self, function_name_content_moderation,
            function_name=function_name_content_moderation,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=content_moderation_role,
            layers=[self.langchain_processor_qa_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name_content_moderation),
            handler='lambda_function' + '.lambda_handler',
            memory_size=256,
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=10
        )
        content_moderation_func.add_environment("content_moderation_api", content_moderation_api)

        return content_moderation_func

    def create_apigw_resource_method_for_knowledge_base_handler(self, api, **kwargs):
            knowledge_base_handler = api.root.add_resource('knowledge_base_handler')

            jobs = knowledge_base_handler.add_resource(
                        "jobs",
                        default_cors_preflight_options=apigw.CorsOptions(
                            allow_methods=['GET','POST'],
                            allow_origins=apigw.Cors.ALL_ORIGINS)
                    )
            jobs_id = jobs.add_resource(
                        "{id}",
                        default_cors_preflight_options=apigw.CorsOptions(
                            allow_methods=['PUT','DELETE','GET'],
                            allow_origins=apigw.Cors.ALL_ORIGINS)
                    )
            presignurl = knowledge_base_handler.add_resource(
                        "presignurl",
                        default_cors_preflight_options=apigw.CorsOptions(
                            allow_methods=['POST'],
                            allow_origins=apigw.Cors.ALL_ORIGINS)
                    )
            indices = knowledge_base_handler.add_resource(
                        "indices",
                        default_cors_preflight_options=apigw.CorsOptions(
                            allow_methods=['GET'],
                            allow_origins=apigw.Cors.ALL_ORIGINS)
                    )
            
            get_presignurl_function = kwargs.get('get_presignurl_function')
            create_job_function = kwargs.get('create_job_function')

            list_jobs_function = kwargs.get('list_jobs_function')
            get_indice_list_function = kwargs.get('get_indice_list_function')

            def create_api_integration(function,resource,method):

                sub_resource_integration = apigw.LambdaIntegration(
                    function,
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
                resource.add_method(
                    method,
                    sub_resource_integration,
                    method_responses=[
                        apigw.MethodResponse(
                            status_code="200",
                            response_parameters={
                                'method.response.header.Access-Control-Allow-Origin': True
                            }
                        )
                    ]
                )

            #POST knowledge_base_handler/jobs
            create_api_integration(create_job_function,jobs,"POST")  
            #GET  knowledge_base_handler/jobs
            create_api_integration(list_jobs_function,jobs,"GET")  

            #POST knowledge_base_handler/presignurl
            create_api_integration(get_presignurl_function,presignurl,"POST")
            #GET knowledge_base_handler/indices
            create_api_integration(get_indice_list_function,indices,"GET")

    def create_knowledge_base_handler(self, api, search_engine_key):

            REGION = os.getenv('AWS_REGION', '')
            EMBEDDING_ENDPOINT_NAME = "bedrock-titan-embed"
            SEARCH_ENGINE = "opensearch"
            PRIMARY_KEY = 'id'

            _knowledge_base_role_policy = _iam.PolicyStatement(
                actions=[
                    'sagemaker:InvokeEndpointAsync',
                    'sagemaker:InvokeEndpoint',
                    's3:AmazonS3FullAccess',
                    'lambda:AWSLambdaBasicExecutionRole',
                    'secretsmanager:GetSecretValue',
                    'bedrock:*',
                    'dynamodb:AmazonDynamoDBFullAccess',
                    'logs:*',
                    'glue:*'
                ],
                resources=['*']  # 可根据需求进行更改
            )

            knowledge_base_handler_role = _iam.Role(
                self, 'knowledge_base_handler_rolev2',
                assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
            )
            knowledge_base_handler_role.add_to_policy(_knowledge_base_role_policy)

            job_table = dynamodb.Table(
                self, "job table",
                partition_key=dynamodb.Attribute(
                    name="id",
                    type=dynamodb.AttributeType.STRING,
                ),
                removal_policy=RemovalPolicy.DESTROY,
                stream=dynamodb.StreamViewType.NEW_IMAGE
            )
        
            deployment = s3deploy.BucketDeployment(self, "extraPythonFiles",
                sources=[s3deploy.Source.asset("../lambda/knowledge_base_handler/job")],
                destination_key_prefix="glue_job_assets",
                destination_bucket=self.bucket
            )

            GlueS3Prefix = f"s3://{self.bucket.bucket_name}/glue_job_assets",

            knowledge_base_handler_glue_role = _iam.Role(
                self, 'knowledge_base_handler_rolev3',
                assumed_by=_iam.ServicePrincipal('glue.amazonaws.com')
            )
            knowledge_base_handler_glue_role.add_to_policy(_knowledge_base_role_policy)
            self.bucket.grant_read_write(knowledge_base_handler_glue_role)
            job_table.grant_full_access(knowledge_base_handler_glue_role)

            glue_job = glue.CfnJob(
                self, "MyGlueJob",
                name="my-glue-job",
                role=knowledge_base_handler_glue_role.role_name,
                execution_property = glue.CfnJob.ExecutionPropertyProperty(
                    max_concurrent_runs=5
                ),
                command=glue.CfnJob.JobCommandProperty(
                    name="pythonshell",
                    python_version="3.9",
                    script_location=f"s3://{self.bucket.bucket_name}/glue_job_assets/glue-job-script.py",
                ),
                default_arguments={
                    "--TempDir": f"s3://{self.bucket.bucket_name}/temporary",
                    "--extra-py-files": f"s3://{self.bucket.bucket_name}/glue_job_assets/smart_search_dataload.py,s3://{self.bucket.bucket_name}/glue_job_assets/bedrock.py,s3://{self.bucket.bucket_name}/glue_job_assets/chinese_text_splitter.py,s3://{self.bucket.bucket_name}/glue_job_assets/opensearch_vector_search.py",
                    "--additional-python-modules": "tiktoken,tqdm==4.65.0,boto3==1.28.72,langchain==0.0.325,opensearch-py==2.3.2,docx2txt==0.8,pypdf==3.16.4,numexpr==2.8.4",
                },
                glue_version="3.0",
                max_capacity=1.0,
                )
            
            self.bucket.grant_read_write(knowledge_base_handler_role)
            job_table.grant_full_access(knowledge_base_handler_role)

            function_name = 'createJob',
            create_job_function = _lambda.Function(
                self, 'createJob',
                function_name='createJob',
                runtime=_lambda.Runtime.PYTHON_3_9,
                role=knowledge_base_handler_role,
                layers=[self.langchain_processor_qa_layer],
                code=_lambda.Code.from_asset(f"../lambda/knowledge_base_handler/job"),
                handler='lambda_function' + '.lambda_handler',
                timeout=Duration.minutes(5),
                environment={
                    "EMBEDDING_ENDPOINT_NAME": EMBEDDING_ENDPOINT_NAME,
                    "BUCKET": self.bucket.bucket_name,
                    "HOST": search_engine_key,
                    "REGION": REGION,
                    "SEARCH_ENGINE": SEARCH_ENGINE,
                    "TABLE_NAME": job_table.table_name,
                    "PRIMARY_KEY": PRIMARY_KEY,
            }
            )

            function_name = 'listJobs',
            list_jobs_function = _lambda.Function(
                self, 'listJobs',
                function_name='listJobs',
                runtime=_lambda.Runtime.PYTHON_3_9,
                role=knowledge_base_handler_role,
                layers=[self.langchain_processor_qa_layer],
                code=_lambda.Code.from_asset(f"../lambda/knowledge_base_handler/crud"),
                handler='get-all' + '.handler',
                timeout=Duration.minutes(5),
                environment={
                    "EMBEDDING_ENDPOINT_NAME": EMBEDDING_ENDPOINT_NAME,
                    "BUCKET": self.bucket.bucket_name,
                    "HOST": search_engine_key,
                    "REGION": REGION,
                    "SEARCH_ENGINE": SEARCH_ENGINE,
                    "TABLE_NAME": job_table.table_name,
                    "PRIMARY_KEY": PRIMARY_KEY
            }
            )

            function_name = 'getPresignURL',
            get_presignurl_function = _lambda.Function(
                self, 'getPresignURL',
                function_name='getPresignURL',
                runtime=_lambda.Runtime.PYTHON_3_9,
                role=knowledge_base_handler_role,
                layers=[self.langchain_processor_qa_layer],
                code=_lambda.Code.from_asset(f"../lambda/knowledge_base_handler/s3action"),
                handler='get-presign-url' + '.handler',
                timeout=Duration.minutes(5),
                environment={
                    "EMBEDDING_ENDPOINT_NAME": EMBEDDING_ENDPOINT_NAME,
                    "BUCKET": self.bucket.bucket_name,
                    "HOST": search_engine_key,
                    "REGION": REGION,
                    "SEARCH_ENGINE": SEARCH_ENGINE,
                    "TABLE_NAME": job_table.table_name,
                    "PRIMARY_KEY": PRIMARY_KEY
            }
            )

            function_name = 'getIndexList',
            get_indice_list_function = _lambda.Function(
                self, 'getIndiceList',
                function_name='getIndiceList',
                runtime=_lambda.Runtime.PYTHON_3_9,
                role=knowledge_base_handler_role,
                layers=[self.langchain_processor_qa_layer],
                code=_lambda.Code.from_asset('../lambda/knowledge_base_handler/indices'),
                handler='lambda_function' + '.lambda_handler',
                timeout=Duration.minutes(5),
                reserved_concurrent_executions=20,
                environment={
                    "EMBEDDING_ENDPOINT_NAME": EMBEDDING_ENDPOINT_NAME,
                    "BUCKET": self.bucket.bucket_name,
                    "HOST": search_engine_key,
                    "REGION": REGION,
                    "SEARCH_ENGINE": SEARCH_ENGINE,
                    "TABLE_NAME": job_table.table_name,
                    "PRIMARY_KEY": PRIMARY_KEY
            }
            )

            self.create_apigw_resource_method_for_knowledge_base_handler(
                api=api,
                create_job_function=create_job_function,
                get_presignurl_function=get_presignurl_function,
                list_jobs_function=list_jobs_function,
                get_indice_list_function=get_indice_list_function,
            )
