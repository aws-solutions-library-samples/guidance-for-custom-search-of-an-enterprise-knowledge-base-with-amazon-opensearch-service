from constructs import Construct
from aws_cdk import (
    Stack,
    # aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_apigateway as apigw,
    RemovalPolicy
)
import os


class ServerlessBackendApiGWStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Now hardcode for testing first
        ACCOUNT = os.getenv('AWS_ACCOUNT_ID', '')
        REGION = os.getenv('AWS_REGION', '')
        bucket_for_uploaded_files = "intelligent-search-data-bucket" + "-" + ACCOUNT + "-" + REGION
        execution_role_name = "custom-role-document-ai-upload-to-s3-vc-test"
        apigateway_name = "intelligent-search-file-management"

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

        """
        2. Create Execution Role for Uploading file to S3
        IAM RoleName: custom-role-document-ai-upload-to-s3
        """
        _role_name = execution_role_name
        _inline_policies = {
            "AllowS3UploadPermission": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "s3:PutObject",
                        ],
                        resources=[f"arn:aws:s3:::{_bucket_name}/*"]),
                ]
            ),
            "AllowLogCreation": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
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

        _execution_role = iam.Role(self,
                                   id=_role_name,
                                   role_name=_role_name,
                                   assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
                                   description="Execution role for uploading file from APIGW to S3 directly.",
                                   inline_policies=_inline_policies
                                   )

        """
        3. Create Lambda for processing file and save to ES
        """

        """
        4. Update S3 file notification with Lambda
          prefix is {BUCKET_NAME}/source_data/
        """
        # _bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED,
        #     s3n.LambdaDestination(my_lambda),
        #     prefix=f"{_bucket_name}/source_data/*")

        """
        5. Create S3-based API Gateway
        """
        binary_media_types = ["application/pdf", "multipart/form-data"]

        s3_apigw = apigw.RestApi(self, "FileManagement",
                                 rest_api_name=apigateway_name,
                                 #  default_cors_preflight_options = apigw.CorsOptions(
                                 #      allow_origins = apigw.Cors.ALL_ORIGINS,
                                 #      allow_methods = apigw.Cors.ALL_METHODS
                                 # ),
                                 endpoint_types=[apigw.EndpointType.REGIONAL]
                                 )

        # Create Resources in below structure
        # /{bucket}/{prefix}/{filename}
        bucket_resource = s3_apigw.root.add_resource(path_part="{bucket}")
        prefix_resource = bucket_resource.add_resource(path_part="{prefix}")
        filename_resource = prefix_resource.add_resource(
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
            "method.request.path.prefix": True  # True if param is mandatory
        }

        request_parameters_in_integration_options = {
            "integration.request.path.bucket": "method.request.path.bucket",
            "integration.request.path.key": "method.request.path.filename",
            "integration.request.path.prefix": "method.request.path.prefix"
        }

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
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                    response_templates = {
                        "application/json": ""
                    }
                )
            ]
        )

        s3_apigw_integration = apigw.AwsIntegration(
            service="s3",
            path="{bucket}/{prefix}/{key}",
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
                    },
                )
            ]
        )
