import json
import os
import sys
import logging

sys.path.insert(0, F"{os.environ['LAMBDA_TASK_ROOT']}/{os.environ['DIR_NAME']}")
import boto3
import botocore

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

lam = boto3.client('lambda')

def lambda_handler(event, context):
    logger.debug("sendmessage: %s" % event)
    evt_body = json.loads(event.get('body', '{}'))
    # _function_name = evt_body['process_function_name']
    _function_name = 'langchain_processor_qa'
    try:
        lam.invoke(
            FunctionName=_function_name,
            InvocationType="Event",
            Payload=json.dumps(event)
        )
        return {
            "statusCode": 200,

        }
    except Exception as e:
        print(e)

    

