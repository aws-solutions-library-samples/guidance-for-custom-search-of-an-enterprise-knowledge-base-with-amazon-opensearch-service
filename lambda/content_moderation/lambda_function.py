import boto3
import json
import requests
from collections import defaultdict
import os
from datetime import datetime
import base64
import uuid

http_method = 'GET'
content_moderation_api = os.environ.get('content_moderation_api')


def format_datetime(_datetime):
    return _datetime.strftime("%Y%m%d %H:%M:%S")


# Lambda execution starts here
def lambda_handler(event, context):
    # get context from event
    print(event)

    if "queryStringParameters" in event.keys():
        content = event['queryStringParameters']['content']
        cm_api_token = event['queryStringParameters']['token']
    else:
        content = event['content']
        cm_api_token = event['token']

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Return if API_TOKEN is empty, NOT use Content Moderation
    if cm_api_token is None:
        response['body'] = json.dumps({
            'msg': "No Content Moderation API found. Skip verification",
            'datetime': format_datetime(datetime.now())
        })

        print(response)
        return response

    payload = {
        'token': cm_api_token,
        'context': content,
        'context_type': 'chat',
        'data_id': str(uuid.uuid4()),
    }

    res = requests.post(content_moderation_api, json=payload)

    """
    body: {
        "suggestion": xxx,
        "label": xxxx
    }
    """
    if "queryStringParameters" in event.keys():
        response['body'] = json.dumps(res.json()['data'])
        print(response)
    else:
        response['body'] = res.json()['data']
        print(response)

    return response
