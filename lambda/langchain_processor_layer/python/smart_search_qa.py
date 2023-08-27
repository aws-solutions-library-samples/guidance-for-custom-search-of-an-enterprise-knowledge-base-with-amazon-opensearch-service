import os
import shutil
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import AmazonKendraRetriever
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.docstore.document import Document
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import ContentHandlerBase
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.chains.summarize import load_summarize_chain
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.utils import enforce_stop_tokens
from langchain import LLMChain
from langchain.llms import AmazonAPIGatewayBedrock
import json
from typing import Dict, List, Tuple, Optional,Any
from tqdm import tqdm
from datetime import datetime
import boto3
import numpy as np


def init_embeddings(endpoint_name,region_name,language: str = "chinese"):
    
    class ContentHandler(EmbeddingsContentHandler):
        content_type = "application/json"
        accepts = "application/json"

        def transform_input(self, inputs: List[str], model_kwargs: Dict) -> bytes:
            input_str = json.dumps({"inputs": inputs, **model_kwargs})
            return input_str.encode('utf-8')

        def transform_output(self, output: bytes) -> List[List[float]]:
            response_json = json.loads(output.read().decode("utf-8"))
            return response_json[0][0]

    content_handler = ContentHandler()

    embeddings = SagemakerEndpointEmbeddings(
        endpoint_name=endpoint_name, 
        region_name=region_name, 
        content_handler=content_handler
    )
    return embeddings


def init_vector_store(embeddings,
             index_name,
             opensearch_host,
             opensearch_port,
             opensearch_user_name,
             opensearch_user_password):

    vector_store = OpenSearchVectorSearch(
        index_name=index_name,
        embedding_function=embeddings, 
        opensearch_url="aws-opensearch-url",
        hosts = [{'host': opensearch_host, 'port': opensearch_port}],
        http_auth = (opensearch_user_name, opensearch_user_password),
    )
    return vector_store


def init_model(endpoint_name,
               region_name,
               temperature: float = 0.01):
    try:
        class ContentHandler(LLMContentHandler):
            content_type = "application/json"
            accepts = "application/json"

            def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
                print('prompt:',prompt)
                input_str = json.dumps({"ask": prompt, **model_kwargs})
                return input_str.encode('utf-8')

            def transform_output(self, output: bytes) -> str:
                response_json = json.loads(output.read().decode("utf-8"))
                return response_json['answer']

        content_handler = ContentHandler()

        llm=SagemakerEndpoint(
                endpoint_name=endpoint_name, 
                region_name=region_name, 
                model_kwargs={"temperature":temperature},
                content_handler=content_handler,
        )
        return llm
    except Exception as e:
        return None


def get_session_info(table_name, session_id):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    session_result = ""
    response = table.get_item(Key={'session-id': session_id})
    if "Item" in response.keys():
        session_result = json.loads(response["Item"]["content"])
    else:
        session_result = ""

    return session_result
    
    
def update_session_info(table_name, session_id, question, answer, intention):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    session_result = ""

    response = table.get_item(Key={'session-id': session_id})

    if "Item" in response.keys():
        chat_history = json.loads(response["Item"]["content"])
    else:
        chat_history = []

    chat_history.append([question, answer, intention])
    content = json.dumps(chat_history)

    response = table.put_item(
        Item={
            'session-id': session_id,
            'content': content
        }
    )

    if "ResponseMetadata" in response.keys():
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            update_result = "success"
        else:
            update_result = "failed"
    else:
        update_result = "failed"

    return update_result

def retrieval_from_kendra(host,query,top_k):
    kendra = boto3.client('kendra')

    kendra_response1 = kendra.describe_index(
        Id=host
    )
    index_name = kendra_response1['Name']

    kendra_response2 = kendra.query(
        QueryText = query,
        IndexId = host
    )

    documents_with_scores = []

    item_number  = top_k if len(kendra_response2['ResultItems']) > top_k else len(kendra_response2['ResultItems'])
    print('item_number:',item_number)
    for i in range(item_number):
        
        title = kendra_response2['ResultItems'][i]['DocumentTitle']['Text']
        paragraph=kendra_response2['ResultItems'][i]['DocumentExcerpt']['Text']
        metadata={'source':title}
        
        score = kendra_response2['ResultItems'][i]['ScoreAttributes']['ScoreConfidence']
        if score == "VERY_HIGH":
            _score = 5
        elif score == "HIGH":
            _score = 4
        elif score == "MEDIUM":
            _score = 3
        elif score == "LOW":
            _score = 2
        else:
            _score = 1
        
        sentence = ""
        for j in range(len(kendra_response2['ResultItems'][i]['DocumentExcerpt']['Highlights'])):
            s_begin = kendra_response2['ResultItems'][i]['DocumentExcerpt']['Highlights'][j]['BeginOffset']
            s_end = kendra_response2['ResultItems'][i]['DocumentExcerpt']['Highlights'][j]['EndOffset']
            sentence = sentence+" "+paragraph[s_begin:s_end]

        documents_with_scores.append((Document(page_content=paragraph,metadata=metadata),_score,sentence))


    return documents_with_scores

def new_call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> str:
    _model_kwargs = self.model_kwargs or {}
    _model_kwargs = {**_model_kwargs, **kwargs}
    _endpoint_kwargs = self.endpoint_kwargs or {}

    body = self.content_handler.transform_input(prompt, _model_kwargs)
    content_type = self.content_handler.content_type
    accepts = self.content_handler.accepts

    # send request
    try:
        response = self.client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            Body=body,
            ContentType=content_type,
            Accept=accepts,
            CustomAttributes='accept_eula=true',  # Added this line
            **_endpoint_kwargs,
        )
    except Exception as e:
        raise ValueError(f"Error raised by inference endpoint: {e}")

    text = self.content_handler.transform_output(response["Body"])
    if stop is not None:
        text = enforce_stop_tokens(text, stop)

    return text

# Monkey patch the class
SagemakerEndpoint._call = new_call



class LLamaContentHandler(LLMContentHandler):
    def __init__(self, parameters):
        self.parameters = parameters
    
    @property
    def content_type(self):
        return "application/json"
    
    @property
    def accepts(self):
        return "application/json"
    
    def transform_input(self, prompt: str, model_kwargs: dict):
        system_content = "You are a helpful assistant."
        history = []
        query = ''
        prompt = json.loads(prompt)
        print('trans prompt keys:',prompt.keys())
        if 'system_content' in prompt.keys():
            system_content = prompt['system_content']
        if 'history' in prompt.keys():
            history = prompt['history']
        if 'query' in prompt.keys():
            query = prompt['query']

        inputs='{"role": "system", "content":"'+ system_content + '"},'
        if len(history) > 0:
            for (question,answer) in history:
                inputs += '{"role": "user", "content":"'+ question + '"},'
                inputs += '{"role": "assistant", "content":"'+ answer + '"},'
        
        inputs += '{"role": "user", "content":"'+ query + '"}'
        payload = '{"inputs": [['+ inputs+']],"parameters":'+str(self.parameters)+' }'
        print('payload:',payload)
        return payload
        
        
    def transform_output(self, response_body):
        # Load the response
        output = json.load(response_body)
        user_response = next((item['generation']['content'] for item in output if item['generation']['role'] == 'assistant'), '')
        return user_response
        
def init_model_llama2(endpoint_name,region_name,temperature):
    try:
        parameters={}
        content_handler = LLamaContentHandler(parameters)
        llm=SagemakerEndpoint(
                    endpoint_name=endpoint_name, 
                    region_name=region_name, 
                    model_kwargs={"parameters": {"max_new_tokens": 512, "top_p": 0.9, "temperature": temperature}},
                    content_handler=content_handler,
        )
        return llm
    except Exception as e:
        return None

def string_processor(string):
    return string.replace('\n','').replace('"','').replace('“','').replace('”','').strip()


class SmartSearchQA:
    
    def init_cfg(self,
                 opensearch_index_name,
                 opensearch_user_name,
                 opensearch_user_password,
                 opensearch_or_kendra_host,
                 opensearch_port,
                 embedding_endpoint_name,
                 region,
                 llm_endpoint_name: str = 'pytorch-inference-llm-v1',
                 temperature: float = 0.01,
                 language: str = "chinese",
                 search_engine: str = "opensearch",
                 model_type:str = "normal",
                 bedrock_api_url:str = "",
                 bedrock_model_id:str="anthropic.claude-v2",
                 bedrock_max_tokens:int=500
                ):
        self.language = language
        self.search_engine = search_engine
        if model_type == "llama2":
            self.llm = init_model_llama2(llm_endpoint_name,region,temperature)
        elif model_type == "bedrock":
            self.llm = AmazonAPIGatewayBedrock(api_url=bedrock_api_url)
            parameters={
                "modelId":bedrock_model_id,
                "max_tokens":bedrock_max_tokens,
                "temperature":temperature
            }
            self.llm.model_kwargs = parameters
        else:
            self.llm = init_model(llm_endpoint_name,region,temperature)
        
        if self.search_engine == "opensearch":
            self.embeddings = init_embeddings(embedding_endpoint_name,region,self.language)
            self.vector_store = init_vector_store(self.embeddings,
                                                 opensearch_index_name,
                                                 opensearch_or_kendra_host,
                                                 opensearch_port,
                                                 opensearch_user_name,
                                                 opensearch_user_password)
        elif self.search_engine == "kendra":
            self.vector_store = None
            self.kendra_host = opensearch_or_kendra_host

    def get_qa_relation_score(self,query,answer):
        
        query_answer_emb = np.array(self.embeddings._embedding_func([query,answer]))
        query_emb = query_answer_emb[0]
        answer_emb = query_answer_emb[1]
        dot = query_emb * answer_emb 
        query_emb_len = np.linalg.norm(query_emb)
        answer_emb_len = np.linalg.norm(answer_emb)
        cos = dot.sum()/(query_emb_len * answer_emb_len)
        return cos

    def get_summarize(self,texts,
                        chain_type: str = "stuff",
                        prompt_template: str = "请根据{text}，总结一段摘要",
                        combine_prompt_template: str = "请根据{text}，总结一段摘要"
                        ):
                            
        texts = texts.split(';')
        texts_len = len(texts)
        print("texts len:",texts_len)
        
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
        COMBINE_PROMPT = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
        
        print('prompt:',PROMPT)
        
        if chain_type == "stuff":
            docs = [Document(page_content=t) for t in texts]
            chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=PROMPT)
            result = chain.run(docs)
            
        else:
            new_texts = []
            num = 20
            for i in range(0,texts_len,num):
                if i + num < texts_len:
                    end = i + num
                else:
                    end = texts_len - i
                if len(texts[i:end]) > 0:
                    new_texts.append(";".join(texts[i:end]))
            docs = [Document(page_content=t) for t in new_texts]
            
            chain = load_summarize_chain(self.llm, 
                                         chain_type=chain_type, 
                                         map_prompt=PROMPT,
                                         combine_prompt=COMBINE_PROMPT)
            result = chain({"input_documents": docs}, return_only_outputs=True)
            result = result['output_text']
        
        return result

    def get_chat(self,query,language,prompt_template,table_name,session_id,model_type):
            
        prompt = PromptTemplate(
            input_variables=["history", "human_input"], 
            template=prompt_template
        )
        
        memory = ConversationBufferMemory(return_messages=True)
        session_info = ""
        if len(session_id) > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "chat":
                        memory.chat_memory.add_user_message(item[0])
                        memory.chat_memory.add_ai_message(item[1])
            
        chat_chain = LLMChain(
            llm=self.llm,
            prompt=prompt, 
            # verbose=True, 
            memory=memory,
        )
            
        output = chat_chain.predict(human_input=query)
        
        if model_type == "bedrock":
            if language == 'chinese':
                output = output.split('\n\n人类输入')[0].strip()
            elif language == 'english':
                output = output.split('\n\nuser')[0].strip()
        
        # if language == 'english':
        #     print('English chat init output:',output)
        #     output = output.split('Answer:',1)[-1]
        #     tem_output_list = output.split('\n')
        #     for tem_output in tem_output_list:
        #         if len(tem_output) > 0:
        #             output = tem_output
        #             break
        #     print('English chat fix output:',output)
        
        if len(session_id) > 0:
            update_session_info(table_name, session_id, query, output, "chat")
        
        return output
    
    def get_retriever(self,top_k):
        
        if self.search_engine == "opensearch":
            retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
        elif self.search_engine == "kendra":
            retriever = AmazonKendraRetriever(index_id=self.kendra_host,top_k=top_k)
            
        return retriever
         

    def get_answer_from_conversational(self,query,
                                        session_id: str='',
                                        table_name: str='',
                                        language: str='chinese',
                                        prompt_template: str = "请根据{context}，回答{question}",
                                        condense_question_prompt: str="",
                                        top_k: int = 3,
                                        chain_type: str="stuff"
                                        ):
        
        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])
        combine_docs_chain_kwargs={"prompt":prompt}
        
        history = []
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "qa":
                        history.append((item[0],item[1]))
        
        print('history:',history)
        retriever = self.get_retriever(top_k)
        
        chain = ConversationalRetrievalChain.from_llm(
                    llm = self.llm,
                    chain_type=chain_type,
                    retriever=retriever,
                    condense_question_prompt = condense_question_prompt,
                    combine_docs_chain_kwargs = combine_docs_chain_kwargs,
                    return_source_documents = True,
                    return_generated_question = True
                )
        
        result = chain({"question": query, "chat_history": history})
        
        answer=result['answer']
        
        answer=answer.split('\n\nhuman')[0].split('\n\n用户')[0].split('\n\nquestion')[0].split('\n\n\ufeffquestion')[0].split('\n\nQuestion')[0].strip()
        
        # if language == "english":
        #     answer = answer.split('Answer:')[-1]
        
        if len(session_id) > 0:
            new_query=result['generated_question']
            update_session_info(table_name, session_id, new_query, answer, "qa")
        
        return result
        

    def get_answer_from_conversational_llama2(self,query,
                                        session_id: str='',
                                        table_name: str='',
                                        prompt_template: str = "",
                                        condense_question_prompt: str="",
                                        top_k: int = 3
                                        ):
        history = []
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "qa":
                        history.append((string_processor(item[0]),string_processor(item[1])))
        
        print('history:',history)
        
        new_question = string_processor(query)
        if len(history) > 0:
            for question,answer in history:
                condense_question_prompt += ('user:'+question+';')
                condense_question_prompt += ('assistant:'+answer+';')
        
            print('condense_question_prompt:',condense_question_prompt)
            
            query_trans = 'convert this question to be a standalone question:'+string_processor(query)
            prompt={'system_content':string_processor(condense_question_prompt),'query':string_processor(query_trans)}
            prompt_str = json.dumps(prompt)
            print('question trans system prompt',prompt_str)
            new_question_response = self.llm.predict(prompt_str)
            new_question = string_processor(new_question_response)
            print('new_question:',new_question)
        
        
        if self.search_engine == "opensearch":
            docs_with_scores = self.vector_store.similarity_search(new_question,k=top_k)
        elif self.search_engine == "kendra":
            docs_with_scores = retrieval_from_kendra(self.kendra_host,new_question,top_k)
        
        docs = [doc[0] for doc in docs_with_scores]
        relate_docs=''
        for i in range(len(docs)):
            page_content = string_processor(docs[i].page_content)
            if len(page_content) > 0:
                relate_docs += (page_content + ';')
        
        prompt_template += relate_docs
        prompt={'system_content':string_processor(prompt_template),'history':history,'query':new_question}
        prompt_str = json.dumps(prompt)
        print('qa system prompt',prompt_str)
        answer = self.llm.predict(prompt_str)
        
        if len(session_id) > 0:
            update_session_info(table_name, session_id, new_question, string_processor(answer), "qa")
        
        response = {'answer':answer,'source_documents':docs_with_scores}
        return response

    def get_answer_from_chat_llama2(self,query,
                                    prompt_template: str = "",
                                    table_name: str='',
                                    session_id: str=''
                                    ):
        history = []
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "chat":
                        history.append((string_processor(item[0]),string_processor(item[1])))
        
        print('history:',history)
        
        prompt={'system_content':string_processor(prompt_template),'history':history,'query':string_processor(query)}
        prompt_str = json.dumps(prompt)
        print('chat system prompt',prompt_str)
        answer = self.llm.predict(prompt_str)
        
        if len(session_id) > 0:
            update_session_info(table_name, session_id, query, string_processor(answer), "chat")
        
        return answer