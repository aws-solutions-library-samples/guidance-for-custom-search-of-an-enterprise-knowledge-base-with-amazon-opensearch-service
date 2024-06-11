import streamlit as st
import os
import requests
import json
from datetime import datetime
from PIL import Image
import boto3
import pandas as pd


invoke_url = 'https://u80f0arzu8.execute-api.us-west-2.amazonaws.com/prod'
api = invoke_url + '/langchain_processor_qa?query='

chinese_index = ""
#data_index = "giant_demo_0423"
#video_index = 'giant_demo_0423_video_3'


cn_embedding_endpoint = ''
cn_llm_endpoint = ''
en_embedding_endpoint = 'cohere.embed-multilingual-v3'
en_llm_endpoint = ''
model_name = 'anthropic.claude-3-sonnet-20240229-v1:0'


prompt = """
You are a maintenance engineer of a bicycle company. Please briefly answer the user's questions based on the following relevant documents. No preface is needed. Answer the user's questions directly.

<documents>
{context}
<documents>

The user's question is:{question}

"""


# App title
st.set_page_config(page_title="aws intelligent recommendation solution")

with st.sidebar:
    st.title('AWS Intelligent Q&A Solution Guide')
    #st.subheader('Models and parameters')
    #language = st.radio("Choose a language",('chinese', 'chinese-tc', 'english'))
    #task = st.radio("Choose a task",('chat', 'qa'))
    #video_search = st.checkbox('Vidoe Search')
    data_index = st.selectbox("Select PDF index",['giant_demo_0423','giant_demo_0508','giant_demo_0509_2'])
    video_index = st.selectbox("Select video index",['giant_demo_0423_video_3','giant_demo_0509_video'])
    language = 'english'
    task = 'qa'
    topK = st.slider("Search documents",min_value=1, max_value=6, value=3, step=1)
    contextRounds = st.slider("History rounds",min_value=0, max_value=5, value=3, step=1)
    videoConfidenceScoer = st.slider("Video confidence score",min_value=0.0, max_value=1.0, value=0.6, step=0.01)
    DocConfidenceScoer = st.slider("Documents confidence score",min_value=0.0, max_value=1.0, value=0.5, step=0.01)


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
    for key in st.session_state.keys():
        del st.session_state[key]

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

# Function for generating LLM response
def generate_response(query,index,topK,contextRounds):

    url = api + query

    url += ('&task='+task)
    url += ('&sessionId='+st.session_state.sessionId)
    url += ('&topK='+str(topK))
    url += ('&requestType=multimodel')
    url += ('&modelType=bedrock')
    url += ('&modelName='+model_name)
    url += ('&streaming=False')
    url += ('&prompt='+prompt)
    url += ('&vectorField=sentence_vector')
    url += ('&textField=paragraph')
    url += ('&contextRounds='+str(contextRounds))
    url += ('&index='+index)
    if language == "english":
        url += '&language=english'
        url += ('&embeddingEndpoint='+en_embedding_endpoint)
        #url += ('&sagemakerEndpoint='+cn_llm_endpoint)
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        #url += ('&sagemakerEndpoint='+cn_llm_endpoint)
    elif language == "chinese-tc":
        url += '&language=chinese-tc'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        #url += ('&sagemakerEndpoint='+cn_llm_endpoint)
 
    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print('result:',result)
    
    return result



def get_video(query):

    url = api + query

    url += '&task=qa'
    url += '&topK=1'
    url += '&requestType=http'
    url += ('&index='+video_index)
    url += '&language=english'
    #url += '&isCheckedKnowledgeBase=False'
    url += ('&embeddingEndpoint='+en_embedding_endpoint)

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print('result:',result)
    #docs = result['docs']
    docs = result['sourceData']
    return docs


# User-provided prompt
if query := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    answer = ''
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            placeholder = st.empty()
            try:
            #if True:
                result = generate_response(query,video_index,topK,contextRounds)
                answer = result['text']
                sourceData = result['sourceData']
                scoreQueryDoc = 0
                if len(sourceData) > 0:
                    scoreQueryDoc = float(sourceData[0]['scoreQueryDoc'])
                print('scoreQueryDoc:',scoreQueryDoc)
                if scoreQueryDoc > videoConfidenceScoer and answer.find('Unfortunately') < 0:
                    print('answer:',answer)
                    placeholder.markdown(answer)
                    video = ''
                    for data in sourceData:   
                        source = data['title']
                        metadata = data['source']
                        video_source = metadata['video']
                        video_start = metadata['start']
                        video_url = 'https://d3p6u5b51qma4a.cloudfront.net/' + video_source
                        subtitles = 'new_giant_srt/' + source
                        print('subtitles:',subtitles)
                        st.write('You can refer to the following video: '+ video_source)
                        st.video(video_url,format="video/mp4", start_time=int(video_start),subtitles=subtitles)
                        break
                else:
                    result = generate_response(query,data_index,topK,contextRounds)
                    answer = result['text']
                    sourceData = result['sourceData']
                    scoreQueryDoc = 0
                    if len(sourceData) > 0:
                        scoreQueryDoc = float(sourceData[0]['scoreQueryDoc'])
                    print('scoreQueryDoc:',scoreQueryDoc)
                    if scoreQueryDoc > DocConfidenceScoer:
                        print('answer:',answer)
                        placeholder.markdown(answer)
                        for data in sourceData:
                            source = data['title']
                            image = ''
                            page = 0
                            metadata = data['source']
                            if 'type' in metadata.keys():
                                if metadata['type'] == 'pdf':
                                    page = metadata['page']
                                    image = metadata['image']
                            if len(source) >= 0 and len(image) > 0:
                                st.write('You can refer to the following documents:' + source + ',  Page:'+ str(page))
                                image_path = 'https://d3p6u5b51qma4a.cloudfront.net/' + image
                                st.image(image_path)
                            elif len(source) >= 0:
                                st.write('You can refer to the following documents:' + source)
                    else:
                        st.write("Sorry, Can't fine the answer,please try angin")

            except:
                placeholder.markdown("Sorry,please try again!")
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)