# -*- coding: utf-8 -*-
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import json
import uuid
import io
import sys

import traceback

from PIL import Image

import requests
import boto3
import sagemaker
import torch


from torch import autocast
from transformers import AutoTokenizer, AutoModelForCausalLM

from huggingface_hub import snapshot_download


# LLM_NAME = ""

print("=================model_download_Start=================")

LLM_NAME = snapshot_download(repo_id="tiiuae/falcon-40b-instruct", cache_dir='/tmp/llm_model')

print("=================model_download_End=================")

tokenizer = AutoTokenizer.from_pretrained(LLM_NAME)



def preprocess(text):
    text = text.replace("\n", "\\n").replace("\t", "\\t")
    return text

def postprocess(text):
    return text.replace("\\n", "\n").replace("\\t", "\t")

def answer(ask, model, temperature=0.1, max_new_tokens=512, top_p=1.0):
    inputs = tokenizer.encode(ask, return_tensors='pt').to('cuda')
    with torch.no_grad():
        tokens = model.generate(
         input_ids=inputs,
         max_new_tokens=max_new_tokens,
         do_sample=True,
         temperature=temperature,
         top_p=top_p,
        )
    answer = tokenizer.decode(tokens[0], skip_special_tokens=True)
    # print(answer)
    return answer


def model_fn(model_dir):
    """
    Load the model for inference,load model from os.environ['model_name'],diffult use stabilityai/stable-diffusion-2
    
    """
    print("=================model_fn_Start=================")
    
    # model = AutoModelForCausalLM.from_pretrained(LLM_NAME, trust_remote_code=True).half().cuda()
    model = AutoModelForCausalLM.from_pretrained(LLM_NAME, torch_dtype=torch.float16, device_map='auto', trust_remote_code=True)
    print("=================model_fn_End=================")
    return model


def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
    # {
    # "ask": "写一个文章，题目是未来城市"
    # }
    print(f"=================input_fn=================\n{request_content_type}\n{request_body}")
    input_data = json.loads(request_body)
    if 'ask' not in input_data:
        input_data['ask']="写一个文章，题目是未来城市"
    return input_data


def predict_fn(input_data, model):
    """
    Apply model to the incoming request
    """
    print("=================predict_fn=================")
   
    print('input_data: ', input_data)
    

    try:
        # if 'temperature' not in input_data:
        #     temperature = 0.5
        # else:
        #     temperature = input_data['temperature']
        result = answer(**input_data, model=model)
        # result = answer(input_data['ask'], temperature=temperature, model=model)
        print(f'====result {result}====')
        return result
        
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        print(f"=================Exception================={ex}")

    return 'Endpoint work error'


def output_fn(prediction, content_type):
    """
    Serialize and prepare the prediction output
    """
    print(content_type)
    return json.dumps(
        {
            'answer': prediction
        }
    )