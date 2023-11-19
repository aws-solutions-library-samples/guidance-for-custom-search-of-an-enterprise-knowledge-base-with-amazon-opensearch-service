import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
from smart_search_qa import SmartSearchQA
from prompt import *

lam = boto3.client('lambda')

EMBEDDING_ENDPOINT_NAME = os.environ.get('embedding_endpoint_name')
LLM_ENDPOINT_NAME = os.environ.get('llm_endpoint_name')
INDEX = os.environ.get('index')
HOST = os.environ.get('host')
LANGUAGE = os.environ.get('language')
region = os.environ.get('AWS_REGION')
zilliz_endpoint = os.environ.get('zilliz_endpoint')
zilliz_token = os.environ.get('zilliz_token')
table_name = os.environ.get('dynamodb_table_name')
search_engine_opensearch = True if str(os.environ.get('search_engine_opensearch')).lower() == 'true' else False
search_engine_kendra = True if str(os.environ.get('search_engine_kendra')).lower() == 'true' else False
search_engine_zilliz = True if str(os.environ.get('search_engine_zilliz')).lower() == 'true' else False

port = 443

TOP_K = 2

domain_name = os.environ.get('api_gw')
stage = 'prod'


def lambda_handler(event, context):
    
    print("event:",event)
    # print("region:",region)
    # print('table name:',table_name)
    
    evt_para = {}
    if 'queryStringParameters' in event.keys():
        evt_para = event['queryStringParameters']

    requestType = 'websocket'
    if isinstance(evt_para, dict) and "requestType" in evt_para.keys():
        requestType = evt_para['requestType']

    evt_body = {}
    if 'body' in event.keys() and requestType == 'websocket':
        if event['body'] != 'None':
            evt_body = json.loads(event['body'])
    else:
        evt_body = evt_para

    query = "hello"
    if "query" in evt_body.keys():
        query = evt_body['query'].strip()
    elif "q" in evt_body.keys():
        query = evt_body['q'].strip()
    print('query:', query)

    task = "search"
    if "task" in evt_body.keys():
        task = evt_body['task']
    elif "action" in evt_body.keys():
        task = evt_body['action']
    print('task:', task)

    if 'body' in event.keys() and requestType == 'websocket':
        evt_body = evt_body['configs']

    index = INDEX
    if "index" in evt_body.keys():
        index = evt_body['index']
    elif "ind" in evt_body.keys():
        index = evt_body['ind']
    elif "indexName" in evt_body.keys():
        index = evt_body['indexName']
    print('index:', index)

    isCheckedContext = False
    if "isCheckedContext" in evt_body.keys():
        isCheckedContext = bool(evt_body['isCheckedContext'])

    isCheckedGenerateReport = False
    if "isCheckedGenerateReport" in evt_body.keys():
        isCheckedGenerateReport = bool(evt_body['isCheckedGenerateReport'])

    isCheckedKnowledgeBase = True
    if "isCheckedKnowledgeBase" in evt_body.keys():
        isCheckedKnowledgeBase = bool(evt_body['isCheckedKnowledgeBase'])

    isCheckedMapReduce = False
    if "isCheckedMapReduce" in evt_body.keys():
        isCheckedMapReduce = bool(evt_body['isCheckedMapReduce'])

    language = LANGUAGE
    if "language" in evt_body.keys():
        language = evt_body['language']

    sessionId = ""
    if "sessionId" in evt_body.keys():
        sessionId = str(evt_body['sessionId'])
    print('sessionId:', sessionId)

    sessionTemplateId = ""
    if "sessionTemplateId" in evt_body.keys():
        sessionTemplateId = str(evt_body['sessionTemplateId'])
    print('sessionTemplateId:', sessionTemplateId)

    taskDefinition = ""
    if "taskDefinition" in evt_body.keys():
        taskDefinition = str(evt_body['taskDefinition'])
    print('taskDefinition:', taskDefinition)

    temperature = 0.01
    if "temperature" in evt_body.keys():
        temperature = float(evt_body['temperature'])

    embeddingEndpoint = EMBEDDING_ENDPOINT_NAME
    sagemakerEndpoint = LLM_ENDPOINT_NAME
    if "embeddingEndpoint" in evt_body.keys():
        embeddingEndpoint = evt_body['embeddingEndpoint']

    if "sagemakerEndpoint" in evt_body.keys():
        sagemakerEndpoint = evt_body['sagemakerEndpoint']

    modelType = 'normal'
    if "modelType" in evt_body.keys():
        modelType = evt_body['modelType']

    apiUrl = ''
    if "apiUrl" in evt_body.keys():
        apiUrl = evt_body['apiUrl']
        
    apiKey = ''
    if "apiKey" in evt_body.keys():
        apiKey = evt_body['apiKey']

    secretKey = ''
    if "secretKey" in evt_body.keys():
        secretKey = evt_body['secretKey']

    modelName = 'anthropic.claude-v2'
    if "modelName" in evt_body.keys():
        modelName = evt_body['modelName']

    maxTokens = 512
    if "maxTokens" in evt_body.keys():
        maxTokens = int(evt_body['maxTokens'])

    name = ''
    if "name" in evt_body.keys():
        name = evt_body['name']

    if "llmData" in evt_body.keys():
        llmData = dict(evt_body['llmData'])
        if "embeddingEndpoint" in llmData.keys():
            embeddingEndpoint = llmData['embeddingEndpoint']
        if "sagemakerEndpoint" in llmData.keys():
            sagemakerEndpoint = llmData['sagemakerEndpoint']
        if "modelName" in llmData.keys():
            modelName = llmData['modelName']
        if "modelType" in llmData.keys():
            modelType = llmData['modelType']
        recordId = ''
        if "recordId" in llmData.keys():
            recordId = llmData['recordId']
        if "apiUrl" in llmData.keys():
            apiUrl = llmData['apiUrl']
        if "apiKey" in llmData.keys():
            apiKey = llmData['apiKey']
        if "secretKey" in llmData.keys():
            secretKey = llmData['secretKey']

    searchEngine = "opensearch"
    if not search_engine_opensearch and search_engine_kendra:
        searchEngine = "kendra"
    if not search_engine_opensearch and search_engine_zilliz:
        searchEngine = "zilliz"
    if "searchEngine" in evt_body.keys():
        searchEngine = evt_body['searchEngine']

    print('searchEngine:', searchEngine)

    # Acquire Secret/Token for Content Moderation
    content_moderation_access_token = ""
    if "tokenContentCheck" in evt_body.keys():
        content_moderation_access_token = evt_body['tokenContentCheck']
    _enable_content_moderation = True if content_moderation_access_token != "" else False
    print(f"_enable_content_moderation: {_enable_content_moderation}")

    username = None
    password = None
    host = HOST
    if searchEngine == "opensearch":
        # retrieve secret manager value by key using boto3                                             
        sm_client = boto3.client('secretsmanager')
        master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
        data = json.loads(master_user)
        username = data.get('username')
        password = data.get('password')
    elif searchEngine == "kendra":
        if "kendraIndexName" in evt_body.keys():
            host = evt_body['kendraIndexName']
    print("host:", host)

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
                           embeddingEndpoint,
                           region,
                           zilliz_endpoint,
                           zilliz_token,
                           sagemakerEndpoint,
                           temperature,
                           language,
                           searchEngine,
                           modelType,
                           apiUrl,
                           modelName,
                           apiKey,
                           secretKey,
                           maxTokens
                           )

        QUERY_VERIFIED_RESULT = None

        # Verify if Query is illegal
        if _enable_content_moderation:
            moderated_result = moderate_content(
                'content_moderation',
                content_moderation_access_token,
                query
            )

            print(f"Moderated Result: {moderated_result}")

            _suggestion = moderated_result['suggestion']
            _reason = moderated_result['label']

            if _suggestion == 'block':  # illegal
                QUERY_VERIFIED_RESULT = _suggestion
                response['body'] = json.dumps(
                    {
                        'datetime': time.time() * 1000,
                        'text': query,
                        'contentCheckLabel': _reason,
                        'contentCheckSuggestion': _suggestion
                    })

        # Only if "Not enable content moderation" or "QUERY_VERIFIED pass"
        if not _enable_content_moderation or QUERY_VERIFIED_RESULT is None:

            contentCheckLabel = "Pass"
            contentCheckSuggestion = "Pass"

            if task == "chat":

                if language == "chinese":
                    prompt_template = CHINESE_CHAT_PROMPT_TEMPLATE
                elif language == "english":
                    prompt_template = ENGLISH_CHAT_PROMPT_TEMPLATE
                    if modelType == 'llama2':
                        prompt_template = EN_CHAT_PROMPT_LLAMA2
                if "prompt" in evt_body.keys() and len(evt_body['prompt']) > 0:
                    prompt_template = evt_body['prompt']

                if modelType == 'llama2':
                    result = search_qa.get_answer_from_chat_llama2(query, prompt_template, table_name, sessionId)
                else:
                    result = search_qa.get_chat(query,
                                                language,
                                                prompt_template,
                                                table_name,
                                                sessionId,
                                                modelType
                                                )

                # print('chat result:',result)

                response['body'] = json.dumps(
                    {
                        'datetime': time.time() * 1000,
                        'text': result
                    })

            elif task == "qa" or task == "search":

                if language == "chinese":
                    prompt_template = CHINESE_PROMPT_TEMPLATE
                    condense_question_prompt = CN_CONDENSE_QUESTION_PROMPT
                    responseIfNoDocsFound = '找不到答案'
                elif language == "chinese-tc":
                    prompt_template = CHINESE_TC_PROMPT_TEMPLATE
                    condense_question_prompt = TC_CONDENSE_QUESTION_PROMPT
                    responseIfNoDocsFound = '找不到答案'
                elif language == "english":
                    prompt_template = ENGLISH_PROMPT_TEMPLATE
                    condense_question_prompt = EN_CONDENSE_QUESTION_PROMPT
                    if modelType == 'llama2':
                        prompt_template = EN_CHAT_PROMPT_LLAMA2
                        condense_question_prompt = EN_CONDENSE_PROMPT_LLAMA2
                    responseIfNoDocsFound = "Can't find answer"
                if "prompt" in evt_body.keys() and len(evt_body['prompt']) > 0:
                    prompt_template = evt_body['prompt']

                topK = TOP_K
                if "topK" in evt_body.keys():
                    topK = int(evt_body['topK'])
                print('topK:', topK)

                searchMethod = 'vector'  # vector/text/mix
                if "searchMethod" in evt_body.keys():
                    searchMethod = evt_body['searchMethod']
                print('searchMethod:', searchMethod)

                txtDocsNum = 0
                if "txtDocsNum" in evt_body.keys() and evt_body['txtDocsNum'] is not None:
                    txtDocsNum = int(evt_body['txtDocsNum'])
                print('txtDocsNum:', txtDocsNum)

                if "responseIfNoDocsFound" in evt_body.keys():
                    responseIfNoDocsFound = evt_body['responseIfNoDocsFound']
                print('responseIfNoDocsFound:', responseIfNoDocsFound)

                vecDocsScoreThresholds = 0
                if "vecDocsScoreThresholds" in evt_body.keys() and evt_body['vecDocsScoreThresholds'] is not None:
                    vecDocsScoreThresholds = float(evt_body['vecDocsScoreThresholds'])
                print('vecDocsScoreThresholds:', vecDocsScoreThresholds)

                txtDocsScoreThresholds = 0
                if "txtDocsScoreThresholds" in evt_body.keys() and evt_body['txtDocsScoreThresholds'] is not None:
                    txtDocsScoreThresholds = float(evt_body['txtDocsScoreThresholds'])
                print('txtDocsScoreThresholds:', txtDocsScoreThresholds)

                if modelType == 'llama2':
                    result = search_qa.get_answer_from_conversational_llama2(query,
                                                                             sessionId,
                                                                             table_name,
                                                                             prompt_template=prompt_template,
                                                                             condense_question_prompt=condense_question_prompt,
                                                                             top_k=topK,
                                                                             )
                    _moderation_suggestion = "NOT APPLICABLE"
                    _moderation_reason = "NOT APPLICABLE"

                else:
                    result = search_qa.get_answer_from_conversational(query,
                                                                      sessionId,
                                                                      table_name,
                                                                      prompt_template=prompt_template,
                                                                      condense_question_prompt=condense_question_prompt,
                                                                      search_method=searchMethod,
                                                                      top_k=topK,
                                                                      txt_docs_num=txtDocsNum,
                                                                      response_if_no_docs_found=responseIfNoDocsFound,
                                                                      vec_docs_score_thresholds=vecDocsScoreThresholds,
                                                                      txt_docs_score_thresholds=txtDocsScoreThresholds,
                                                                      )

                print('result:', result)

                answer = result['answer']
                print('answer:', answer)

                source_documents = result['source_documents']
                if searchEngine == "opensearch":
                    source_docs = [doc[0] for doc in source_documents]
                    query_docs_scores = [doc[1] for doc in source_documents]
                    sentences = [doc[2] for doc in source_documents]
                elif searchEngine == "kendra":
                    source_docs = source_documents
                elif searchEngine == "zilliz":
                    source_docs = [doc[0] for doc in source_documents]
                    query_docs_scores = [doc[1] for doc in source_documents]
                    sentences = [doc[2] for doc in source_documents]

                # cal query_answer_score
                isCheckedScoreQA = False
                query_answer_score = -1
                if "isCheckedScoreQA" in evt_body.keys():
                    isCheckedScoreQA = bool(evt_body['isCheckedScoreQA'])
                if isCheckedScoreQA and (searchEngine == "opensearch" or searchEngine == "zilliz"):
                    if language.find("chinese") >= 0 and len(answer) > 350:
                        answer = answer[:350]
                    query_answer_score = search_qa.get_qa_relation_score(query, answer)
                print('1.query_answer_score:', query_answer_score)

                # cal answer_docs_scores
                isCheckedScoreAD = False
                answer_docs_scores = []
                if "isCheckedScoreAD" in evt_body.keys():
                    isCheckedScoreAD = bool(evt_body['isCheckedScoreAD'])
                print('isCheckedScoreAD:',isCheckedScoreAD)
                if isCheckedScoreAD and (searchEngine == "opensearch" or searchEngine == "zilliz"):
                    cal_answer = answer
                    if language.find("chinese") >= 0 and len(answer) > 150:
                        cal_answer = answer[:150]
                    for source_doc in source_docs:
                        cal_source_page_content = source_doc.page_content
                        if language.find("chinese") >= 0 and len(cal_source_page_content) > 150:
                            cal_source_page_content = cal_source_page_content[:150]
                        answer_docs_score = search_qa.get_qa_relation_score(cal_answer, cal_source_page_content)
                        answer_docs_scores.append(answer_docs_score)
                print('2.answer_docs_scores:', answer_docs_scores)

                response_type = ""
                if "response_type" in evt_body.keys():
                    response_type = evt_body['response_type']

                if response_type.find('web_ui') >= 0:
                    source_list = []
                    for i in range(len(source_docs)):
                        source = {}
                        source["_id"] = i
                        if language.find("chinese") >= 0:
                            source["_score"] = float(query_docs_scores[i]) \
                                if searchEngine == "opensearch" or searchEngine == "zilliz" else 1
                        else:
                            source["_score"] = query_docs_scores[i] \
                                if searchEngine == "opensearch" or searchEngine == "zilliz" else 1

                        try:
                            source["title"] = os.path.split(source_docs[i].metadata['source'])[-1]
                        except KeyError:
                            print("KeyError,Source not found")
                            source["title"] = ''
                        source["sentence"] = sentences[i] if searchEngine == "opensearch" or searchEngine == "zilliz" \
                            else source_docs[i].page_content.replace("\n", "")
                        source["paragraph"] = source_docs[i].page_content.replace("\n", "")
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
                            'datetime': time.time() * 1000,
                            'body': source_list,
                            'text': answer,
                            'contentCheckLabel': contentCheckLabel,
                            'contentCheckSuggestion': contentCheckSuggestion
                        })

                else:
                    source_list = []
                    for i in range(len(source_docs)):
                        source = {}
                        source["id"] = i
                        try:
                            source["title"] = os.path.split(source_docs[i].metadata['source'])[-1]
                            source["titleLink"] = "http://#"
                        except KeyError:
                            print("KeyError found")
                        source["paragraph"] = source_docs[i].page_content.replace("\n", "")
                        source["sentence"] = sentences[i] if searchEngine == "opensearch" or searchEngine == "zilliz" \
                            else source_docs[i].page_content.replace("\n", "")
                        if (searchEngine == "opensearch" or searchEngine == "zilliz") and len(query_docs_scores) > 0:
                            source["scoreQueryDoc"] = round(float(query_docs_scores[i]),3)
                        else:
                            source["scoreQueryDoc"] = -1
                            
                        if (searchEngine == "opensearch" or searchEngine == "zilliz") and len(answer_docs_scores) > 0:
                            source["scoreAnswerDoc"] = round(float(answer_docs_scores[i]),3)
                        else:
                            source["scoreAnswerDoc"] = -1
                        
                        source_list.append(source)
                    
                    response['body'] = json.dumps(
                        {
                            'timestamp': time.time() * 1000,
                            'sourceData': source_list,
                            'text': answer,
                            'scoreQueryAnswer': str(round(query_answer_score,3)),
                            'contentCheckLabel': contentCheckLabel,
                            'contentCheckSuggestion': contentCheckSuggestion

                        })

            elif task == "summarize":

                prompt_template = SUMMARIZE_PROMPT_TEMPLATE
                if "prompt" in evt_body.keys():
                    prompt_template = evt_body['prompt']

                chain_type = "stuff"
                combine_prompt_template = COMBINE_SUMMARIZE_PROMPT_TEMPLATE

                if "chain_type" in evt_body.keys():
                    chain_type = evt_body['chain_type']
                    if chain_type == "map_reduce":
                        if "combine_prompt" in evt_body.keys():
                            combine_prompt_template = evt_body['combine_prompt']

                result = search_qa.get_summarize(query, chain_type, prompt_template, combine_prompt_template)

                response['body'] = json.dumps(
                    {
                        'datetime': time.time() * 1000,
                        'summarize': result,
                        'contentCheckLabel': contentCheckLabel,
                        'contentCheckSuggestion': contentCheckSuggestion,
                    })

        if requestType == 'websocket':
            print('response body',response['body'])
            connectionId = str(event.get('requestContext', {}).get('connectionId'))
            endpoint_url = F"https://{domain_name}.execute-api.{region}.amazonaws.com/{stage}"
            apigw_management = boto3.client('apigatewaymanagementapi',
                                            endpoint_url=endpoint_url)
            api_res = apigw_management.post_to_connection(ConnectionId=connectionId,
                                                          Data=response['body'])
            print('api_res', api_res)
        else:
            return response

    except Exception as e:
        traceback.print_exc()
        return {
            'statusCode': 400,
            'body': str(e)
        }


def moderate_content(function_name, access_token, content):
    payload = {
        "content": content,
        "token": access_token
    }

    response = lam.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )

    print(f"response from moderate_content : {response}")

    _payload = response.get('Payload').read()
    print(f"payload is {_payload}")

    result = json.loads(_payload)['body']
    print(f"result : {result}")

    return result
