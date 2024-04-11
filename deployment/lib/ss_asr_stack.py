from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sagemaker,
    CfnOutput,
    Duration,
    Fn
)
from constructs import Construct

import os
import boto3
import sagemaker
from sagemaker.jumpstart.model import JumpStartModel
# from sagemaker.jumpstart.utils import get_jumpstart_content_bucket
# from .sagemaker_endpoint_construct import SagemakerEndpointConstruct
from sagemaker import script_uris
from sagemaker import image_uris 
from sagemaker import model_uris

class ASRStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        account_id = os.getenv('AWS_ACCOUNT_ID', '')
        region_name= os.getenv('AWS_REGION','')
        asr_lambda_arn= "arn:aws:lambda:{}:{}:function:asr_processing_job".format(region_name,account_id)

        #Set role and policy for asr code hook lambda function
        asr_lambda_policy_statement = iam.PolicyStatement(
            actions=[
                'lambda:InvokeFunctionUrl' ,
                'lambda:InvokeFunction',
                'lambda:InvokeAsync',
                'lambda:AWSLambdaBasicExecutionRole',
                'logs:*',
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'polly:SynthesizeSpeech'
                ],
            resources=['*'] # Customize it according to your use case
        )
        
        asr_lambda_role = iam.Role(
            self, 'asr_lambda_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        asr_lambda_role.add_to_policy(asr_lambda_policy_statement)
   
        #define lambda function
        asr_lambda = self.define_lambda_function('asr_processing_job',asr_lambda_role,timeout= 60)
        asr_endpoint_name = self.node.try_get_context("asr_endpoint_name")
        # asr_lambda.add_environment("asr_endpoint_name", asr_endpoint_name)
        #get asr endpoint name value from cdk.json

        # api gateway resource
        api = apigw.RestApi(self, 'asr-processing-api',
                            endpoint_types=[apigw.EndpointType.REGIONAL],
                            )
        #add api gateway data mapping in request body method request
        # api_data_mapping = apigw.IntegrationRequestParameterMapping()
        # api_data_mapping.put_method_request_parameter('Content-Type', 'method.request.header.Content-Type')
        self.create_apigw_resource_method_for_asr_lambda(
            api=api,
            asr_processing_job_function=asr_lambda
        )

        role = iam.Role(self, "SageMaker-Policy", assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        
        sts_policy = iam.Policy(self, "sm-deploy-policy-sts",
                                    statements=[iam.PolicyStatement(
                                        effect=iam.Effect.ALLOW,
                                        actions=[
                                            "sts:AssumeRole",
                                            "s3:*"
                                          ],
                                        resources=["*"]
                                    )]
                                )

        logs_policy = iam.Policy(self, "sm-deploy-policy-logs",
                                    statements=[iam.PolicyStatement(
                                        effect=iam.Effect.ALLOW,
                                        actions=[
                                            "cloudwatch:PutMetricData",
                                            "logs:CreateLogStream",
                                            "logs:PutLogEvents",
                                            "logs:CreateLogGroup",
                                            "logs:DescribeLogStreams",
                                            "ecr:GetAuthorizationToken"
                                          ],
                                        resources=["*"]
                                    )]
                                )
        
        ecr_policy = iam.Policy(self, "sm-deploy-policy-ecr",
                                    statements=[iam.PolicyStatement(
                                        effect=iam.Effect.ALLOW,
                                        actions=[
                                            "ecr:*",
                                          ],
                                        resources=["*"]
                                    )]
                                )
        # model_data_bucket_policy = iam.PolicyStatement(
        # actions=["s3:GetObject", "s3:ListBucket"],
        # resources=[
        #     f"arn:aws:s3:::jumpstart-cache-prod-us-east-1",
        #     f"arn:aws:s3:::jumpstart-cache-prod-us-east-1/huggingface-infer/prepack/v1.0.1/infer-prepack-huggingface-asr-whisper-large-v2.tar.gz"
        # ]
        # )

                                
        role.attach_inline_policy(sts_policy)
        role.attach_inline_policy(logs_policy)
        role.attach_inline_policy(ecr_policy)
        # role.add_to_principal_policy(model_data_bucket_policy)
      
        MODEL_ID = "huggingface-asr-whisper-large-v2"
        INFERENCE_INSTANCE_TYPE = "ml.g5.2xlarge" 
        MODEL_TASK_TYPE = "asr"
        model_info = self.get_sagemaker_uris(model_task_type=MODEL_TASK_TYPE,
                                            instance_type=INFERENCE_INSTANCE_TYPE,
                                            region_name=region_name,
                                            model_id=MODEL_ID)
        print(model_info) 
        # self.createEndpointASR(role = sagemaker_role,model_id=asr_endpoint_name)
        endpoint =  SageMakerEndpointConstruct(self, "ASR",
                                    project_prefix = "smart-search",
                                    
                                    role_arn= role.role_arn,

                                    model_name = "huggingface-asr-whisper-large-v2",
                                    model_bucket_name = model_info["model_bucket_name"],
                                    model_bucket_key = model_info["model_bucket_key"],
                                    model_docker_image = model_info["model_docker_image"],

                                    variant_name = "AllTraffic",
                                    variant_weight = 1,
                                    instance_count = 1,
                                    instance_type = model_info["instance_type"],

                                    environment = {
                                        "MMS_MAX_RESPONSE_SIZE": "20000000",
                                        "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
                                        "SAGEMAKER_PROGRAM": "inference.py",
                                        "SAGEMAKER_REGION": model_info["region_name"],
                                        "SAGEMAKER_SUBMIT_DIRECTORY": "/opt/ml/model/code",
                                    },

                                    deploy_enable = True
        )
        endpoint.node.add_dependency(sts_policy)
        endpoint.node.add_dependency(logs_policy)
        endpoint.node.add_dependency(ecr_policy)
        endpoint.node.add_dependency(role)
        # upload enpoint to aws lambda environment variable
        endpoint_name = endpoint.endpoint_name
        asr_lambda.add_environment("asr_endpoint_name", endpoint_name)

    # def createEndpointASR(self,role,model_id ='huggingface-asr-whisper-large-v2',):
    #     #Param: model_id can be "huggingface-asr-whisper-large-v2","huggingface-asr-whisper-large","huggingface-asr-whisper-base","huggingface-asr-whisper-medium",,"huggingface-asr-whisper-small","huggingface-asr-whisper-tiny"
    #     #account_id = boto3.client('sts').get_caller_identity().get('Account')
    #     #region_name = boto3.session.Session().region_name
    #     # role_arn = role.role_arn  # Get the IAM role ARN as a string
    #     model = JumpStartModel(model_id=model_id,
    #                            role=role_arn )
    #     predictor = model.deploy(instance_type='ml.g5.2xlarge',
    #                              endpoint_name = model_id
    #                               )



    def define_lambda_function(self, function_name,role,timeout = 10 ):
        lambda_function = _lambda.Function(
            self, function_name,
            function_name = function_name,
            runtime = _lambda.Runtime.PYTHON_3_9,
            role = role,
            code = _lambda.Code.from_asset('../lambda/'+function_name),
            handler = 'lambda_function' + '.lambda_handler',
            timeout = Duration.seconds(timeout),
            reserved_concurrent_executions=20
        )
        return lambda_function

    def create_apigw_resource_method_for_asr_lambda(self, api, asr_processing_job_function):

        asr_processing_job_resource = api.root.add_resource(
            'asr_processing_job',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['POST', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        asr_processing_job_integration = apigw.LambdaIntegration(
            asr_processing_job_function,
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

        asr_processing_job_resource.add_method(
            'POST',
            asr_processing_job_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
    def get_sagemaker_uris(self, model_task_type, instance_type, region_name, model_id):
    
        FILTER = f"task == {model_task_type}"
        #txt2img_models = list_jumpstart_models(filter=FILTER)
        
        MODEL_VERSION = "*"  # latest
        SCOPE = "inference"

        inference_image_uri = image_uris.retrieve(region=region_name, 
                                            framework=None,
                                            model_id=model_id, 
                                            model_version=MODEL_VERSION, 
                                            image_scope=SCOPE, 
                                            instance_type=instance_type)
        
        inference_model_uri = model_uris.retrieve(region=region_name, 
                                            model_id=model_id, 
                                            model_version=MODEL_VERSION, 
                                            model_scope=SCOPE)
        
        inference_source_uri = script_uris.retrieve(region=region_name, 
                                                model_id=model_id, 
                                                model_version=MODEL_VERSION, 
                                                script_scope=SCOPE)

        model_bucket_name = inference_model_uri.split("/")[2]
        model_bucket_key = "/".join(inference_model_uri.split("/")[3:])
        model_docker_image = inference_image_uri

        return {"model_bucket_name":model_bucket_name, "model_bucket_key": model_bucket_key, \
                "model_docker_image":model_docker_image, "instance_type":instance_type, \
                    "inference_source_uri":inference_source_uri, "region_name":region_name}
    



class SageMakerEndpointConstruct(Construct):

    def __init__(self, scope: Construct, construct_id: str, 
        project_prefix: str,
        role_arn: str,
        model_name: str,
        model_bucket_name: str,
        model_bucket_key: str,
        model_docker_image: str,
        variant_name: str,
        variant_weight: int,
        instance_count: int,
        instance_type: str,
        environment: dict,
        deploy_enable: bool) -> None:
        super().__init__(scope, construct_id)
        
        model = aws_sagemaker.CfnModel(self, f"{model_name}-Model",
                           execution_role_arn= role_arn,
                           containers=[
                               aws_sagemaker.CfnModel.ContainerDefinitionProperty(
                                        image= model_docker_image,
                                        model_data_url= f"s3://{model_bucket_name}/{model_bucket_key}",
                                        environment= environment
                                    )
                               ],
                           model_name= f"{project_prefix}-{model_name}-Model"
        )
        
        config = aws_sagemaker.CfnEndpointConfig(self, f"{model_name}-Config",
                            endpoint_config_name= f"{project_prefix}-{model_name}-Config",
                            production_variants=[
                                aws_sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                                    model_name= model.attr_model_name,
                                    variant_name= variant_name,
                                    initial_variant_weight= variant_weight,
                                    initial_instance_count= instance_count,
                                    instance_type= instance_type
                                )
                            ]
        )
        
        self.deploy_enable = deploy_enable
        if deploy_enable:
            self.endpoint = aws_sagemaker.CfnEndpoint(self, f"{model_name}-Endpoint",
                                endpoint_name= f"{project_prefix}-{model_name}-Endpoint",
                                endpoint_config_name= config.attr_endpoint_config_name
            )
            
            CfnOutput(scope=self,id=f"{model_name}EndpointName", value=self.endpoint.endpoint_name)
            
            
    @property
    def endpoint_name(self) -> str:
        return self.endpoint.attr_endpoint_name if self.deploy_enable else "not_yet_deployed"