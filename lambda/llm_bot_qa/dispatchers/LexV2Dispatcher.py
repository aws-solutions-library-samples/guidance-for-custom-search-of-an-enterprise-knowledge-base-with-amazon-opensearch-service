from dispatchers import utils
import json
import os
import logging
import boto3
import time

logger = utils.get_logger(__name__)
logger.setLevel(logging.DEBUG)
CHAT_HISTORY="chat_history"
initial_history = {CHAT_HISTORY: f"AI: Hi there! How Can I help you?\nHuman: ",}

class LexV2Dispatcher():

    def __init__(self, intent_request):
        # See lex bot input format to lambda https://docs.aws.amazon.com/lex/latest/dg/lambda-input-response-format.html
        self.intent_request = intent_request
        self.localeId = self.intent_request['bot']['localeId']
        self.input_transcript = self.intent_request['inputTranscript'] # user input
        self.session_attributes = utils.get_session_attributes(
            self.intent_request)
        self.fulfillment_state = "Fulfilled"
        self.text = "" # response from endpoint
        self.message = {'contentType': 'PlainText','content': self.text}
        self.session_id = self.intent_request['sessionId']

    def dispatch_intent(self):

        
        # define prompt
        prompt_template = """The following is a friendly conversation between a human and an AI. The AI is 
        talkative and provides lots of specific details from its context. If the AI does not know 
        the answer to a question, it truthfully says it does not know. You are provided with information
        about entities the Human mentions, if relevant.

        Chat History:
        {chat_history}

        Conversation:
        Human: {input}
        AI:"""
        
        # Set context with convo history for custom memory "RAG" in langchain
        conv_context: str = self.session_attributes.get('ConversationContext',json.dumps(initial_history))

        logger.debug("Conv Conext:")
        logger.debug(conv_context)
        logger.debug(type(conv_context))

        # LLM
        # langchain_bot = SagemakerLangchainBot(
        #     prompt_template = prompt_template,
        #     sm_endpoint_name = os.environ.get("ENDPOINT_NAME","cai-lex-hf-flan-bot-endpoint"),
        #     region_name = os.environ.get('AWS_REGION',"us-east-1"),
        #     lex_conv_history = conv_context
        # )
        # if session_id is not digit, use epoch time as session_id
     
        epoch_time_ms = int(time.time()*1000)
        qa_session_id = str(epoch_time_ms)

        body ={
            'queryStringParameters':
            {
             'query':self.input_transcript,
             'task':'qa',
             'session_id':qa_session_id
            }
        }
        my_session = boto3.session.Session()
        my_region = my_session.region_name
        my_account = boto3.client('sts').get_caller_identity().get('Account')
        langchain_processor_qa_arn= "arn:aws:lambda:{}:{}:function:langchain_processor_qa".format(my_region,my_account)
        lambda_client = boto3.client('lambda')
        invoke_response = lambda_client.invoke(FunctionName=langchain_processor_qa_arn,
                                        InvocationType='RequestResponse',
                                        Payload=json.dumps(body))
        # print(invoke_response.get('Payload').get('body').get('suggestion_answer'))
        payload = invoke_response["Payload"].read().decode("utf-8")
        payload = json.loads(payload)
        llm_response= json.loads(payload.get('body')).get('suggestion_answer')
        print('llm_response-->',llm_response)
        
        self.message = {
            'contentType': 'PlainText',
            'content': llm_response
        }

        # save chat history as Lex session attributes
        session_conv_context = json.loads(conv_context)
        session_conv_context[CHAT_HISTORY] = session_conv_context[CHAT_HISTORY] + self.input_transcript + f"\nAI: {llm_response}" +"\nHuman: "
        self.session_attributes["ConversationContext"] = json.dumps(session_conv_context)

        self.response = utils.close(
            self.intent_request, 
            self.session_attributes, 
            self.fulfillment_state, 
            self.message
        )

        return self.response