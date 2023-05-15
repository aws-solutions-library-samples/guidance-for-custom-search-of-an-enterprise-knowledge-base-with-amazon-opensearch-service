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
    aws_events as events,
    aws_events_targets as target,
    aws_sqs as sqs,
    aws_lambda_event_sources as source,
    aws_iam as _iam,
    ContextProvider
)

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str , ops_endpoint: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



# get value from opensearch stack       
        host =  "https://"+ops_endpoint+"/"
#get CloudFormation parameter
                            

        func_selection = self.node.try_get_context("selection")

        print("These functions are slected( configuration is in cdk.json context 'selection'):  ",func_selection)
        # role and policy (smartsearch knn doc,opensearch-search-knn,knn_faq),all three function using same policy.
        if('knn' in func_selection or 'knn_faq'in func_selection or 'doc' in func_selection):
            knn_policy_statement = _iam.PolicyStatement(
                actions=[
                    'sagemaker:InvokeEndpointAsync',
                    'sagemaker:InvokeEndpoint',
                    'es:ESHttpPost' ,
                    'secretsmanager:GetSecretValue' ,
                    ],
                resources=['*'] # 可根据需求进行更改
            )
            knn_lambda_role = _iam.Role(
                self, 'knn_lambda_role_Role',
                assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
            )
            knn_lambda_role.add_to_policy(knn_policy_statement)
            

        # role and policy (insert feedback)
        if('feedback' in func_selection):
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
        if('post_selection' in func_selection):
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
        if('xgb_train' in func_selection):
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

#api gateway resource
        api = apigw.RestApi( self,'opensearch-api', 
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            ),
            endpoint_types=[apigw.EndpointType.REGIONAL]
        )
        
#define lambda function, knn role is not defined by guideline
        if( 'knn' in func_selection):
            self.opensearch_search_knn_lambda = self.define_lambda_function('opensearch-search-knn',knn_lambda_role)
            self.opensearch_search_knn_lambda.add_environment("host",host)
            # search_knn_resource
            search_knn_resource = api.root.add_resource(
                    'search_knn',            
                    default_cors_preflight_options= apigw.CorsOptions(
                    allow_methods=['GET', 'OPTIONS'],
                    allow_origins= apigw.Cors.ALL_ORIGINS)
            )
            search_knn_integration = apigw.LambdaIntegration(
                    self.opensearch_search_knn_lambda,
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

            user_model = api.add_model("UserModel",
                schema=apigw.JsonSchema(
                    type=apigw.JsonSchemaType.OBJECT,
                    properties={
                        "ind": apigw.JsonSchema(
                            type=apigw.JsonSchemaType.STRING
                        ),
                        "knn": apigw.JsonSchema(
                            type=apigw.JsonSchemaType.STRING
                        ),
                        "ml": apigw.JsonSchema(
                            type=apigw.JsonSchemaType.STRING
                        ),
                        "q": apigw.JsonSchema(
                            type=apigw.JsonSchemaType.STRING
                        )                   
                    },
                    required=["ind","knn","q"]
                )
            )

            search_knn_resource.add_method(
                'GET', 
                search_knn_integration,
                request_models={
                "application/json": user_model
                },
                method_responses=[
                    apigw.MethodResponse(
                        status_code="200",
                        response_parameters={
                            'method.response.header.Access-Control-Allow-Origin': True
                        }
                    )
                ]
            )
        if('knn_faq' in func_selection):
            self.opensearch_search_knn_faq_lambda = self.define_lambda_function('opensearch-search-knn-faq',knn_lambda_role)
            self.opensearch_search_knn_faq_lambda.add_environment("host",host)
            # search_knn_faq_resource
            search_faq_resource = api.root.add_resource(
                    'search_faq',            
                    default_cors_preflight_options= apigw.CorsOptions(
                    allow_methods=['GET', 'OPTIONS'],
                    allow_origins= apigw.Cors.ALL_ORIGINS)
            )

            search_faq_integration = apigw.LambdaIntegration(
                    self.opensearch_search_knn_faq_lambda,
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

            search_faq_resource.add_method(
                'GET', 
                search_faq_integration,
                request_models={
                "application/json": user_model
                },
                method_responses=[
                    apigw.MethodResponse(
                        status_code="200",
                        response_parameters={
                            'method.response.header.Access-Control-Allow-Origin': True
                        }
                    )
                ]
            )
            
        if('feedback' in func_selection):
            self.opensearch_lambda_insert_feedback_lambda = self.define_lambda_function('opensearch-lambda-insert_feedback',fb_lambda_role)
        if('post_selection' in func_selection):
            self.opensearch_lambda_post_selection_lambda = self.define_lambda_function('opensearch-lambda-post_selection',ps_lambda_role)
        if('xgb_train' in func_selection):
            self.open_search_xgb_train_deploy_lambda = self.define_lambda_function('open-search_xgb_train_deploy',xgb_lambda_role)
        if('knn_doc' in func_selection):
            self.opensearch_search_knn_doc_lambda = self.define_lambda_function('opensearch-search-knn-doc',knn_lambda_role,timeout= 60)
            self.opensearch_search_knn_doc_lambda.add_environment("host",host)
            # search_knn_doc_resource
            search_knn_doc_resource = api.root.add_resource(
                    'search_knn_doc',            
                    default_cors_preflight_options= apigw.CorsOptions(
                    allow_methods=['GET', 'OPTIONS'],
                    allow_origins= apigw.Cors.ALL_ORIGINS)
            )

            search_knn_doc_integration = apigw.LambdaIntegration(
                    self.opensearch_search_knn_doc_lambda,
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

            search_knn_doc_resource.add_method(
                'GET', 
                search_knn_doc_integration,
                method_responses=[
                    apigw.MethodResponse(
                        status_code="200",
                        response_parameters={
                            'method.response.header.Access-Control-Allow-Origin': True
                        }
                    )
                ]
            )






    def define_lambda_function(self, function_name,role,timeout = 10 ):
        lambda_function = _lambda.Function(
            self, function_name,
            function_name = function_name,
            runtime = _lambda.Runtime.PYTHON_3_9,
            role = role,
            code = _lambda.Code.from_asset('../lambda/'+function_name),
            handler = 'lambda_function' + '.lambda_handler',
            timeout = Duration.seconds(timeout),
            reserved_concurrent_executions=100
        )
        return lambda_function
    
    



                    

