
# from transformers import AutoTokenizer, AutoModel
import torch

import json
# import torch.nn.functional as F

from transformers import BertTokenizer, BertModel

EB_NAME = 'shibing624/text2vec-base-chinese'

# Helper: Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def model_fn(model_dir):
    print("=================model_fn_Start=================")
    tokenizer = BertTokenizer.from_pretrained(EB_NAME)
    model = BertModel.from_pretrained(EB_NAME)
    print("=================model_fn_End=================")
    return model, tokenizer

def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
    print(f"=================input_fn=================\n{request_content_type}\n{request_body}")
    input_data = json.loads(request_body)
    print(input_data)
    return input_data



def predict_fn(data, model_and_tokenizer):
    
    print(f"=================predict_fn=================\n")
    print(data)
    # destruct model and tokenizer
    model, tokenizer = model_and_tokenizer

    # Tokenize sentences
    sentences = data.pop("inputs", data)
    
    ebs = []
    
    for sentence in sentences:
    
        encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            model_output = model(**encoded_input)
        # Perform pooling. In this case, mean pooling.
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
        
        ebs.append(sentence_embeddings.tolist())

    # return dictonary, which will be json serializable
    return ebs
    # return sentence_embeddings.tolist()
    # return {"vectors": sentence_embeddings.tolist()}

def output_fn(prediction, content_type):
    """
    Serialize and prepare the prediction output
    """
    print(f"=================out_fn_type=================\n")
    print(content_type)
    return [prediction]