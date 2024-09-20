import streamlit as st
import os
import requests
import json
from datetime import datetime
from PIL import Image
import pandas as pd
import io, base64

invoke_url = 'https://oqjzlhql2l.execute-api.us-east-1.amazonaws.com/prod'
api = invoke_url + '/multi_modal_qa?query='

default_index = ""
chinese_index = ""
english_index = ""
excel_index = 'wy_demo_excel_0822'
wts_index = 'wy_demo_wts_0822'
image_index = 'wy_demo_image_2'

cn_embedding_endpoint = ''
cn_llm_endpoint = ''
en_embedding_endpoint = 'cohere.embed-multilingual-v3'
en_llm_endpoint = ''

modelName = "anthropic.claude-3-haiku-20240307-v1:0"
#modelName = "meta.llama3-8b-instruct-v1:0"


prompt_template = """
The content of the related documents is the operation information of machine maintenance. Please combine the operation information into a machine maintenance guide.

<instruction>
1.There is no need for a preface,no need to point out the source of the answer,and directly output the answer.
2.The answer should be simple.
3.Answer strictly according to the document content, don't make up answer.
</instruction>
"""


# App title
st.set_page_config(page_title="aws intelligent recommendation solution")

with st.sidebar:
    st.title('AWS Intelligent Q&A Solution Guide')
    #st.subheader('Models and parameters')
    #language = st.radio("Choose a language",('chinese', 'chinese-tc', 'english'))
    #task = st.radio("Choose a task",('chat', 'qa'))
    language = 'english'
    task = 'RAG'
    mode = st.radio("mode",["Q&A","Image"])

    if mode == 'Q&A':
        excel_index = st.text_input(label="Input the excel index", value=excel_index)
        wts_index = st.text_input(label="Input the wts index", value=wts_index)
        topK = 1
        action_prompt = st.text_area("Action Prompt",prompt_template,height=300)
    elif mode == 'Image':
        image_index = st.text_input(label="Input the image index", value=image_index)
        topK = st.slider("Vector Search Number",min_value=1, max_value=3, value=1, step=1)
    
    search_type  = "vector"
    vectorConfidence = st.slider("Vector score Threshold",min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    textSearchNumber = 0
    textScoreThresholds = 0.0

    #contextRounds = st.slider("Input the context rounds",min_value=0, max_value=3, value=0, step=1)
    contextRounds = 0


st.write("## Chatbot Demo")


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    # st.session_state.messages = [{"role": "assistant", "content": "Hello,How may I assist you today?"}]
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]
    elif language == 'chinese-tc':
        st.session_state.messages = [{"role": "assistant", "content": "您好，請問有什麽可以幫助您嗎?"}]
        
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
    elif language == 'chinese-tc':
        st.session_state.messages = [{"role": "assistant", "content": "您好，請問有什麽可以幫助您嗎?"}]

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'qa'+str(timestamp)
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


def generate_response(prompt):

    url = api + prompt

    url += ('&task='+task)
    url += ('&sessionId='+st.session_state.sessionId)
    url += ('&requestType=http')
    url += ('&index='+excel_index)
    url += ('&indexWTS='+wts_index)
    url += ('&contextRounds='+str(contextRounds))
    url += '&language=english'
    url += ('&embeddingEndpoint='+en_embedding_endpoint)
    
    if len(modelName)>0: 
        url += ('&modelName='+modelName)
        url += ('&modelType=bedrock')
        url += ('&maxTokens=2048')
    
    if len(action_prompt) > 0:
        url += ('&systemPrompt='+action_prompt)

    url += ('&searchMethod='+search_type)
    if topK > 0:
        url += ('&vecTopK='+str(topK))
    if textSearchNumber > 0:
        url += ('&txtTopK='+str(textSearchNumber))
    if float(textScoreThresholds) > 0:
        url += ('&txtDocsScoreThresholds='+str(textScoreThresholds))

    if float(vectorConfidence) > 0:
        url += ('&vecDocsScoreThresholds='+str(vectorConfidence))
    
    url += ('&responseIfNoDocsFound=找不到問題的答案，請試���其他問題吧!')

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    #print('result:',result)
    answer = result['text']
    #print('answer:',answer)
    source_data = result['sourceData']
    if len(source_data) >=2:
        excel_source = source_data[0]['source']
        excel_score = source_data[0]['scoreQueryDoc']

        wts_source = source_data[1]['source']
        wts_score = source_data[1]['scoreQueryDoc']
        wts_id = wts_source['id']
        project = wts_source['teamProject']
        #print('project:',project)
        #answer = "id:" + str(wts_id) + ",System.TeamProject:" + str(project) + ',action:'+answer
        answer = str(wts_id) + "," + str(project) + "," + answer
        #print('answer:',answer)

        source_data = [{"excel_source":excel_source,"Query-Doc-Score":excel_score},{"wts_source":wts_source,"Query-Doc-Score":wts_score}]
   
    elif len(source_data) == 1:
        source = source_data[0]['source']
        score = source_data[0]['scoreQueryDoc']
        source_data = [{"source":source,"Query-Doc-Score":score}]


    return answer,source_data


def get_image(prompt):

    url = api + prompt

    url += ('&module=Image')
    url += ('&sessionId='+st.session_state.sessionId)
    url += ('&requestType=http')
    url += ('&index='+image_index)
    url += ('&embeddingEndpoint='+en_embedding_endpoint)

    url += ('&searchMethod='+search_type)
    if topK > 0:
        url += ('&vecTopK='+str(topK))
    if textSearchNumber > 0:
        url += ('&txtTopK='+str(textSearchNumber))
    if float(textScoreThresholds) > 0:
        url += ('&txtDocsScoreThresholds='+str(textScoreThresholds))

    if float(vectorConfidence) > 0:
        url += ('&vecDocsScoreThresholds='+str(vectorConfidence))

    url += ('&responseIfNoDocsFound=找不到問題的答案，請試試其他問題吧!')

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    #print('result:',result)
    answer = result['text']
    print('answer:',answer)
    source_data = result['sourceData']

    return source_data


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
            #try:
            if True:
                if mode == "Q&A":
                    answer,source = generate_response(prompt)
                    print('answer:',answer)
                    st.write(answer)
                    with st.expander("Data Source"):
                        st.write(source)
                elif mode == "Image":
                    source_datas = get_image(prompt)
                    for source_data in source_datas:
                        image_base64 = source_data['source']['image_code'].split(',')[-1]
                        img = Image.open(io.BytesIO(base64.decodebytes(bytes(image_base64, "utf-8"))))
                        name = source_data['source']['id']+'.jpeg'
                        img.save(name)
                        st.image(name)

                        #subject = source_data['source']['subject']
                        description = source_data['source']['sentence']

                        with st.expander("Description"):
                            st.markdown(description)

    
                        os.remove(name)

                #placeholder.markdown(answer)
            #except:
            #    placeholder.markdown("找不到問題的答案，請試試其他問題吧!")
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)