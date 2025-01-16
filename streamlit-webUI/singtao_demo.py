import streamlit as st
import os
import requests
import json
from datetime import datetime
from PIL import Image
import boto3
import pandas as pd
import websocket
from websocket import create_connection, WebSocketTimeoutException

invoke_url = 'https://yxzsros6mc.execute-api.us-east-1.amazonaws.com/prod'
api = invoke_url + '/multi_modal_qa?query='

index = "singtao_demo_1025_2"
english_index = ""

cn_embedding_endpoint = 'cohere.embed-multilingual-v3'
cn_llm_endpoint = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
en_embedding_endpoint = ''
en_llm_endpoint = ''
reranker_endpoint = 'bge-m3-reranker-2024-09-17-07-14-26-136-endpoint'
WEBSOCKET_PATH = 'wss://nkb20y2rk2.execute-api.us-east-1.amazonaws.com/prod/'

LAST_REPLY = ""

websocket.setdefaulttimeout(60)



prompt_template = """
你是一個網站新聞內容編輯，任務是根據用戶的搜索問題和相關新聞，首先是根據相關新聞回答用戶的問題，然後生成用戶可能感興趣的新聞問題,
目標��讓客戶繼續點擊感興趣的新聞觀看。

<instruction>
1.直接回答用戶的問題和生成用戶可能感興趣的相關新聞問題，不需要前言
2.生成的答案必須嚴格根據給定的相關文檔生成，不能胡編亂造
2.生成的用戶問題答案在<answer></answer>tag内，生成的用戶可能感興趣的相關新聞問題在<related></related>tag内
3.生成的问题答案在150字内，要求有：（1）提供事件的基本背景或重要性，（2）說明事件的具體安排、參與者及其活動，（3）簡要提及事件的後續影響或相關活動
4.生成的相關新聞問題數量最多5個
</instruction>

<example>
用户输入问题: 特郎普選情如何？
回复：
<answer>
特郎普目前在多個州領先
</answer>
<related>
這是特郎普選舉相關的問題：
为什么特朗普在共和党内仍然如此受欢迎？
特朗普的经济政策有哪些具体措施？
特朗普的支持者们对他的领导风格有什么看法？
特朗普的竞选对手们都退选了吗？
特朗���的言论是否会影响他的选举结果？
</related>
</example>

"""


rewrite_prompt = """
你是一個網站客服，任務是对有问题的用戶搜索問題进行改写，改写规则如下：
<rewriting rules>

1、如果用戶的提問包含以下發的詞語轉換規則，請按規則轉換提問的詞語
<Word conversion rules>
1.‘武漢肺炎’ 转为 ‘新冠肺炎’
2.‘的士佬 , 小巴佬 , 巴士佬, etc.’ 转为 ‘的士司機, 小巴司機, 巴士司機 , etc.’
3.‘裝修佬,冷氣佬, etc.’ 转为 ‘裝修師傅, 冷氣技工 , etc.’
4.‘支那人’ 转为 ‘       中國人’
5.‘美國佬/英國佬/印度佬 , etc.’ 转为 ‘美國人/英國人/印度人 , etc.’
6.‘鬼佬’ 转为 ‘外國人’
7.‘呀叉’ 转为 ‘印度人 / 巴基斯坦裔人士’
8.‘摩羅差’ 转为 ‘印度人 / 巴基斯坦裔人士’
9.‘咖哩佬’ 转为 ‘(印度人)       印度人’
10.‘黑鬼’ 转为 ‘黑人 / 非裔人士’
11.‘猶太���’ 转为 ‘猶太人 / 猶太社群’
12.‘阿拉伯豬’ 转为 ‘阿拉伯人 / 中東裔人士’
13.‘巴基躝坦’ 转为 ‘巴基斯坦’
14.‘老野’ 转为 ‘長者’
15.‘雞 / 鴨 (性工作者)’ 转为 ‘性工作者’
16.‘死肥仔, 死肥婆, etc.’ 转为 ‘體重較重的男士/女士’
17.‘白卡佬, 痴線佬, etc.’ 转为 ‘有精神健康問題人士’
18.‘乞衣, 乞丐, etc.’ 转为 ‘無家者’
19.‘地產狗’ 转为 ‘地產代理’
20.‘AA’ 转为 ‘地產代理’
21.‘保險佬’ 转为 ‘保險代理’
22.‘跛佬’ 转为 ‘傷殘人士’
</Word conversion rules>

2.如果用戶提問的詞語中包含錯別字，請按規則改正有錯別字的詞語
<typo correction>
1.‘蘭桂芳’ 改为 ‘蘭桂坊’
2.‘乾躁’ 改为 ‘乾燥’
3.‘燥底’ 改为 ‘躁底’
4.‘籍口’ 改为 ‘藉口’
5.‘國藉’ 改为 ‘國籍’
6.‘防衞’ 改为 ‘防衛’
7.‘衛生署’ ��为 ‘衞生署’
8.‘晒太陽’ 改为 ‘曬太陽’
9.‘多謝曬’ 改为 ‘多謝晒’
10.‘感歎’ 改为 ‘感嘆’
11.‘嘆世界’ 改为 ‘歎世界’
12.‘鬼崇’ 改为 ‘鬼祟’
13.‘祟高’ 改为 ‘崇高’
14.‘墮毀’ 改为 ‘墜毀’
15.‘墜落’ 改为 ‘墮落’
16.‘匯豐’ 改为 ‘滙豐’
17.‘聯係’ 改为 ‘聯繫’
18.‘關繫’ 改为 ‘關係’
19.‘學繫’ 改为 ‘學系’
20.‘惟一’ 改为 ‘唯一’
21.‘唯有’ 改为 ‘惟有’
22.‘熱辣辣’ 改为 ‘熱焫焫’
23.‘榴蓮’ 改为 ‘榴槤’
24.‘舖滿’ 改为 ‘鋪滿’
25.‘店鋪’ 改为 ‘店舖’
26.‘迫供’ 改为 ‘逼供’
27.‘強逼/被逼’ 改为 ‘   強迫/被迫’
28.‘恆生/恆地’ 改为 ‘   恒生/恒地’
29.‘恒常’       改为 ‘恆常’
</typo correction>

3、如果用戶的問題包含以下不合適的主題，請直接輸出“你的問題涉及不當用詞”
<inappropriate theme>
1.自殺
2.教唆他人��殺或說明
3.教唆他人犯罪或說明
4.關於傷害或自殘的說明
5.觸犯法律的行為
6.宣揚暴力行為
7.色情 (e.g. 賣淫)
8.性騷擾
9.仇限言論 (e.g. 種族歧視)
10.極端主義觀點
11.威脅言論
12.未經證實的醫療建議
13.詐騙資訊
14.粗口/低俗用詞 (屌你, 冚家剷, asshole, fuck, on9, slut, 鳩, 閪, 柒, 撚, 你老味, 仆街, 屎忽鬼,etc.)
15.粗口偕音 (on9, dklm, dllm, diu, etc.)
15.敏感的個人資料, 如身份証號碼, 電話等
16.販售或推廣管制商品 (e.g. 動物, 毒品藥物, 武器)
</inappropriate theme>

4、改寫規則不能反轉，如“蘭桂坊” 不能改爲 “蘭桂芳”
5、不需要前言,直接輸出改寫的問題
6、如果問題不涉及不當用詞,無需改寫，直接輸出"無需改寫"

</rewriting rules>

<examples>
<example>
input:鬼佬
output:外國人
</example>
<example>
input:摩羅差
output:印度人 / 巴基斯坦裔人士
</example>
<example>
input:呀叉
output:印度人 / 巴基斯坦裔人士
</example>
<example>
input:猶太豬
output:猶太人 / 猶太社群
</example>
<example>
input:阿拉伯豬
output:阿拉伯人 / 中東裔人士
</example>
<example>
input:港澳辦主任夏寶龍
output:無需改寫
</example>
</examples>

"""





# App title
st.set_page_config(page_title="aws intelligent recommendation solution")

with st.sidebar:
    st.title('AWS Intelligent Q&A Solution Guide')
    st.subheader('Models and parameters')
    
    #index_list = ['singtao_demo_1028','singtao_demo_1025_2']
    #index = st.radio('Please select a index',index_list)
    
    index = 'singtao_demo_1028'


    #language = st.radio("Please select a language",('chinese-tc', 'chinese', 'english'))
    language = 'chinese-tc'

    model_id_list = ['anthropic.claude-3-sonnet-20240229-v1:0','anthropic.claude-3-5-sonnet-20240620-v1:0','anthropic.claude-3-haiku-20240307-v1:0']
    model_id = st.radio("Please select text embedding sagemaker endpoint",model_id_list)
    
    vectorSearchNumber = st.slider("Search Number",min_value=1, max_value=10, value=3, step=1)
    #vectorScoreThresholds = st.slider("Vector Score Threshold",min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    vectorScoreThresholds = 0
    system_prompt = st.text_area("System Prompt",prompt_template,height=450)


st.write("## ST news related topics demo")


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
    st.session_state.prompt = ''

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
    st.session_state.prompt = ''
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


def generate_response(prompt):

    url = api + prompt
    print('url prompt:',prompt)

    url += ('&module=RAG')
    url += ('&sessionId='+st.session_state.sessionId)
    url += ('&requestType=http')
    url += ('&index='+index)
    url += '&language=chinese-tc'
    url += ('&requestType=http')
    url += ('&embeddingEndpoint='+cn_embedding_endpoint)


    print('model_id:',model_id)
    if len(model_id) > 0:
        url += ('&modelName='+model_id)
        #url += ('&modelType=bedrock')
        url += ('&maxTokens=2048')

        url += ('&modelType=bedrock_api')
        url += ('&apiUrl=https://apj2m6tzu9.execute-api.us-east-1.amazonaws.com/prod/')

    if len(reranker_endpoint)>0:
        url += ('&rerankerEndpoint='+reranker_endpoint)

    if len(system_prompt) > 0:
        url += ('&systemPrompt='+system_prompt)

    url += ('&searchMethod=vector')
    if vectorSearchNumber > 0:
        url += ('&vecTopK='+str(vectorSearchNumber))
    if float(vectorScoreThresholds) > 0:
        url += ('&vecDocsScoreThresholds='+str(vectorScoreThresholds))

    url += ('&responseIfNoDocsFound=找��到問題的答案，請試試其他問題吧!')

    
    print('url:',url)
    response = requests.get(url)
    result = response.text
    print('result:',result)
    result = json.loads(result)
    answer  = ''
    source_data = []
    rewrite_query = ''
    if 'text' in result.keys():
        answer = result['text']
        source_data = result['sourceData']
        rewrite_query = result['rewriteQuery']
    else:
        answer = result['message']
    #print('source_data:',source_data)
    return answer,source_data,rewrite_query



def news_search(prompt):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    body = {}
    body['query'] = prompt
    body['module'] = "SEARCH"
    body['isCheckedKnowledgeBase'] = False
    body['index'] = index
    body['rewritePrompt'] = rewrite_prompt
    body['embeddingEndpoint'] = cn_embedding_endpoint
    body['rerankerEndpoint'] = reranker_endpoint
    body['searchMethod'] = "mix"
    body['vecTopK'] = vectorSearchNumber
    body['txtTopK'] = vectorSearchNumber
    if vectorScoreThresholds > 0:
        body['vectorScoreThresholds'] = vectorScoreThresholds

    print('body:',body)
    response = requests.post(api,json=body,headers=headers)

    result = response.text
    print('result:',result)
    result = json.loads(result)

    source_data = []
    rewrite_query = ''
    if 'sourceData' in result.keys():
        source_data = result['sourceData']
    if 'rewriteQuery' in result.keys():
        rewrite_query = result['rewriteQuery']

    #print('source_data:',source_data)
    return source_data,rewrite_query

def generate_answer(prompt,relatedDocs):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    body = {}
    body['query'] = prompt
    body['module'] = "GENERATE"
    body['isCheckedKnowledgeBase'] = False
    body['relatedDocs'] = relatedDocs
    body['systemPrompt'] = system_prompt
    body['modelName'] = model_id
    body['maxTokens'] = 2048

    print('body:',body)
    response = requests.post(api,json=body,headers=headers)

    result = response.text
    print('result:',result)
    result = json.loads(result)

    answer = ''
    if 'answer' in result.keys():
        answer = result['answer']

    return answer


def send_and_receive_message(websocket_path: str, prompt: str, status_item: st.status):

    print('in the send and receive message')
    global LAST_REPLY

    body = {}
    body['query'] = prompt
    body['module'] = "GENERATE"
    body['isCheckedKnowledgeBase'] = False
    body['relatedDocs'] = relatedDocs
    body['systemPrompt'] = system_prompt
    body['modelName'] = model_id
    body['maxTokens'] = 2048

    message = json.dumps(body)
    ws = create_connection(websocket_path)
    LAST_REPLY = ""
    try:
        print('before sent')
        ws.send(message)
        print('after sent')

        while True:

            response = ws.recv()
            print('after response')
            try:
                parsed_response = json.loads(response)
                print('parsed_response:',parsed_response)
            except Exception as exc:
                raise Exception(f"Cannot parse message to json {response}") from exc

            if "message" in parsed_response:
                # Yield the response data if it matches a certain type
                if parsed_response["message"] == "streaming":
                    status_item.update(label="Generating answers")
                    LAST_REPLY += parsed_response["text"]
                    yield parsed_response["text"]
                elif parsed_response["message"] == "streaming_end":
                    status_item.update(label="Done", state="complete")
                    break  # Exit after receiving 'end_text'

    except WebSocketTimeoutException:
        status_item.update(label="Timeout", state="error")
        yield "Error: Receiving timed out."

    except Exception as e:
        status_item.update(label="Error", state="error")
        LAST_REPLY = f"Error: {str(e)}"
        yield f"Error: {str(e)}"
    finally:
        ws.close()



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
                #response,source_datas,rewrite_query = generate_response(prompt)
                #answer = ''
                #related = ''
                #if response.find('你的問題涉及不當用詞') <0:
                #    response_list = response.split('</answer>')
                #    print('response_list:',response_list)
                #    answer = response_list[0].replace('<answer>','')
                #    related = response_list[1].replace('<related>','').replace('</related>','')
                #else:
                #    answer = response

            
                source_datas,rewrite_query = news_search(prompt)
                response = rewrite_query
                st.write('Rewrite query: ' + rewrite_query)
                st.divider()

                #st.write(answer)
                #st.divider()

                relatedDocs = []
                for source_data in source_datas[:vectorSearchNumber]:
                    source_data = source_data['source']
                    if len(relatedDocs) == 0:
                        relatedDocs.append(source_data['description'])
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        image = source_data['thumbnail']
                        if len(image) > 0:
                            st.image(image)
                    with col2:
                        if 'url' in source_data.keys():
                            href = source_data['url']
                        title = source_data['sentence']
                        description = source_data['description']
                        if 'url' in source_data.keys():
                            href = source_data['url']
                            st.markdown('<a href="' + href +'"> ' + title + '</a>', unsafe_allow_html=True)
                        else:
                            st.markdown(title)
                        st.caption(description[:100]+'..')
    
                if len(relatedDocs) == 0:
                    response = "沒有相關新聞"
                    st.write(response)
    
                elif rewrite_query.find('你的問題涉及不當用詞') < 0: 
                    response = generate_answer(rewrite_query,relatedDocs)
                    
                    response_list = response.split('</answer>')
                    print('response_list:',response_list)
                    
                    answer = response_list[0].replace('<answer>','')
                    if len(answer) > 0:
                        st.write(answer)

                    related = ''
                    if len(response_list) > 1:
                        related = response_list[1].replace('<related>','').replace('</related>','')
               
                    if len(related) > 0:
                        st.divider()
                        related_list = related.split('\n')
                        for related_question in related_list:
                            if len(related_question) > 0:
                                st.write(related_question)
                        response = answer + str(related_list)

            #except:
            #    placeholder.markdown("Sorry,please try again!")
    

    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)