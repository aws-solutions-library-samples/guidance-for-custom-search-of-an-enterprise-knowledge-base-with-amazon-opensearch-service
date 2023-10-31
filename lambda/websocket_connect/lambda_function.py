import json
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
connections = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    logger.debug("onconnect: %s" % event)

    connectionId = event.get('requestContext',{}).get('connectionId')
    if connectionId is None:
        return { 'statusCode': 400, 
                 'body': 'bad request' }

    result = connections.put_item(Item={ 'id': connectionId})
    if result.get('ResponseMetadata',{}).get('HTTPStatusCode') != 200:
        return { 'statusCode': 500,
                 'body': 'something went wrong' }
    return { 'statusCode': 200,
             'body': connectionId }