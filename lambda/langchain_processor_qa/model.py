from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.llms import Bedrock
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.utils import enforce_stop_tokens
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.vectorstores import Zilliz
from typing import Dict, List, Optional,Any
import json

def init_embeddings(endpoint_name,region_name,language: str = "chinese"):
    
    class ContentHandler(EmbeddingsContentHandler):
        content_type = "application/json"
        accepts = "application/json"

        def transform_input(self, inputs: List[str], model_kwargs: Dict) -> bytes:
            input_str = json.dumps({"inputs": inputs, **model_kwargs})
            return input_str.encode('utf-8')

        def transform_output(self, output: bytes) -> List[List[float]]:
            response_json = json.loads(output.read().decode("utf-8"))
            return response_json

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


#init zilliz cloud
def init_zilliz_vector_store(embeddings, zilliz_endpoint, zilliz_token):

    vector_store = Zilliz(embedding_function = embeddings,
                          collection_name = 'rag',
                          connection_args = {'uri':zilliz_endpoint, 'token':zilliz_token, 'secure':True}
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
        payload = '{"inputs": [['+ inputs+']],"parameters":{"max_new_tokens": 512, "top_p": 0.9, "temperature": 0.01} }'
        print('payload:',payload)
        return payload
        
        
    def transform_output(self, response_body):
        # Load the response
        output = json.load(response_body)
        user_response = next((item['generation']['content'] for item in output if item['generation']['role'] == 'assistant'), '')
        return user_response
        
def init_model_llama2(endpoint_name,region_name,temperature):
    print('init_model_llama2')
    try:
        parameters={"max_new_tokens": 512, "top_p": 0.9, "temperature": temperature}
        content_handler = LLamaContentHandler(parameters)
        llm=SagemakerEndpoint(
                    endpoint_name=endpoint_name, 
                    region_name=region_name, 
                    model_kwargs={"parameters": parameters},
                    content_handler=content_handler,
        )
        return llm
    except Exception as e:
        return None
    
def init_model_bedrock(model_id):
    try:
        llm = Bedrock(model_id=model_id)
        return llm
    except Exception as e:
        return None
def init_model_bedrock_withstreaming(model_id,callbackHandler):
    try:
        llm = Bedrock(model_id=model_id,
                      streaming=True,
                     callbacks=[callbackHandler],)
        return llm
    except Exception as e:
        return None
def string_processor(string):
    return string.replace('\n','').replace('"','').replace('“','').replace('”','').strip()
