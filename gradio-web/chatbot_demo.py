import streamlit as st
import os
import requests
import json
from datetime import datetime
from PIL import Image
import boto3
import pandas as pd


invoke_url = "https://rrlwyuy0o7.execute-api.us-west-1.amazonaws.com/prod"
api = invoke_url + '/langchain_processor_qa?query='

chinese_index = "smart_search_qa_test"
english_index = "smart_search_qa_test_en"

# App title
st.set_page_config(page_title="aws intelligent recommendation solution")

with st.sidebar:
    st.title('AWS Intelligent Q&A Solution Guide')
    st.subheader('Models and parameters')
    language = st.radio("Choose a language",('chinese', 'english'))
    task = st.radio("Choose a task",('chat', 'qa'))
    

st.write("## Chatbot Demo")


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    # st.session_state.messages = [{"role": "assistant", "content": "Hello,How may I assist you today?"}]
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'qa'+str(timestamp)

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'qa'+str(timestamp)
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_response(prompt):

    url = api + prompt

    url += ('&task='+task)
    url += ('&session_id='+st.session_state.sessionId)
    url += ('&top_k=1')
    if language == "english":
        url += '&language=english'
        url += ('&embedding_endpoint_name=huggingface-inference-eb-en')
        url += ('&llm_embedding_name=pytorch-inference-llm-v1-en')
        url += ('&index='+english_index)
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embedding_endpoint_name=huggingface-inference-eb')
        url += ('&llm_embedding_name=pytorch-inference-llm-v1')
        url += ('&index='+chinese_index)
 

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    answer = result['suggestion_answer']
    
    return answer


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    answer = ''
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            placeholder = st.empty()
            try:
                answer = generate_response(prompt)
                placeholder.markdown(answer)
            except:
                try:
                    answer = generate_response(prompt)
                    placeholder.markdown(answer)
                except:
                    placeholder.markdown("Sorry,please try again!")
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)