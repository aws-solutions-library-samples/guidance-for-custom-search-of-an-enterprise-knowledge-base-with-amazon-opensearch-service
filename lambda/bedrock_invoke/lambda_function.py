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

    httpMethod = 'GET'
    if 'httpMethod' in event.keys():
        httpMethod = event['httpMethod']
    print('httpMethod:',httpMethod)
    
    evt_para = {}
    if httpMethod == 'GET':
        evt_para = json.loads(event['queryStringParameters'])
    elif httpMethod == 'POST':
        evt_para = json.loads(event['body'])

    prompt=''
    if "prompt" in evt_para.keys():
        prompt = evt_para['prompt']
    print('prompt:',prompt)
    
    max_tokens=4096
    if "max_tokens" in evt_para.keys():
        max_tokens = int(evt_para['max_tokens'])
    print('max_tokens:',max_tokens)
        
    modelId = 'anthropic.claude-v2'
    if "modelId" in evt_para.keys():
        modelId = evt_para['modelId']
    print('modelId:',modelId)
        
    temperature=0.01
    if "temperature" in evt_para.keys():
        temperature = float(evt_para['temperature'])
    print('temperature:',temperature)

    system=''
    if "system" in evt_para.keys():
        system = evt_para['system']
    print('system:',system)
    
    provider = modelId.split(".")[0]
    params = {"max_tokens": max_tokens,"temperature": temperature,"system":system}
    if "input_docs" in evt_para.keys():
        params['input_docs'] = evt_para['input_docs']
    if "related_docs" in evt_para.keys():
        params['related_docs'] = evt_para['related_docs']

    params["modelId"] = modelId
    input_body = BedrockAdapter.prepare_input(provider, prompt, params)
    body = json.dumps(input_body)
    print('body:',body)
        
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
    if modelId.find('nova') >=0:
        answer = result_body.get("output").get("message").get("content")[0].get("text")
    print('answer:',answer)
    print('embedding:',embedding)
    
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    
    if modelId == 'amazon.titan-e1t-medium' or modelId.find('amazon.titan-embed')>=0:
        response['body'] = json.dumps(
                {
                    'embedding':embedding,
                })      
    else:
        response['body'] = json.dumps(
            {
                'answer':answer,
            })
    return response