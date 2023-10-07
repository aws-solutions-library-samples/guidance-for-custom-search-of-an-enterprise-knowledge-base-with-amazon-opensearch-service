import json
import boto3
import os
from os import environ
import time
# from llama_cpp import Llama


def find_first_bin_file(root_path):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.bin'):
                return os.path.join(root, file)
    return None


if "MODEL_PATH" not in environ.keys() or environ["MODEL_PATH"] is None:
    check_path = "/opt/program/model"
    bin_file_path = find_first_bin_file(check_path)
    if bin_file_path:
        environ["MODEL_PATH"] = bin_file_path
    else:
        print('Error, can not find model file')
        exit(1)

if "CONTEXT_SIZE" not in environ.keys() or environ["CONTEXT_SIZE"] is None:
    environ["CONTEXT_SIZE"] = '512'

model_path = environ['MODEL_PATH']
n_ctx = int(environ['CONTEXT_SIZE'])

print('Loading Model...')
print('Model Path: ', model_path)
print('Maximum context size: ', n_ctx)
os.system('ls ')

# model = Llama(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=100, use_mlock=True)

from ctransformers import AutoModelForCausalLM
llm = AutoModelForCausalLM.from_pretrained(model_path, model_type="llama", gpu_layers=50)


print('Load Model Done...')



def handler(event, context):

    print('event: ', event)

    try:
        prompt = event['prompt']
        prompt = str(prompt)
        print('Prompt: ', prompt)

        if 'max_tokens' not in event.keys():
            event['max_tokens'] = '512'
        
        if 'temperature' not in event.keys():
            event['temperature'] = '0.8'
        
        max_tokens = int(event['max_tokens'])
        temperature = float(event['temperature'])

        print("Max Tokens: ", max_tokens)
        print('Temperature: ', temperature)

        start = time.time()

        response = llm(prompt)

        # response = output['choices'][0]['text']

        print('Response: ', response)
        timecost = '{:.3f}'.format(time.time() - start)
        print('Time Cost: ', timecost)
        
        return {
            'statusCode': 200,
            'body': response,
            'timecost': timecost
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': e
        }