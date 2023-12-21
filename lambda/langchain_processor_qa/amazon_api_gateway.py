from typing import Any, Dict, List, Mapping, Optional

import requests
import warnings

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from langchain.pydantic_v1 import Extra
import json
import time
import hashlib
import zhipuai

def calculate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    encrypted = md5.hexdigest()
    return encrypted
    
HUMAN_PROMPT = "\n\nHuman:"
ASSISTANT_PROMPT = "\n\nAssistant:"
ALTERNATION_ERROR = (
    "Error: Prompt must alternate between '\n\nHuman:' and '\n\nAssistant:'."
)


def _add_newlines_before_ha(input_text: str) -> str:
    new_text = input_text
    for word in ["Human:", "Assistant:"]:
        new_text = new_text.replace(word, "\n\n" + word)
        for i in range(2):
            new_text = new_text.replace("\n\n\n" + word, "\n\n" + word)
    return new_text


def _human_assistant_format(input_text: str) -> str:
    if input_text.count("Human:") == 0 or (
        input_text.find("Human:") > input_text.find("Assistant:")
        and "Assistant:" in input_text
    ):
        input_text = HUMAN_PROMPT + " " + input_text  # SILENT CORRECTION
    if input_text.count("Assistant:") == 0:
        input_text = input_text + ASSISTANT_PROMPT  # SILENT CORRECTION
    if input_text[: len("Human:")] == "Human:":
        input_text = "\n\n" + input_text
    input_text = _add_newlines_before_ha(input_text)
    count = 0
    # track alternation
    for i in range(len(input_text)):
        if input_text[i : i + len(HUMAN_PROMPT)] == HUMAN_PROMPT:
            if count % 2 == 0:
                count += 1
            else:
                warnings.warn(ALTERNATION_ERROR + f" Received {input_text}")
        if input_text[i : i + len(ASSISTANT_PROMPT)] == ASSISTANT_PROMPT:
            if count % 2 == 1:
                count += 1
            else:
                warnings.warn(ALTERNATION_ERROR + f" Received {input_text}")

    if count % 2 == 1:  # Only saw Human, no Assistant
        input_text = input_text + ASSISTANT_PROMPT  # SILENT CORRECTION

    return input_text
    

class ContentHandlerAmazonAPIGateway:
    """Adapter to prepare the inputs from Langchain to a format
    that LLM model expects.

    It also provides helper function to extract
    the generated text from the model response."""

    @classmethod
    def transform_input(
        cls, prompt: str, model_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {"inputs": prompt, "parameters": model_kwargs}

    @classmethod
    def transform_output(cls, response: Any) -> str:
        return response.json()[0]["generated_text"]

    @classmethod
    def transform_input_baichuan(
        cls, prompt: str, model_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        input_format =  {
            "model": model_kwargs['modelId'],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        return input_format

    @classmethod
    def transform_output_baichuan(cls, response: Any) -> str:
        print('response text:',json.loads(response.text))
        return json.loads(response.text)['data']['messages'][0]['content']
        
    @classmethod
    def transform_output_chatglm(cls, response: Any) -> str:
        return response['data']['choices'][0]['content'][1:-1].strip()
        
    @classmethod
    def transform_input_bedrock(
        cls, provider: str,prompt: str, model_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        input_body = {"parameters": model_kwargs}
        if provider == "anthropic":
            input_body["prompt"] = _human_assistant_format(prompt)
        elif provider in ("ai21", "cohere", "meta"):
            input_body["prompt"] = prompt
        elif provider == "amazon":
            input_body = dict()
            input_body["inputText"] = prompt
            input_body["textGenerationConfig"] = {**model_kwargs}
        else:
            input_body["inputText"] = prompt

        if provider == "anthropic" and "max_tokens_to_sample" not in input_body:
            input_body["max_tokens_to_sample"] = 256

        return input_body

    @classmethod
    def transform_output_bedrock(cls, response: Any) -> str:
        return json.loads(response.text)['answer']
    

class AmazonAPIGateway(LLM):
    """Amazon API Gateway to access LLM models hosted on AWS."""

    api_url: str
    """API Gateway URL"""

    headers: Optional[Dict] = None
    """API Gateway HTTP Headers to send, e.g. for authentication"""

    model_kwargs: Optional[Dict] = None
    """Keyword arguments to pass to the model."""

    content_handler: ContentHandlerAmazonAPIGateway = ContentHandlerAmazonAPIGateway()
    """The content handler class that provides an input and
    output transform functions to handle formats between LLM
    and the endpoint.
    """

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        _model_kwargs = self.model_kwargs or {}
        return {
            **{"api_url": self.api_url, "headers": self.headers},
            **{"model_kwargs": _model_kwargs},
        }

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "amazon_api_gateway"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call out to Amazon API Gateway model.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = se("Tell me a joke.")
        """
        _model_kwargs = self.model_kwargs or {}
        modelId = ''
        if 'modelId' in _model_kwargs.keys():
            modelId = _model_kwargs['modelId']
        
        if modelId.find('anthropic') >= 0 or modelId.find('meta') >= 0:
            provider = modelId.split(".")[0]
            payload = self.content_handler.transform_input_bedrock(provider, prompt, _model_kwargs)
            try:
                prompt = payload['prompt']
                print('******')
                print('bedrock prompt:',prompt)
                print('*******')
                url = self.api_url + ('prompt='+prompt)
                parameters = payload['parameters']
                print('parameters:',parameters)
                for key in parameters.keys():
                    url += ('&'+key+'='+str(parameters[key]))
                    
                print('url:',url)
                response = requests.get(url)
                text = self.content_handler.transform_output_bedrock(response)
    
            except Exception as error:
                raise ValueError(f"Error raised by the service: {error}")            
            
        elif modelId.find('Baichuan') >= 0:
            payload = self.content_handler.transform_input_baichuan(prompt, _model_kwargs)
            api_key = _model_kwargs['api_key']
            secret_key = _model_kwargs['secret_key']
            time_stamp = int(time.time())
            json_data = json.dumps(payload)
            signature = calculate_md5(secret_key + json_data + str(time_stamp))
            
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key,
                "X-BC-Request-Id": "your requestId",
                "X-BC-Timestamp": str(time_stamp),
                "X-BC-Signature": signature,
                "X-BC-Sign-Algo": "MD5",
            }
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                )
                text = self.content_handler.transform_output_baichuan(response)
            except Exception as error:
                raise ValueError(f"Error raised by the service: {error}")
            
        elif modelId.find('chatglm') >= 0:
            api_key = _model_kwargs['api_key']
            zhipuai.api_key = api_key
            
            print('prompt:',prompt)
            
            try:
                response = zhipuai.model_api.invoke(
                    model=modelId,
                    prompt=[
                        {"role": "user", "content": prompt},
                    ]
                )
                text = self.content_handler.transform_output_chatglm(response)
                text = eval('"'+text+'"')
                print('text:',text)
                
            except Exception as error:
                raise ValueError(f"Error raised by the service: {error}")

        if stop is not None:
            text = enforce_stop_tokens(text, stop)

        return text
