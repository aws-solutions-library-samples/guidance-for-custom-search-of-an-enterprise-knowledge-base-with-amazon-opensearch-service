from pyclbr import Function
import json
import os
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnParameter,
    Aws,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as _iam,
    aws_lex as lex,
    aws_logs as logs,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    RemovalPolicy
    )
# from cdk_utils import define_lambda_function

#Global const value
BOT_NAME = 'llmbot'
DATA_PRIVACY = {'ChildDirected': False}
SENTIMENT_ANALYSYS_SETTINGS = {'DetectSentiment': False}
IDLE_SESION_TIMEOUT_IN_SECONDS = 300

class BotStack(Stack):

    def __init__(self, scope: Construct, construct_id: str , **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #Get configuration
        data_privacy = DATA_PRIVACY
        sentiment_analysis_settings = SENTIMENT_ANALYSYS_SETTINGS
        idle_session_ttl_in_seconds = IDLE_SESION_TIMEOUT_IN_SECONDS
        account_id = os.getenv('AWS_ACCOUNT_ID', '')
        region_name= os.getenv('AWS_REGION','')
        bot_lambda_arn= "arn:aws:lambda:{}:{}:function:langchain_processor_qa".format(region_name,account_id)
        log_group  = logs.LogGroup(self, "Log Group", removal_policy=RemovalPolicy.DESTROY)
        s3_bots  = S3BotFiles(self, 's3bots')

        #Set role and policy for lex v2 code hook lambda function
        bot_lambda_policy_statement = _iam.PolicyStatement(
            actions=[
                'lambda:InvokeFunctionUrl' ,
                'lambda:InvokeFunction',
                'lambda:InvokeAsync',
                'polly:SynthesizeSpeech'
                ],
            resources=['*'] # Customize it according to your use case
        )
        bot_lambda_role = _iam.Role(
            self, 'bot_lambda_role',
            assumed_by=_iam.ServicePrincipal('lambda.amazonaws.com')
        )
        bot_lambda_role.add_to_policy(bot_lambda_policy_statement)
        #define Lex V2 role
        bot_lexv2_policy_statement = _iam.PolicyStatement(
            actions=[
                'lexv2:*' ,
                's3:AmazonS3FullAccess',
                ],
            resources=['*'] # Customize it according to your use case
        )
        bot_lexv2_role = _iam.Role(
            self, 'bot_lexv2_role',
            assumed_by=_iam.ServicePrincipal('lexv2.amazonaws.com')
        )
        bot_lexv2_role.add_to_policy(bot_lexv2_policy_statement)

    
        #define lambda function, knn role is not defined by guideline
        self.ai_bot_qa_lambda = self.define_lambda_function('llm_bot_qa',bot_lambda_role,timeout= 60)

        #define Lex configuration
        code_hook_specification=lex.CfnBot.CodeHookSpecificationProperty(
            lambda_code_hook=lex.CfnBot.LambdaCodeHookProperty(
                code_hook_interface_version="1.0",
                lambda_arn=self.ai_bot_qa_lambda.function_arn
            )
        )

        bot_alias_locale_setting=lex.CfnBot.BotAliasLocaleSettingsProperty(
            enabled=True, code_hook_specification=code_hook_specification
        )

        conversation_log_settings=lex.CfnBot.ConversationLogSettingsProperty(
            audio_log_settings=[lex.CfnBot.AudioLogSettingProperty(
                destination=lex.CfnBot.AudioLogDestinationProperty(
                    s3_bucket=lex.CfnBot.S3BucketLogDestinationProperty(
                        log_prefix=f"{BOT_NAME}/audios",
                        s3_bucket_arn=s3_bots.bucket.bucket_arn,
                    )
                ),
                enabled=True
            )],
            text_log_settings=[lex.CfnBot.TextLogSettingProperty(
                destination=lex.CfnBot.TextLogDestinationProperty(
                    cloud_watch=lex.CfnBot.CloudWatchLogGroupLogDestinationProperty(
                        cloud_watch_log_group_arn=log_group.log_group_arn,
                        log_prefix=f"{BOT_NAME}/text"
                    )
                ),
                enabled=True
            )]
        )
#get  bot_lexv2_role arn
                    
        cfn_bot = lex.CfnBot(self, "CfnBot",
            data_privacy = data_privacy,
            idle_session_ttl_in_seconds = idle_session_ttl_in_seconds,
            name=BOT_NAME,
            role_arn=bot_lexv2_role.role_arn,
            bot_file_s3_location=lex.CfnBot.S3LocationProperty(
                s3_bucket=s3_bots.s3deploy.deployed_bucket.bucket_name,
                s3_object_key=s3_bots.key['llmbot']),
            auto_build_bot_locales=True,
            description=f"{BOT_NAME}-CDK Generation",
            test_bot_alias_settings=lex.CfnBot.TestBotAliasSettingsProperty(
                bot_alias_locale_settings=[lex.CfnBot.BotAliasLocaleSettingsItemProperty(
                    bot_alias_locale_setting= bot_alias_locale_setting, 
                    locale_id="zh_CN"                           # zh_CN = Mandarin Chinese
                )],
                conversation_log_settings = conversation_log_settings,
                sentiment_analysis_settings=SENTIMENT_ANALYSYS_SETTINGS
            )
        )

        self.ai_bot_qa_lambda.add_permission(
            principal=_iam.ServicePrincipal("lexv2.amazonaws.com"),id='bot-invoke',
            action='lambda:InvokeFunction', source_arn = f"arn:aws:lex:{Stack.of(self).region}:{Stack.of(self).account}:bot-alias/*"
            )
        
        cfn_bot.node.add_dependency(bot_lexv2_role)
        cfn_bot.node.add_dependency(s3_bots.s3deploy.deployed_bucket)
        
    def define_lambda_function(self, function_name,role,timeout = 10 ):
        lambda_function = _lambda.Function(
            self, function_name,
            function_name = function_name,
            runtime = _lambda.Runtime.PYTHON_3_9,
            role = role,
            code = _lambda.Code.from_asset('../lambda/'+function_name),
            handler = 'lambda_function' + '.lambda_handler',
            timeout = Duration.seconds(timeout),
            reserved_concurrent_executions=50
        )
        return lambda_function




class S3BotFiles(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.bucket = s3.Bucket(self, "b", removal_policy=RemovalPolicy.DESTROY, auto_delete_objects=True)
        self.s3deploy = s3deploy.BucketDeployment(self, "DeployLLMbot",
            sources=[s3deploy.Source.asset("../extension/bot")],
            destination_bucket=self.bucket,
            destination_key_prefix="bot"
        )
        self.key = {"llmbot": "bot/llmbot-lex.zip"}




 


    
    



                    

