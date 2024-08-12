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
    print('event:',event)
        

    _function_name = 'multi_modal_qa'
    
    if 'body' in event.keys():
        body = json.loads(event['body'])
        if 'workMode' in body.keys():
            if body['workMode'] == 'text':
                _function_name = 'text_qa'
    
    print('_function_name:',_function_name)      
    
    
    
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

    

