import os
import sys
import json

import boto3
import botocore

from bedrockAdapter import BedrockAdapter

boto3_bedrock = boto3.client(
    service_name="bedrock-runtime", region_name=os.environ.get("AWS_REGION")
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
    
    provider = modelId.split(".")[0]
    params = {"max_tokens": max_tokens,"temperature": temperature}
    params["modelId"] = modelId
    input_body = BedrockAdapter.prepare_input(provider, prompt, params)
    body = json.dumps(input_body)
        
    accept = "application/json"
    if modelId == 'meta.llama2-13b-chat-v1':
        accept = "*/*"
    contentType = "application/json"

    result = boto3_bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    result_body = json.loads(result.get("body").read())
    print('result_body:',result_body)
    
    answer = ''
    embedding = []
    if modelId.find('claude-3') >=0:
        answer = result_body.get("content")[0].get("text")
    elif modelId.find('claude') >=0:
        answer = result_body.get("completion")
    elif modelId.find('llama') >=0:
        answer = result_body.get("generation")
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
    
    if modelId.find('claude') >=0 or modelId.find('llama') >=0 or modelId == 'amazon.titan-tg1-large': 
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