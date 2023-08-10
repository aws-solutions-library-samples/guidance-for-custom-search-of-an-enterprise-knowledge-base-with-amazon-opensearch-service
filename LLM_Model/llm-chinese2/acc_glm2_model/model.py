from djl_python import Input, Output
from djl_python.streaming_utils import StreamingUtils
import os
import deepspeed
import torch
import logging
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, AutoModel
from torch import autocast

model = None
tokenizer = None


def get_model(properties):
    model_name = properties["model_id"]
    tensor_parallel_degree = properties["tensor_parallel_degree"]
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    # model = AutoModel.from_pretrained(model_name, trust_remote_code=True).half().cuda()
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True).cuda()
    model = model.eval()

    return model, tokenizer


def inference(inputs):
    try:
        input_map = inputs.get_as_json()
        data = input_map.pop("ask", input_map)
        history = input_map.pop("history", [])
        parameters = input_map.pop("parameters", {})
        outputs = Output()
        
        with torch.no_grad():
            response, history = model.chat(tokenizer, data, history, **parameters)
        
        outputs.add_as_json({"answer": response, "history": history})
        return outputs
    
    except Exception as e:
        logging.exception("Inference failed")
        # error handling
        outputs = Output().error(str(e))



def handle(inputs: Input) -> None:
    global model, tokenizer
    if not model:
        model, tokenizer = get_model(inputs.get_properties())

    if inputs.is_empty():
        # Model server makes an empty call to warmup the model on startup
        return None

    return inference(inputs)