import sys
from typing import TYPE_CHECKING, Any, Dict, List
#from langchain_core.outputs import LLMResult
import time
import boto3
import json
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
class MyStreamingHandler(StreamingStdOutCallbackHandler ):
    def __init__(self, connectionId: str, domainName: str, region: str,stage:str):

        if region.find('cn') >=0 :
            endpoint_url = F"https://{domainName}.execute-api.{region}.amazonaws.com.cn/{stage}"
        else:
            endpoint_url = F"https://{domainName}.execute-api.{region}.amazonaws.com/{stage}"
        self.apigw_management = boto3.client('apigatewaymanagementapi',
                                             endpoint_url=endpoint_url)
        self.answer=''
        self.connectionId=connectionId


    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.answer=f"{self.answer}{token}"
        streaming_answer={
            'message': "streaming",
            'timestamp': time.time() * 1000,
            'sourceData': [],
            'text': self.answer,
            'scoreQueryAnswer': '',
            'contentCheckLabel': '',
            'contentCheckSuggestion': ''

        }
        response_body = json.dumps(streaming_answer)
        self.api_res = self.apigw_management.post_to_connection(ConnectionId=self.connectionId, Data=response_body)
"""  def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.answer=f"{self.answer}<end>"
        streaming_answer={
            'message': "streaming_end",
            'timestamp': time.time() * 1000,
            'sourceData': [],
            'text': self.answer,
            'scoreQueryAnswer': '',
            'contentCheckLabel': '',
            'contentCheckSuggestion': ''

        }
        response_body = json.dumps(streaming_answer)
        self.api_res = self.apigw_management.post_to_connection(ConnectionId=self.connectionId, Data=response_body)
"""