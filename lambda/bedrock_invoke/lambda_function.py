import os
import sys
import json

import boto3
import botocore

# module_path = ".."
# sys.path.append(os.path.abspath(module_path))
from utils import bedrock

if('BEDROCK_ASSUME_ROLE' in os.environ):
    boto3_bedrock = bedrock.get_bedrock_client(
        assumed_role=os.environ.get('BEDROCK_ASSUME_ROLE', None),
        region=os.environ.get("AWS_REGION", None)
    )
else:
    boto3_bedrock = bedrock.get_bedrock_client(
        region=os.environ.get("AWS_REGION", None)
    )


def lambda_handler(event, context):
    
    print("event:",event)
    print("boto3_bedrock:",boto3_bedrock)
    prompt_data = """hello"""
    
    prompt=prompt_data
    if "prompt" in event['queryStringParameters'].keys():
        prompt = event['queryStringParameters']['prompt']
    print('prompt:',prompt)
    
    max_tokens=512
    if "max_tokens" in event['queryStringParameters'].keys():
        max_tokens = int(event['queryStringParameters']['max_tokens'])
    print('max_tokens:',max_tokens)
        
    modelId = 'anthropic.claude-v2'
    if "modelId" in event['queryStringParameters'].keys():
        modelId = event['queryStringParameters']['modelId']
    print('modelId:',modelId)
        
    temperature=0.01
    if "temperature" in event['queryStringParameters'].keys():
        temperature = float(event['queryStringParameters']['temperature'])
    print('temperature:',temperature)
    
    
    if modelId.find('claude') >=0:
        body = json.dumps({"prompt": prompt, "max_tokens_to_sample": max_tokens,"temperature": temperature})
    elif modelId == 'amazon.titan-tg1-large':
        body = json.dumps({"inputText": prompt,  
        "textGenerationConfig" : { 
                "maxTokenCount": max_tokens,
                "stopSequences": [],
                "temperature":temperature,
                "topP":0.9
            }
        })
    elif modelId == 'amazon.titan-e1t-medium':
        body = json.dumps({"inputText": prompt})
        
    accept = "application/json"
    contentType = "application/json"
    result = boto3_bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    result_body = json.loads(result.get("body").read())
    print('result_body:',result_body)
    
    answer = ''
    embedding = []
    if modelId.find('claude') >=0:
        answer = result_body.get("completion")
    elif modelId == 'amazon.titan-tg1-large':
        answer = result_body.get("results")[0].get("outputText")
    elif modelId == 'amazon.titan-e1t-medium' or modelId.find('amazon.titan-embed')>=0:
        embedding =result_body.get("embedding")
    print('answer:',answer)
    print('embedding:',embedding)
    
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    
    if modelId.find('claude') >=0 or modelId == 'amazon.titan-tg1-large': 
        response['body'] = json.dumps(
                    {
                        'answer':answer,
                    })
    elif modelId == 'amazon.titan-e1t-medium' or modelId.find('amazon.titan-embed')>=0:
        response['body'] = json.dumps(
                {
                    'embedding':embedding,
                })      
    
    return response