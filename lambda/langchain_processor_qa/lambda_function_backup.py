import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
from smart_search_qa import SmartSearchQA
from prompt import *

EMBEDDING_ENDPOINT_NAME = os.environ.get('embedding_endpoint_name')
LLM_ENDPOINT_NAME = os.environ.get('llm_endpoint_name')
INDEX =  os.environ.get('index')
HOST =  os.environ.get('host')
LANGUAGE =  os.environ.get('language')
region = os.environ.get('AWS_REGION')
table_name = os.environ.get('dynamodb_table_name')
search_engine_opensearch = True if str(os.environ.get('search_engine_opensearch')).lower() == 'true' else False
search_engine_kendra = True if str(os.environ.get('search_engine_kendra')).lower() == 'true' else False


port = 443

TOP_K = 2


def lambda_handler(event, context):
    
    print("event:",event)
    print("region:",region)
    print('table name:',table_name)
    evt_body = json.loads(event['body'])
    
    index = INDEX
    if "index" in event['queryStringParameters'].keys():
        index = event['queryStringParameters']['index']
    elif "ind" in event['queryStringParameters'].keys():
        index = event['queryStringParameters']['ind']
    elif "index" in evt_body.keys():
        index = evt_body['index']
    elif "ind" in evt_body.keys():
        index = evt_body['ind']
    elif "indexName" in evt_body.keys():
        index = evt_body['indexName']
    print('index:',index)
    
    isCheckedContext= False
    if "isCheckedContext" in evt_body.keys():
        isCheckedContext = bool(evt_body['isCheckedContext'])

    isCheckedGenerateReport= False
    if "isCheckedGenerateReport" in evt_body.keys():
        isCheckedGenerateReport = bool(evt_body['isCheckedGenerateReport'])

    isCheckedKnowledgeBase= True
    if "isCheckedKnowledgeBase" in evt_body.keys():
        isCheckedKnowledgeBase = bool(evt_body['isCheckedKnowledgeBase'])

    isCheckedMapReduce= False
    if "isCheckedMapReduce" in evt_body.keys():
        isCheckedMapReduce = bool(evt_body['isCheckedMapReduce'])
    
    language=LANGUAGE
    if "language" in event['queryStringParameters'].keys():
        language = event['queryStringParameters']['language']
    elif "language" in evt_body.keys():
        language = evt_body['language']

    session_id=""
    if "session_id" in event['queryStringParameters'].keys():
        session_id = str(event['queryStringParameters']['session_id'])
    elif "sessionId" in evt_body.keys():
        sessionId = str(evt_body['sessionId'])
    print('session_id:',session_id)
    
    sessionTemplateId=""
    if "sessionTemplateId" in evt_body.keys():
        sessionTemplateId = str(evt_body['sessionTemplateId'])
    print('sessionTemplateId:',sessionTemplateId)

    taskDefinition=""
    if "taskDefinition" in evt_body.keys():
        taskDefinition = str(evt_body['taskDefinition'])
    print('taskDefinition:',taskDefinition)


    temperature=0.01
    if "temperature" in event['queryStringParameters'].keys():
        temperature = float(event['queryStringParameters']['temperature'])
    elif "temperature" in evt_body.keys():
        temperature = float(evt_body['temperature'])

  
    embedding_endpoint_name=EMBEDDING_ENDPOINT_NAME
    if "embedding_endpoint_name" in event['queryStringParameters'].keys():
        embedding_endpoint_name = event['queryStringParameters']['embedding_endpoint_name']
        
    llm_embedding_name=LLM_ENDPOINT_NAME
    if "llm_embedding_name" in event['queryStringParameters'].keys():
        llm_embedding_name = event['queryStringParameters']['llm_embedding_name']

    search_engine = "opensearch"
    if not search_engine_opensearch and search_engine_kendra:
        search_engine = "kendra"
    if "search_engine" in event['queryStringParameters'].keys():
        search_engine = event['queryStringParameters']['search_engine']
    print('search_engine:',search_engine)

    username = None
    password = None
    host = HOST
    if search_engine == "opensearch":
        # retrieve secret manager value by key using boto3                                             
        sm_client = boto3.client('secretsmanager')
        master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
        data= json.loads(master_user)
        username = data.get('username')
        password = data.get('password')
    elif search_engine == "kendra":
        if "kendra_index_id" in event['queryStringParameters'].keys():
            host = event['queryStringParameters']['kendra_index_id']
    print("host:",host)
  
    model_type = 'normal'
    if "model_type" in event['queryStringParameters'].keys():
        model_type = event['queryStringParameters']['model_type']
  
    bedrock_api_url = ''
    if "bedrock_api_url" in event['queryStringParameters'].keys():
        bedrock_api_url = event['queryStringParameters']['bedrock_api_url']
  
    bedrock_model_id = 'anthropic.claude-v2'
    if "bedrock_model_id" in event['queryStringParameters'].keys():
        bedrock_model_id = event['queryStringParameters']['bedrock_model_id']

    bedrock_max_tokens = 500
    if "bedrock_max_tokens" in event['queryStringParameters'].keys():
        bedrock_max_tokens = int(event['queryStringParameters']['bedrock_max_tokens'])
  
  
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    try:
        search_qa = SmartSearchQA()
        search_qa.init_cfg(index,
                         username,
                         password,
                         host,
                         port,
                         embedding_endpoint_name,
                         region,
                         llm_embedding_name,
                         temperature,
                         language,
                         search_engine,
                         model_type,
                         bedrock_api_url,
                         bedrock_model_id,
                         bedrock_max_tokens
                         )
            
        query = "hello"
        if "query" in event['queryStringParameters'].keys():
            query = event['queryStringParameters']['query'].strip()
        elif "q" in event['queryStringParameters'].keys():
            query = event['queryStringParameters']['q'].strip()
        print('query:', query)
        
        
        task = "qa"    
        if "task" in event['queryStringParameters'].keys():
            task = event['queryStringParameters']['task']
        print('task:',task)

        if task == "chat":
            
            if language == "chinese":
                prompt_template = CHINESE_CHAT_PROMPT_TEMPLATE
            elif language == "english":
                prompt_template = ENGLISH_CHAT_PROMPT_TEMPLATE
                if model_type == 'llama2':    
                    prompt_template = EN_CHAT_PROMPT_LLAMA2
            if "prompt" in event['queryStringParameters'].keys():
                prompt_template = event['queryStringParameters']['prompt']            
            
            if model_type == 'llama2':
                result = search_qa.get_answer_from_chat_llama2(query,prompt_template,table_name,session_id)
            else:
                result = search_qa.get_chat(query,language,prompt_template,table_name,session_id,model_type)
            
            
            print('chat result:',result)
            
            response['body'] = json.dumps(
            {
                'datetime':time.time(),
                'suggestion_answer':result
            })
            print('response:',response)
            return response

        elif task == "qa":

            if language == "chinese":
                prompt_template = CHINESE_PROMPT_TEMPLATE
                condense_question_prompt = CN_CONDENSE_QUESTION_PROMPT
                response_if_no_docs_found = '找不到答案'
            elif language == "chinese-tc":
                prompt_template = CHINESE_TC_PROMPT_TEMPLATE
                condense_question_prompt = TC_CONDENSE_QUESTION_PROMPT
                response_if_no_docs_found = '找不到答案'
            elif language == "english":
                prompt_template = ENGLISH_PROMPT_TEMPLATE
                condense_question_prompt = EN_CONDENSE_QUESTION_PROMPT
                if model_type == 'llama2':    
                    prompt_template = EN_CHAT_PROMPT_LLAMA2
                    condense_question_prompt = EN_CONDENSE_PROMPT_LLAMA2
                response_if_no_docs_found = "Can't find answer"
            if "prompt" in event['queryStringParameters'].keys():
                prompt_template = event['queryStringParameters']['prompt']
                
            top_k = TOP_K
            if "top_k" in event['queryStringParameters'].keys():
                top_k = int(event['queryStringParameters']['top_k'])
            print('top_k:',top_k)
            
            search_method = 'vector' #vector/aos/mix
            if "search_method" in event['queryStringParameters'].keys():
                search_method = event['queryStringParameters']['search_method']
            print('search_method:',search_method)
    
            aos_docs_num = 0
            if "aos_docs_num" in event['queryStringParameters'].keys():
                aos_docs_num = int(event['queryStringParameters']['aos_docs_num'])
            print('aos_docs_num:',aos_docs_num)   
            
            if "response_if_no_docs_found" in event['queryStringParameters'].keys():
                response_if_no_docs_found = event['queryStringParameters']['response_if_no_docs_found']
            print('response_if_no_docs_found:',response_if_no_docs_found)
            
            vec_docs_score_thresholds = 0
            if "vec_docs_score_thresholds" in event['queryStringParameters'].keys():
                vec_docs_score_thresholds = float(event['queryStringParameters']['vec_docs_score_thresholds'])
            print('vec_docs_score_thresholds:',vec_docs_score_thresholds) 
            
            aos_docs_score_thresholds = 0
            if "aos_docs_score_thresholds" in event['queryStringParameters'].keys():
                aos_docs_score_thresholds = float(event['queryStringParameters']['aos_docs_score_thresholds'])
            print('aos_docs_score_thresholds:',aos_docs_score_thresholds) 
            
            if model_type == 'llama2':                            
                result = search_qa.get_answer_from_conversational_llama2(query,
                                            session_id,
                                            table_name,
                                            prompt_template=prompt_template,
                                            condense_question_prompt=condense_question_prompt,
                                            top_k=top_k
                                            )
            else:
                result = search_qa.get_answer_from_conversational(query,
                            session_id,
                            table_name,
                            prompt_template=prompt_template,
                            condense_question_prompt=condense_question_prompt,
                            top_k=top_k,
                            search_method=search_method,
                            aos_docs_num=aos_docs_num,
                            response_if_no_docs_found=response_if_no_docs_found,
                            vec_docs_score_thresholds=vec_docs_score_thresholds,
                            aos_docs_score_thresholds=aos_docs_score_thresholds
                            )
                    
            print('result:',result)
            
            answer = result['answer']
            print('answer:',answer)
            
            source_documents = result['source_documents']
            if search_engine == "opensearch":
                source_docs = [doc[0] for doc in source_documents]
                query_docs_scores = [doc[1] for doc in source_documents]
                sentences = [doc[2] for doc in source_documents]
            elif search_engine == "kendra":
                source_docs = source_documents
                
            #cal query_answer_score
            cal_query_answer_score = "false"
            query_answer_score = -1
            if "cal_query_answer_score" in event['queryStringParameters'].keys():
                cal_query_answer_score = event['queryStringParameters']['cal_query_answer_score']
            if cal_query_answer_score == 'true' and search_engine == "opensearch":
                if language.find("chinese")>=0 and len(answer) > 350:
                    answer = answer[:350]
                query_answer_score = search_qa.get_qa_relation_score(query,answer)
            print('1.query_answer_score:',query_answer_score)
                
            #cal answer_docs_scores
            cal_answer_docs_score = "false"
            answer_docs_scores = []
            if "cal_answer_docs_score" in event['queryStringParameters'].keys():
                cal_answer_docs_score = event['queryStringParameters']['cal_answer_docs_score']
            if cal_answer_docs_score == 'true' and search_engine == "opensearch":
                cal_answer = answer
                if language.find("chinese")>=0 and len(answer) > 150:
                    cal_answer = answer[:150]
                for source_doc in source_docs:
                    cal_source_page_content = source_doc.page_content
                    if language.find("chinese")>=0 and len(cal_source_page_content) > 150:
                        cal_source_page_content = cal_source_page_content[:150]
                    answer_docs_score = search_qa.get_qa_relation_score(cal_answer,cal_source_page_content)
                    answer_docs_scores.append(answer_docs_score)
            print('2.answer_docs_scores:',answer_docs_scores)
            
            #cal docs_list_overlap_score
            docs_list_overlap_score = -1
            cal_docs_list_overlap_score = "false"
            if "cal_docs_list_overlap_score" in event['queryStringParameters'].keys():
                cal_docs_list_overlap_score = event['queryStringParameters']['cal_docs_list_overlap_score']
            if cal_docs_list_overlap_score == 'true' and search_engine == "opensearch":       
                find_answer_top_k = 3
                answer_relate_docs = search_qa.get_retriever(find_answer_top_k).get_relevant_documents(answer)
                print('answer_relate_docs:',answer_relate_docs)
                answer_relate_docs = [doc[0] for doc in answer_relate_docs]

                find_index = []
                for answer_relate_doc in answer_relate_docs:
                    try:
                        relate_source = answer_relate_doc.metadata['source']
                        relate_page_content = answer_relate_doc.page_content
                    except KeyError:
                        print("KeyError found")
                        continue
                    for i in range(len(source_docs)):
                        source_page_content = source_docs[i].page_content
                        if source_page_content == relate_page_content:
                            find_index.append(i)
                            break
                print('find_index:',find_index)

                if len(find_index) > 0:                
                    list_score = 0
                    find_topk = 1
                    query_relate_docs_len = len(source_docs)
                    answer_relate_docs_len = len(answer_relate_docs)
                    for i in range(query_relate_docs_len):
                        for j in range(len(find_index)):
                            if i == find_index[j]:
                                list_score += (query_relate_docs_len-i)*(answer_relate_docs_len-j)        
                    print('qa_list_score:',list_score)

                    total = query_relate_docs_len*answer_relate_docs_len
                    if query_relate_docs_len > 1 and answer_relate_docs_len > 1:
                        total += (query_relate_docs_len-1)*(answer_relate_docs_len-1)
                    print('total score:',total)

                    docs_list_overlap_score = round(list_score/total,3)
            print('3.docs_list_overlap_score:',docs_list_overlap_score)
                    
            response_type = ""
            if "response_type" in event['queryStringParameters'].keys():
                response_type = event['queryStringParameters']['response_type']         

            if response_type.find('web_ui') >= 0:
                
                source_list = []
                for i in range(len(source_docs)):
                    source = {}
                    source["_id"] = i
                    if language.find("chinese")>=0: 
                        source["_score"] = float(query_docs_scores[i])*100 if search_engine == "opensearch" else 1
                    else:
                        source["_score"] = query_docs_scores[i] if search_engine == "opensearch" else 1
                    
                    try:
                        source["title"] = os.path.split(source_docs[i].metadata['source'])[-1]
                    except KeyError:
                        print("KeyError,Source not found")
                        source["title"] = ''
                    source["sentence"] = sentences[i] if search_engine == "opensearch" else source_docs[i].page_content.replace("\n","")
                    source["paragraph"] =source_docs[i].page_content.replace("\n","")
                    source["sentence_id"] = i
                    if 'row' in source_docs[i].metadata.keys():
                        source["paragraph_id"] = source_docs[i].metadata['row']
                    elif 'page' in source_docs[i].metadata.keys():
                        source["paragraph_id"] = source_docs[i].metadata['page']
                    else:
                        source["paragraph_id"] = i
                    source_list.append(source)
                                     
                response['body'] = json.dumps(
                {
                    'datetime':time.time(),
                    'body': source_list,
                    'suggestion_answer': answer
                    
                })

            else:    
                source_list = []
                for i in range(len(source_docs)):
                    source = {}
                    source["id"] = i
                    try:
                        source["source"] = os.path.split(source_docs[i].metadata['source'])[-1]
                    except KeyError:
                        print("KeyError found")                    
                    source["paragraph"] =source_docs[i].page_content.replace("\n","")
                    source["sentence"] = sentences[i] if search_engine == "opensearch" else source_docs[i].page_content.replace("\n","")
                    if language.find("chinese")>=0: 
                        source["score"] = float(query_docs_scores[i])*100 if search_engine == "opensearch" else 1
                    else:
                        source["score"] = query_docs_scores[i] if search_engine == "opensearch" else 1

                    source_list.append(source)
            
                query_docs_score = query_docs_scores[0] if search_engine == "opensearch" and len(query_docs_scores) > 0 else -1
                answer_docs_score = max(answer_docs_scores) if len(answer_docs_scores) > 0 else -1
                response['body'] = json.dumps(
                {
                    'datetime':time.time(),
                    'source_list': source_list,
                    'suggestion_answer': answer,
                    'query_docs_score': str(query_docs_score),
                    'query_answer_score': str(query_answer_score),
                    'answer_docs_score': str(answer_docs_score),
                    'docs_list_overlap_score' : str(docs_list_overlap_score),
                    
                })
            return response

        elif task == "summarize":
            
            prompt_template = SUMMARIZE_PROMPT_TEMPLATE
            if "prompt" in event['queryStringParameters'].keys():
                prompt_template = event['queryStringParameters']['prompt']

            chain_type = "stuff"  
            combine_prompt_template = COMBINE_SUMMARIZE_PROMPT_TEMPLATE
            if "chain_type" in event['queryStringParameters'].keys():
                chain_type = event['queryStringParameters']['chain_type']
                if chain_type =="map_reduce":
                    if "combine_prompt" in event['queryStringParameters'].keys():
                        combine_prompt_template = event['queryStringParameters']['combine_prompt']
            
            result = search_qa.get_summarize(query,chain_type,prompt_template,combine_prompt_template)
            
            response['body'] = json.dumps(
            {
                'datetime':time.time(),
                'summarize': result
            })
            
            return response

    except Exception as e:
        traceback.print_exc()
        return {
            'statusCode': 400,
            'body': str(e)
        }