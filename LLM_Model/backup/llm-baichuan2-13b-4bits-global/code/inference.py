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

# from PIL import Image

import requests
import boto3
import sagemaker
import torch


# from torch import autocast
# from transformers import AutoTokenizer, AutoModelForCausalLM

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig


from huggingface_hub import snapshot_download


print("=================model_download_Start=================")

os.system("df -hl")

# model_id = "baichuan-inc/Baichuan2-7B-Chat"
model_id = "baichuan-inc/Baichuan2-13B-Chat-4bits"

LLM_NAME = snapshot_download(repo_id=model_id, cache_dir='/tmp/llm_model')

print("=================model_download_End=================")


tokenizer = AutoTokenizer.from_pretrained(LLM_NAME, use_fast=False, trust_remote_code=True)


def model_fn(model_dir):
    """
    Load the model for inference,load model from os.environ['model_name'],diffult use stabilityai/stable-diffusion-2
    
    """
    print("=================model_fn_Start=================")
    # model = AutoModelForCausalLM.from_pretrained(LLM_NAME, torch_dtype=torch.float16,
    #                                              trust_remote_code=True)
    # model = model.quantize(4).cuda()
    
    model = AutoModelForCausalLM.from_pretrained(LLM_NAME, device_map="auto",
                                                 trust_remote_code=True)
    # model = AutoModelForCausalLM.from_pretrained(LLM_NAME, device_map="auto",
    #                                              torch_dtype=torch.bfloat16, trust_remote_code=True)
    model.generation_config = GenerationConfig.from_pretrained(LLM_NAME)
    print("=================model_fn_End=================")
    return model


def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
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
        messages = []
        messages.append({"role": "user", "content": input_data['ask']})
        result = model.chat(tokenizer, messages)
        print(f'====result {result}====')
        return result
        
    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        print(f"=================Exception================={ex}")

    return 'Endpoint Failed'


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