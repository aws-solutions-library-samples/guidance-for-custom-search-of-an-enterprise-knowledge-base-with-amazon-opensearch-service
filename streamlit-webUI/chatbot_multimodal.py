import streamlit as st
import os
import requests
import json
from datetime import datetime
from PIL import Image
import pandas as pd


invoke_url = ''
api = invoke_url + ''

chinese_index = ""
english_index = ""

cn_embedding_endpoint = ''
cn_llm_endpoint = ''
en_embedding_endpoint = ''
en_llm_endpoint = ''

modelName = "anthropic.claude-3-sonnet-20240229-v1:0"


prompt_template = """
你是一名電商網站客服人員. 任務是根據給定的文檔迴複用戶的問題，請根據下面的相關文檔，迴答用戶的提問，如果參考文檔中的答案包含參考圖片，需要每個答案點中間插入圖片鏈接，圖片的鏈接使用標籤<image></image>，例子如下:
<iamge>
https://sample-image.png
</image>
不要在最後才輸出圖片鏈接，用繁體中文迴答,不要前���，不要輸出『根據參考文檔』、『作為一家網上商店的店主』等前言,直接輸出答案。

問題:{question}

<related doc>
{context}
</related doc>

答案:

"""


trans_prompt_template = """
你是一名電商網站客服人員. 任務是任務是將用戶提問的問題改寫生成一個新問題，使得新問題更能體現問題的語義。
不要前言，直接輸出答案。

{history}
問題:{human_input}

答案:

"""


def containEnglish(query):
    import re
    return bool(re.search('[A-Z]',query)) or bool(re.search('[a-z]',query))


# App title
st.set_page_config(page_title="aws intelligent recommendation solution")

with st.sidebar:
    st.title('AWS Intelligent Q&A Solution Guide')
    #st.subheader('Models and parameters')
    #language = st.radio("Choose a language",('chinese', 'chinese-tc', 'english'))
    #task = st.radio("Choose a task",('chat', 'qa'))
    language = 'chinese-tc'
    task = 'qa'
    index = st.text_input(label="Input the index", value=chinese_index)
    search_type  = st.radio("Search Type",["vector","text",'mix'])
    topK = st.slider("Vector Search Number",min_value=1, max_value=10, value=1, step=1)
    #topK = 1
    vectorConfidence = st.slider("Vector score Threshold",min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    textSearchNumber = st.slider("Text Search Number",min_value=1, max_value=10, value=3, step=1)
    textScoreThresholds = st.slider("Text Score Threshold",min_value=0.0, max_value=1.0, value=0.5, step=0.01)   

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


def query_rewrite(query):
    url = api + prompt
    url += ('&task=chat')
    url += ('&requestType=http')

    if len(modelName)>0:
        url += ('&modelName='+modelName)
        url += ('&modelType=bedrock')
        url += ('&maxTokens=2048')

    if len(trans_prompt_template) > 0:
        url += ('&prompt='+trans_prompt_template)

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    answer = result['text']
    print('rewrite query:',answer)

    return answer


def generate_response(prompt):

    url = api + prompt

    url += ('&task='+task)
    url += ('&sessionId='+st.session_state.sessionId)
    url += ('&topK='+str(topK))
    url += ('&requestType=http')
    url += ('&index='+index)
    url += ('&contextRounds='+str(contextRounds))
    url += ('&sourceFilter=True')
    if language == "english":
        url += '&language=english'
        url += ('&embeddingEndpoint='+en_embedding_endpoint)
        url += ('&sagemakerEndpoint='+en_llm_endpoint)
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        url += ('&sagemakerEndpoint'+cn_llm_endpoint)
    elif language == "chinese-tc":
        url += '&language=chinese-tc'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        if len(cn_llm_endpoint) > 0:
            url += ('&sagemakerEndpoint='+cn_llm_endpoint)

    if len(modelName)>0: 
        url += ('&modelName='+modelName)
        url += ('&modelType=bedrock')
        url += ('&maxTokens=2048')
    
    if len(prompt_template) > 0:
        url += ('&prompt='+prompt_template)

    url += ('&searchMethod='+search_type)
    if topK > 0:
        url += ('&topK='+str(topK))
    if textSearchNumber > 0:
        url += ('&txtDocsNum='+str(textSearchNumber))
    if float(textScoreThresholds) > 0:
        url += ('&txtDocsScoreThresholds='+str(textScoreThresholds))

    if float(vectorConfidence) > 0:
        url += ('&vecDocsScoreThresholds='+str(vectorConfidence))
    
    url += ('&responseIfNoDocsFound=找不到問題的答案，請試試其他問題吧!')

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print('result:',result)
    answer = result['text']
    print('answer:',answer)
    source_data = result['sourceData']
    source = ''
    if len(source_data) > 0:
        source = source_data[0]['title']

    return answer,source


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
            # if True:
                if containEnglish(prompt):
                    prompt = query_rewrite(prompt)
                

                answer,source = generate_response(prompt)
                answer_list = answer.split('<image>')
                for text in answer_list:
                    text_list = text.split('</image>')
                    for t in text_list:
                        t = t.strip()
                        if t.find('https') >=0:
                            link = t
                            if t.find('https') >0:
                                link = 'https' + t.split('https')[1]
                            link_list = link.split('/')
                            if len(link_list[-1].split('.')) >2 :
                                link = link.replace(link_list[-1],'')
                            
                            if link.find('#') > 0:
                                link = link.split('#')[0]
                            
                            print('image link:',link)
                            st.image(link)
                        else:
                            st.write(t.replace('<image>','').strip())
                if len(source) > 0:
                    st.write('參考文檔:'+source)
            except:
                placeholder.markdown("找不到問題的答���，請試試其他問題吧!")
    message = {"role": "assistant", "content": answer}
    st.session_state.messages.append(message)