#!/usr/bin/env python3
import os
import aws_cdk as cdk
from lib.ss_vpcstack import VpcStack
from lib.ss_lambdastack import LambdaStack
from lib.ss_lambdavpcstack import LambdaVPCStack
from lib.ss_osstack import OpenSearchStack
from lib.ss_osvpcstack import OpenSearchVPCStack
from lib.ss_notebook import NotebookStack
from lib.ss_botstack import BotStack
from lib.ss_kendrastack import KendraStack
from lib.ss_bedrockstack import BedrockStack

ACCOUNT = os.getenv('AWS_ACCOUNT_ID', '')
REGION = os.getenv('AWS_REGION', '')
AWS_ENV = cdk.Environment(account=ACCOUNT, region=REGION)
env = AWS_ENV
print(env)
app = cdk.App()
if app.node.try_get_context('vpc_deployment'):
    vpcstack = VpcStack(app, 'VpcStack',env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
    searchstack = OpenSearchVPCStack(app, "OpenSearchVPCStack",vpc=vpcstack.vpc, env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
    searchstack.add_dependency(vpcstack)
    search_engine_key = searchstack.search_domain_endpoint
    lambdastack = LambdaVPCStack(app, "LambdaVPCStack", search_engine_key,vpc=vpcstack.vpc, env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
    lambdastack.add_dependency(searchstack)
    bedrockstack = BedrockStack( app, "BedrockStack", env=env)
else:
    if app.node.try_get_context('search_engine_opensearch'):
        searchstack = OpenSearchStack(app, "OpenSearchStack", env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
        search_engine_key = searchstack.search_domain_endpoint
    else:
        searchstack = KendraStack(app, "KendraStack", env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
        search_engine_key = searchstack.kendra_index_id        
    lambdastack = LambdaStack(app, "LambdaStack", search_engine_key=search_engine_key, env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
    lambdastack.add_dependency(searchstack)
    bedrockstack = BedrockStack( app, "BedrockStack", env=env)
notebookstack = NotebookStack(app, "NotebookStack", search_engine_key=search_engine_key, env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
notebookstack.add_dependency(searchstack)

  
if('bot' in app.node.try_get_context("extension")):   
    botstack = BotStack(app, "BotStack", env=env, description="Guidance for Custom Search of an Enterprise Knowledge Base on AWS - (SO9251)")
    botstack.add_dependency(lambdastack)


app.synth()
