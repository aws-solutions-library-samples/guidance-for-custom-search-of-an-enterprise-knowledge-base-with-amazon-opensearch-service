import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
from smart_search_qa import SmartSearchQA
from prompt import *


EMBEDDING_ENDPOINT_NAME = "huggingface-inference-eb-zh"
LLM_ENDPOINT_NAME = "pytorch-inference-chatglm2-g5-4x"

index = "huixiaoer_1027"
search_engine = 'opensearch'
language = "chinese"

sm_client = boto3.client('secretsmanager')
master_user = sm_client.get_secret_value(SecretId='opensearch-host-url')['SecretString']
data= json.loads(master_user)
es_host_name = data.get('host')
host = es_host_name+'/' if es_host_name[-1] != '/' else es_host_name# cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com/
host = host[8:-1]
region = boto3.Session().region_name # e.g. cn-north-1
print('host:',host)
print('region:',region)

sm_client = boto3.client('secretsmanager')
master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
data= json.loads(master_user)
username = data.get('username')
password = data.get('password')
port = 443

if language == "chinese":
    prompt_template = CHINESE_PROMPT_TEMPLATE
    condense_question_prompt = CN_CONDENSE_QUESTION_PROMPT
elif language == "english":
    prompt_template = ENGLISH_PROMPT_TEMPLATE
    condense_question_prompt = EN_CONDENSE_QUESTION_PROMPT

table_name = 'LambdaStack-ChatSessionRecord189120C3-AY8RLOK9671A'
session_id = ''

    
def test_chat():
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine
                     )
    
    
    if language == "chinese":
        prompt_template = CHINESE_CHAT_PROMPT_TEMPLATE
    elif language == "english":
        prompt_template = ENGLISH_CHAT_PROMPT_TEMPLATE
        if model_type == 'llama2':    
            prompt_template = EN_CHAT_PROMPT_LLAMA2
            
    model_type = 'chatglm'
    query = '我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店'
    result = search_qa.get_chat(query,language,prompt_template,table_name,session_id,model_type)
    print('chat result:',result)

def test_chat_llama2():
    
    LLM_ENDPOINT_NAME = 'meta-textgeneration-llama-2-7b-f-2023-07-19-06-07-05-430'
    language = "english"
    model_type = 'llama2'
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type
                     )
    
    
    if language == "chinese":
        prompt_template = CHINESE_CHAT_PROMPT_TEMPLATE
    elif language == "english":
        prompt_template = ENGLISH_CHAT_PROMPT_TEMPLATE
        if model_type == 'llama2':    
            prompt_template = EN_CHAT_PROMPT_LLAMA2
            
    query = 'how to fly from beijing to hongkong?'
    result = search_qa.get_answer_from_chat_llama2(query,prompt_template,table_name,session_id)
    print('llama2 chat result:',result)

    
def test_rag_chatglm():
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine
                     )
    query = '我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店'
    top_k =2
    result = search_qa.get_answer_from_conversational(query,
                        session_id,
                        table_name,
                        prompt_template=prompt_template,
                        condense_question_prompt=condense_question_prompt,
                        top_k=top_k
                        )
                    
    print('rag chatglm result:',result)
    
def test_rag_llama2():
    
    LLM_ENDPOINT_NAME = 'meta-textgeneration-llama-2-7b-f-2023-07-19-06-07-05-430'
    EMBEDDING_ENDPOINT_NAME = 'pytorch-inference-all-minilm-l6-v2'
    language = "english"
    model_type = 'llama2'
    index = 'hktdc_hr_handbook_0928'
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type
                     )
        
    prompt_template = EN_CHAT_PROMPT_LLAMA2
    condense_question_prompt = EN_CONDENSE_PROMPT_LLAMA2
            
    query = 'how to fly from beijing to hongkong?'
    top_k =2
    result = search_qa.get_answer_from_conversational_llama2(query,
                            session_id,
                            table_name,
                            prompt_template=prompt_template,
                            condense_question_prompt=condense_question_prompt,
                            top_k=top_k
                            )
    print('rag llama2 result:',result)
    
def test_chat_bedrock_api():
    
    bedrock_url = 'https://l05s3tnj06.execute-api.us-west-2.amazonaws.com/prod/bedrock?'
    model_type = "bedrock_api"
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type,
                     bedrock_api_url= bedrock_url,
                     bedrock_model_id = "anthropic.claude-v2",
                     bedrock_max_tokens = 500
                     )
    
    
  
    prompt_template = CLAUDE_CHAT_PROMPT_CN            
    query = "我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店."
    
    result = search_qa.get_chat(query,language,prompt_template,table_name,session_id,model_type)
    print('bedrock chat result:',result)
    

def test_rag_bedrock_api():
    
    bedrock_url = 'https://l05s3tnj06.execute-api.us-west-2.amazonaws.com/prod/bedrock?'
    model_type = "bedrock_api"
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type,
                     bedrock_api_url= bedrock_url,
                     bedrock_model_id = "anthropic.claude-v2",
                     bedrock_max_tokens = 500
                     )
    
    
  
    prompt_template = CLAUDE_RAG_PROMPT_CN            
    query = "我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店."
    top_k =2
    result = search_qa.get_answer_from_conversational(query,
                        session_id,
                        table_name,
                        prompt_template=prompt_template,
                        condense_question_prompt=condense_question_prompt,
                        top_k=top_k
                        )
                    
    print('rag bedrock result:',result)
    
def test_chat_bedrock():
    
    model_type = "bedrock"
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type,
                     bedrock_model_id = "anthropic.claude-v2",
                     bedrock_max_tokens = 500
                     )
    
    prompt_template = CLAUDE_CHAT_PROMPT_CN            
    query = "我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店."
    
    result = search_qa.get_chat(query,language,prompt_template,table_name,session_id,model_type)
    print('bedrock chat result:',result)

def test_rag_bedrock():

    model_type = "bedrock"
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type,
                     bedrock_model_id = "anthropic.claude-v2",
                     bedrock_max_tokens = 500
                     )
    
    
  
    prompt_template = CLAUDE_RAG_PROMPT_CN            
    query = "我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店."
    top_k =2
    result = search_qa.get_answer_from_conversational(query,
                        session_id,
                        table_name,
                        prompt_template=prompt_template,
                        condense_question_prompt=condense_question_prompt,
                        top_k=top_k
                        )
                    
    print('rag bedrock result:',result)    
    
def test_rag_bedrock_aos():

    model_type = "bedrock"
#     search_method = 'aos'
    search_method = 'mix'
    aos_docs_num = 3
    response_if_no_docs_found = '找不到答案'
    vec_docs_score_thresholds = 0.7
    aos_docs_score_thresholds = 0.8
    
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type,
                     bedrock_model_id = "anthropic.claude-v2",
                     bedrock_max_tokens = 500
                     )
    prompt_template = CLAUDE_RAG_PROMPT_CN            
    query = "我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店."
#     query = "飞机怎么飞？"
    top_k =2
    result = search_qa.get_answer_from_conversational(query,
                        session_id,
                        table_name,
                        prompt_template=prompt_template,
                        condense_question_prompt=condense_question_prompt,
                        top_k=top_k,
                        search_method = search_method,
                        aos_docs_num = aos_docs_num,
                        response_if_no_docs_found = response_if_no_docs_found,
                        vec_docs_score_thresholds = vec_docs_score_thresholds,
                        aos_docs_score_thresholds = aos_docs_score_thresholds         
                        )
                    
    print('rag bedrock result:',result)      
    
def test_rag_bedrock_mix():

    model_type = "bedrock"
    search_method = 'mix'
    aos_docs_num = 3
    
    search_qa = SmartSearchQA()
    search_qa.init_cfg(index,
                     username,
                     password,
                     host,
                     port,
                     EMBEDDING_ENDPOINT_NAME,
                     region,
                     LLM_ENDPOINT_NAME,
                     temperature = 0.01,
                     language = language,
                     search_engine = search_engine,
                     model_type = model_type,
                     bedrock_model_id = "anthropic.claude-v2",
                     bedrock_max_tokens = 500
                     )
    prompt_template = CLAUDE_RAG_PROMPT_CN            
    query = "我想找一个在广州琶洲的酒店开展培训，人数在300左右，酒店平均每天价格3000元，请我看看是否有符合要求的酒店."
    top_k =2
    result = search_qa.get_answer_from_conversational(query,
                        session_id,
                        table_name,
                        prompt_template=prompt_template,
                        condense_question_prompt=condense_question_prompt,
                        top_k=top_k,
                        search_method = search_method,
                        aos_docs_num = aos_docs_num
                        )
                    
    print('rag bedrock result:',result)      
    
    
    
    
    
if __name__ == '__main__':
    test_chat()
#     test_chat_llama2()
#     test_rag_chatglm()
#     test_rag_llama2()
#     test_chat_bedrock_api()
#     test_rag_bedrock_api()
#     test_chat_bedrock()
#     test_rag_bedrock()
#     test_rag_bedrock_aos()
#     test_rag_bedrock_mix()