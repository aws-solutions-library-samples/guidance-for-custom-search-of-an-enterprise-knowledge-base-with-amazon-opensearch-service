import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
import ast
from smart_search_qa import SmartSearchQA
from prompt import *
from streaming_callback_handler import MyStreamingHandler

from model import *
printTime('init-time')
lam = boto3.client('lambda')

EMBEDDING_ENDPOINT_NAME = os.environ.get('embedding_endpoint_name')
LLM_ENDPOINT_NAME = os.environ.get('llm_endpoint_name')
INDEX = os.environ.get('index')
HOST = os.environ.get('host')
LANGUAGE = os.environ.get('language')
region = os.environ.get('AWS_REGION')

table_name = os.environ.get('dynamodb_table_name')
search_engine_opensearch = True if str(os.environ.get('search_engine_opensearch')).lower() == 'true' else False
search_engine_kendra = True if str(os.environ.get('search_engine_kendra')).lower() == 'true' else False

#init the master_user of opensearch
sm_client = boto3.client('secretsmanager')
master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']

#init the vector store

port = 443

TOP_K = 3

domain_name = os.environ.get('api_gw')
stage = 'prod'

response = {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Headers":'Content-Type',
        "Access-Control-Allow-Origin": '*',
        "Access-Control-Allow-Methods":'OPTIONS,GET,POST'
    },
    "isBase64Encoded": False
}

def lambda_handler(event, context):
    contentCheckLabel = "Pass"
    contentCheckSuggestion = "Pass"

    printTime('enter handler')
    try:
        print("event:",event)
        # print("region:",region)
        # print('table name:',table_name)

        httpMethod = ''
        if 'httpMethod' in event.keys():
            httpMethod = event['httpMethod']
        print('httpMethod:',httpMethod)
        
        requestType = 'http'
        if httpMethod == '':
            requestType = 'websocket'
        print('requestType:',requestType)
        
        evt_body = {}
        if httpMethod == 'GET':
            evt_body = json.loads(event['queryStringParameters'])
        elif httpMethod == 'POST' or httpMethod == '':
            evt_body = json.loads(event['body'])

        query = "hello"
        if "query" in evt_body.keys():
            query = evt_body['query'].strip()
        print('query:', query)
        
        question = []
        if "question" in evt_body.keys():
            if isinstance(evt_body['question'],str):
                question = ast.literal_eval(evt_body['question'])
            else:
                question = evt_body['question']
        print('question:',question)
        
        if len(question) == 0 and len(query) > 0:
            question = [{'type': 'text', 'text': query}]
            print('trans question:',question)
            
        module = "RAG"
        if "module" in evt_body.keys():
            module = evt_body['module']
        print('module:',module)
        
        workMode = 'text'
        if 'workMode' in evt_body.keys():
            workMode = evt_body['workMode']
        print('workMode:',workMode)
        
        language = LANGUAGE
        if "language" in evt_body.keys():
            language = evt_body['language']        
        
        systemPrompt = ""
        if "systemPrompt" in evt_body.keys():
            systemPrompt = evt_body['systemPrompt'].strip()
        else:
            if language == "chinese":
                systemPrompt = CLAUDE3_MULTIMODEL_CN
            elif language == "chinese-tc":
                systemPrompt = CLAUDE3_MULTIMODEL_TC
            elif language == "english":
                systemPrompt = CLAUDE3_MULTIMODEL_EN
        print('systemPrompt:',systemPrompt)

        indexName = INDEX
        if "index" in evt_body.keys():
            indexName = evt_body['index']
        elif "indexName" in evt_body.keys():
            indexName = evt_body['indexName']
        print('indexName:', indexName)

        isCheckedContext = False
        if "isCheckedContext" in evt_body.keys():
            isCheckedContext = ast.literal_eval(str(evt_body['isCheckedContext']).title())

        isCheckedGenerateReport = False
        if "isCheckedGenerateReport" in evt_body.keys():
            isCheckedGenerateReport = ast.literal_eval(str(evt_body['isCheckedGenerateReport']).title())

        isCheckedKnowledgeBase = True
        if "isCheckedKnowledgeBase" in evt_body.keys():
            isCheckedKnowledgeBase = ast.literal_eval(str(evt_body['isCheckedKnowledgeBase']).title())
        print('isCheckedKnowledgeBase:', isCheckedKnowledgeBase)

        isCheckedMapReduce = False
        if "isCheckedMapReduce" in evt_body.keys():
            isCheckedMapReduce = ast.literal_eval(str(evt_body['isCheckedMapReduce']).title())

        sessionId = ""
        if "sessionId" in evt_body.keys():
            sessionId = str(evt_body['sessionId'])
        print('sessionId:', sessionId)

        temperature = 0.01
        if "temperature" in evt_body.keys():
            temperature = float(evt_body['temperature'])

        embeddingEndpoint = EMBEDDING_ENDPOINT_NAME
        sagemakerEndpoint = LLM_ENDPOINT_NAME
        if "embeddingEndpoint" in evt_body.keys():
            embeddingEndpoint = evt_body['embeddingEndpoint']

        if "sagemakerEndpoint" in evt_body.keys():
            sagemakerEndpoint = evt_body['sagemakerEndpoint']

        modelType = 'bedrock'
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

        modelName = 'anthropic.claude-3-sonnet-20240229-v1:0'
        if "modelName" in evt_body.keys():
            modelName = evt_body['modelName']

        maxTokens = 512
        if "maxTokens" in evt_body.keys():
            maxTokens = int(evt_body['maxTokens'])

        # add para: streaming output
        streaming = True
        if "streaming" in evt_body.keys():
            streaming = ast.literal_eval(str(evt_body['streaming']).title())
        if requestType != 'websocket':
            streaming = False
        print('streaming:',streaming)
        
        contextRounds = 0
        if "contextRounds" in evt_body.keys():
            contextRounds = int(evt_body['contextRounds'])
        print('contextRounds:', contextRounds)

        searchEngine = "opensearch"
        if not search_engine_opensearch and search_engine_kendra:
            searchEngine = "kendra"

        if "searchEngine" in evt_body.keys():
            searchEngine = evt_body['searchEngine']

        print('searchEngine:', searchEngine)

        username = None
        password = None
        host = HOST
        
        printTime('before opensearch init')
        if searchEngine == "opensearch":
            data = json.loads(master_user)
            username = data.get('username')
            password = data.get('password')
        elif searchEngine == "kendra":
            if "kendraIndexId" in evt_body.keys():
                host = evt_body['kendraIndexId']
        print("host:", host)

        printTime("before init_cfg")
        connectionId = str(event.get('requestContext', {}).get('connectionId'))
        search_qa = SmartSearchQA()
        search_qa.init_cfg(indexName,
                           username,
                           password,
                           host,
                           port,
                           region,
                           embeddingEndpoint,
                           sagemakerEndpoint,
                           temperature,
                           language,
                           searchEngine,
                           modelType,
                           apiUrl,
                           modelName,
                           apiKey,
                           secretKey,
                           maxTokens,
                           streaming,
                           MyStreamingHandler(connectionId,domain_name,region,stage)
                           )

        printTime("after init_cfg")


        contentCheckLabel = "Pass"
        contentCheckSuggestion = "Pass"

        print('module:',module)
        print('isCheckedKnowledgeBase:',isCheckedKnowledgeBase)
        if module == "CHAT" or not isCheckedKnowledgeBase:
            print('in the chat module')
            
            if modelName.find('anthropic.claude') >=0:
                result = search_qa.get_answer_from_multimodel(query,
                                                              question,
                                                              module,
                                                              isCheckedKnowledgeBase,
                                                              systemPrompt,
                                                              sessionId,
                                                              table_name,
                                                              work_mode = workMode,
                                                              context_rounds=contextRounds,
                                                              )
            else:
                
                if len(systemPrompt) > 0: 
                    prompt_template = systemPrompt
                else:
                    if language == "chinese":
                        prompt_template = CHINESE_CHAT_PROMPT_TEMPLATE
                    elif language == "chinese-tc":
                        prompt_template = CHINESE_TC_CHAT_PROMPT_TEMPLATE
                    elif language == "english":
                        prompt_template = ENGLISH_CHAT_PROMPT_TEMPLATE
                    
                result = search_qa.get_chat(query,
                                        prompt_template,
                                        table_name,
                                        sessionId,
                                        contextRounds,
                                        )

            if streaming and requestType == 'websocket':
                response['body'] = json.dumps(
                    {
                        'timestamp': time.time() * 1000,
                        'moduleCalled':module,
                        'sourceData': [],
                        'text': str(result),
                        'contentCheckLabel': contentCheckLabel,
                        'contentCheckSuggestion': contentCheckSuggestion,
                        'message':'streaming'
                    })
                sendWebSocket(response['body'],event)
                
            response['body'] = json.dumps(
                {
                    'message': 'streaming_end',
                    'moduleCalled':module,
                    'timestamp': time.time() * 1000,
                    'sourceData': [],
                    'text': str(result),
                    'contentCheckLabel': contentCheckLabel,
                    'contentCheckSuggestion': contentCheckSuggestion
                })

        elif module == "RAG" or isCheckedKnowledgeBase:
            print('in the rag module')

            vecTopK = TOP_K
            if "vecTopK" in evt_body.keys():
                vecTopK = int(evt_body['vecTopK'])
            print('vecTopK:', vecTopK)

            searchMethod = 'vector'  # vector/text/mix
            if "searchMethod" in evt_body.keys():
                searchMethod = evt_body['searchMethod']
            print('searchMethod:', searchMethod)

            txtTopK = 0
            if "txtTopK" in evt_body.keys() and evt_body['txtTopK'] is not None:
                txtTopK = int(evt_body['txtTopK'])
            print('txtTopK:', txtTopK)

            responseIfNoDocsFound = "Can't find answer"
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

            textField = "paragraph"
            if "textField" in evt_body.keys():
                textField = evt_body['textField']
            print('textField:', textField)
            
            imageField = "image_base64"
            if "imageField" in evt_body.keys():
                imageField = evt_body['imageField']
            print('imageField:', imageField)

            vectorField = "sentence_vector"
            if "vectorField" in evt_body.keys():
                vectorField = evt_body['vectorField']
            print('vectorField:', vectorField)
            
            rerankerEndpoint = ""
            if "rerankerEndpoint" in evt_body.keys():
                rerankerEndpoint = evt_body['rerankerEndpoint']
            print('rerankerEndpoint:', rerankerEndpoint)
            
            rewritePrompt = ""
            if "rewritePrompt" in evt_body.keys():
                rewritePrompt = evt_body['rewritePrompt']
            print('rewritePrompt:', rewritePrompt)
            
            if modelName.find('anthropic.claude') >=0:
                result = search_qa.get_answer_from_multimodel(query,
                                                              question,
                                                              module,
                                                              isCheckedKnowledgeBase,
                                                              systemPrompt,
                                                              sessionId,
                                                              table_name,
                                                              work_mode = workMode,
                                                              reranker_endpoint = rerankerEndpoint,
                                                              top_k=vecTopK,
                                                              search_method=searchMethod,
                                                              txt_docs_num=txtTopK,
                                                              response_if_no_docs_found=responseIfNoDocsFound,
                                                              vec_docs_score_thresholds=vecDocsScoreThresholds,
                                                              txt_docs_score_thresholds=txtDocsScoreThresholds,
                                                              context_rounds=contextRounds,
                                                              text_field=textField,
                                                              vector_field=vectorField,
                                                              image_field=imageField,
                                                              rewrite_system_prompt=rewritePrompt,
                                                              )
            else:
                
                if language == "chinese":
                    prompt_template = CHINESE_PROMPT_TEMPLATE
                    condense_question_prompt = CN_CONDENSE_QUESTION_PROMPT
                elif language == "chinese-tc":
                    prompt_template = CHINESE_TC_PROMPT_TEMPLATE
                    condense_question_prompt = TC_CONDENSE_QUESTION_PROMPT
                elif language == "english":
                    prompt_template = ENGLISH_PROMPT_TEMPLATE
                    condense_question_prompt = EN_CONDENSE_QUESTION_PROMPT
                    if modelType == 'llama2':
                        prompt_template = EN_CHAT_PROMPT_LLAMA2
                        condense_question_prompt = EN_CONDENSE_PROMPT_LLAMA2
                    
                if len(systemPrompt) > 0: 
                    prompt_template = systemPrompt
                    print('prompt_template:',prompt_template)
                
                result = search_qa.get_answer_from_conversational(query,
                                              sessionId,
                                              table_name,
                                              prompt_template=prompt_template,
                                              condense_question_prompt=condense_question_prompt,
                                              search_method=searchMethod,
                                              top_k=vecTopK,
                                              txt_docs_num=txtTopK,
                                              response_if_no_docs_found=responseIfNoDocsFound,
                                              vec_docs_score_thresholds=vecDocsScoreThresholds,
                                              txt_docs_score_thresholds=txtDocsScoreThresholds,
                                              context_rounds=contextRounds,
                                              text_field=textField,
                                              vector_field=vectorField,
                                              )

            print('result:', result)
            if len(result) > 0 and 'answer' in result.keys():
                answer = result['answer']
            else:
                answer = responseIfNoDocsFound
            print('answer:', answer)

            rewrite_query = ''
            if len(rewritePrompt) > 0:
                rewrite_query = result['rewrite_query']

            source_docs = []
            query_docs_scores = []
            images = ''
            if len(result) > 0 and 'source_documents' in result.keys():
                source_documents = result['source_documents']
                if searchEngine == "opensearch":
                    source_docs = [doc[0] for doc in source_documents]
                    query_docs_scores = [doc[1] for doc in source_documents]
                    if len(source_documents) > 0 and len(source_documents[0]) == 3 and workMode == 'multi-modal':
                        images = source_documents[0][2]
                    # sentences = [doc[2] for doc in source_documents]
                elif searchEngine == "kendra":
                    source_docs = source_documents

            #if enable streaming， return the souce docs before caculating the scores
            if streaming and requestType == 'websocket':
                source_list=buildSourceList(searchEngine, source_docs, images, [], [])
                response['body'] = json.dumps(
                    {
                        'message': 'streaming',
                        'moduleCalled':module,
                        'timestamp': time.time() * 1000,
                        'sourceData': source_list,
                        'text': answer,
                        'rewriteQuery':rewrite_query,
                        'scoreQueryAnswer': '',
                        'contentCheckLabel': '',
                        'contentCheckSuggestion': ''

                    })
                #print(f"if streaming and requestType == 'websocket'==={len(source_list)}")
                sendWebSocket(response['body'],event)
     
            chinese_truncation_len = 350
            english_truncation_len = 500
            # cal query_answer_score
            isCheckedScoreQA = False
            query_answer_score = -1
            if "isCheckedScoreQA" in evt_body.keys():
                isCheckedScoreQA = ast.literal_eval(str(evt_body['isCheckedScoreQA']).title())
            if isCheckedScoreQA and (searchEngine == "opensearch"):
                cal_answer = answer
                if language.find("chinese") >= 0 and len(answer) > chinese_truncation_len:
                    cal_answer = answer[:chinese_truncation_len]
                elif language.find("english") >= 0 and len(answer) > english_truncation_len:
                    cal_answer = answer[:english_truncation_len]

                if language.find("chinese") >= 0 and len(query) > chinese_truncation_len:
                    query = query[:chinese_truncation_len]
                elif language.find("english") >= 0 and len(query) > english_truncation_len:
                    query = query[:english_truncation_len]
                query_answer_score = search_qa.get_qa_relation_score(query, cal_answer)
            print('1.query_answer_score:', query_answer_score)

            # cal answer_docs_scores
            isCheckedScoreAD = False
            answer_docs_scores = []
            if "isCheckedScoreAD" in evt_body.keys():
                isCheckedScoreAD = ast.literal_eval(str(evt_body['isCheckedScoreAD']).title())
            print('isCheckedScoreAD:',isCheckedScoreAD)
            if isCheckedScoreAD and searchEngine == "opensearch":
                cal_answer = answer
                if language.find("chinese") >= 0 and len(answer) > chinese_truncation_len:
                    cal_answer = answer[:chinese_truncation_len]
                elif language.find("english") >= 0 and len(answer) > english_truncation_len:
                    cal_answer = answer[:english_truncation_len]    
                    
                for source_doc in source_docs:
                    cal_source_page_content = source_doc.page_content
                    if language.find("chinese") >= 0 and len(cal_source_page_content) > chinese_truncation_len:
                        cal_source_page_content = cal_source_page_content[:chinese_truncation_len]
                    elif language.find("english") >= 0 and len(cal_source_page_content) > english_truncation_len:
                        cal_source_page_content = cal_source_page_content[:english_truncation_len]
                    answer_docs_score = search_qa.get_qa_relation_score(cal_answer, cal_source_page_content)
                    answer_docs_scores.append(answer_docs_score)
            print('2.answer_docs_scores:', answer_docs_scores)

            #update the source list according the query_docs_scores and answer_docs_scores
            source_list = buildSourceList(searchEngine, source_docs, images, query_docs_scores, answer_docs_scores)

            response['body'] = json.dumps(
                {
                    'message': 'streaming_end',
                    'moduleCalled':module,
                    'timestamp': time.time() * 1000,
                    'sourceData': source_list,
                    'text': answer,
                    'rewriteQuery':rewrite_query,
                    'scoreQueryAnswer': str(round(query_answer_score,3)),
                    'contentCheckLabel': contentCheckLabel,
                    'contentCheckSuggestion': contentCheckSuggestion

                })

    except Exception as e:
        traceback.print_exc()
        response['body'] = json.dumps(
            {
                'timestamp': time.time() * 1000,
                'moduleCalled':module,
                'text': str(e),
                'errorMessage': str(e),
                'sourceData': [],
                'message':'error',
                'rewriteQuery':'',
                'contentCheckLabel': contentCheckLabel,
                'contentCheckSuggestion': contentCheckSuggestion,
            })

    print('response body',response['body'])

    if requestType == 'websocket':
        sendWebSocket(response['body'],event)
    else:
        return response

def sendWebSocket(msgbody,event):
    connectionId = str(event.get('requestContext', {}).get('connectionId'))
    if region.find('cn') >=0 :
        endpoint_url = F"https://{domain_name}.execute-api.{region}.amazonaws.com.cn/{stage}"
    else:
        endpoint_url = F"https://{domain_name}.execute-api.{region}.amazonaws.com/{stage}"
    apigw_management = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
    api_res = apigw_management.post_to_connection(ConnectionId=connectionId, Data=msgbody)
    print('api_res', api_res)

def buildSourceList(searchEngine, source_docs, images,query_docs_scores, answer_docs_scores):
    source_list=[]
    if not query_docs_scores or len(query_docs_scores) == 0:
        query_docs_scores = [-1] * len(source_docs)
    if not answer_docs_scores or len(answer_docs_scores) == 0:
        answer_docs_scores = [-1] * len(answer_docs_scores)
    for i in range(len(source_docs)):
        source = {}
        source["id"] = i
        source["title"] = ''
        source["source"] = source_docs[i].metadata
        if searchEngine == "opensearch":
            if 'source' in source_docs[i].metadata.keys():
                source["title"] = os.path.split(source_docs[i].metadata['source'])[-1]
            elif 'sources' in source_docs[i].metadata.keys():
                source["title"] = os.path.split(source_docs[i].metadata['sources'])[-1]
            elif 'title' in source_docs[i].metadata.keys():
                source["title"] = source_docs[i].metadata['title']
                
        if len(images) > 0 and i == 0:
            source['image'] = images
            
        source["paragraph"] = source_docs[i].page_content.replace("\n", "")
        source["sentence"] = source_docs[i].metadata['sentence'] if searchEngine == "opensearch" and 'sentence' in source_docs[i].metadata.keys() \
            else source_docs[i].page_content.replace("\n", "")
        if searchEngine == "opensearch" and len(query_docs_scores) > 0:
            source["scoreQueryDoc"] = round(float(query_docs_scores[i]),3)
        else:
            source["scoreQueryDoc"] = -1

        if searchEngine == "opensearch" and len(answer_docs_scores) > 0:
            source["scoreAnswerDoc"] = round(float(answer_docs_scores[i]),3)
        else:
            source["scoreAnswerDoc"] = -1

        source_list.append(source)
    return source_list
