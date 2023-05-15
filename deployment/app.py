#!/usr/bin/env python3
import os
import aws_cdk as cdk
# from lib.ss_stdstack import SmartSearchStack
from lib.ss_lambdastack import LambdaStack
from lib.ss_osstack import OpenSearchStack
from lib.ss_notebook import NotebookStack
from lib.ss_file_upload_apigw import ServerlessBackendApiGWStack

ACCOUNT = os.getenv('AWS_ACCOUNT_ID', '')
REGION = os.getenv('AWS_REGION', '')
AWS_ENV = cdk.Environment(account=ACCOUNT, region=REGION)
env=AWS_ENV
print(env)
app = cdk.App()
opsstack = OpenSearchStack(app, "OpenSearchStack", env=env)
lambdastack = LambdaStack(app, "LambdaStack",ops_endpoint=opsstack.search_domain_endpoint, env=env)
lambdastack.add_dependency(opsstack)
notebookstack = NotebookStack(app, "NotebookStack",ops_endpoint=opsstack.search_domain_endpoint, env=env)
notebookstack.add_dependency(opsstack)

# SmartSearchStack(app, "smartsearch")

apigwstack = ServerlessBackendApiGWStack( app, "APIGw", env=env)

app.synth()
