from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    RemovalPolicy,
    Duration
)
import os

class BedrockStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # configure the lambda role
        _bedrock_role_policy = iam.PolicyStatement(
            actions=["bedrock:*"],
            resources=['*']
        )
        
        bedrock_role = iam.Role(
            self, 'bedrock_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        bedrock_role.add_to_policy(_bedrock_role_policy)

        bedrock_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        
        bedrock_layer = _lambda.LayerVersion(
          self, 'BedrockLayer',
          code=_lambda.Code.from_asset('../lambda/langchain_processor_layer'),
          compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
          description='Bedrock Library'
        )
        
        function_name = 'bedrock_invoke'
        bedrock_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=bedrock_role,
            layers=[bedrock_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            memory_size=256,
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=50
        )
        
        bedrock_api = apigw.RestApi(self, 'bedrock-invoke-api',
                               default_cors_preflight_options=apigw.CorsOptions(
                                   allow_origins=apigw.Cors.ALL_ORIGINS,
                                   allow_methods=apigw.Cors.ALL_METHODS
                               ),
                               endpoint_types=[apigw.EndpointType.REGIONAL]
                               )

        bedrock_resource = bedrock_api.root.add_resource(
            'bedrock',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        bedrock_integration = apigw.LambdaIntegration(
            bedrock_function,
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

        bedrock_resource.add_method(
            'GET',
            bedrock_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )