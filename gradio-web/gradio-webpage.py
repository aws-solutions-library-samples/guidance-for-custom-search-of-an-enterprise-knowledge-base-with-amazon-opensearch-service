import requests
import json
import gradio as gr
from datetime import datetime

#Fill in your configuration
invoke_url = ''
bedrock_url = ''

chinese_index = 'smart_search_qa_test'
english_index = 'smart_search_qa_test'

cn_embedding_endpoint = 'huggingface-inference-eb'
cn_llm_endpoint = 'pytorch-inference-llm-v1'

en_embedding_endpoint = 'huggingface-inference-eb'
en_llm_endpoint = 'pytorch-inference-llm-v1'

llama2_llm_endpoint = ''

responseIfNoDocsFound = ''

#Modify the default prompt as needed
chinese_prompt = """基于以下已知信息，简洁和专业的来回答用户的问题，并告知是依据哪些信息来进行回答的。
   如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    
            问题: {question}
            =========
            {context}
            =========
            答案:"""

english_prompt = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
{context}

Question: {question}
Answer:"""                                


chinses_summarize_prompt="""请根据访客与客服的通话记录，写一段访客提出问题的摘要，突出显示与亚马逊云服务相关的要点, 摘要不需要有客服的相关内容:
{text}

摘要是:"""

english_summarize_prompt="""Based on the call records between the visitor and the customer service, write a summary of the visitor's questions, highlighting the key points related to Amazon Web Services, and the summary does not need to have customer service-related content:
{text}

The summary is:"""

claude_chat_prompt_cn="""
Human: 请根据 {history}，回答：{human_input}

Assistant:
"""

claude_chat_prompt_cn_tc="""
Human: 請根據 {history}，使用繁體中文回答：{human_input}

Assistant:
"""

claude_chat_prompt_english="""
Human: Based on {history}, answer the question：{human_input}

Assistant:
"""



claude_rag_prompt_cn = """
Human: 基于以下已知信息，简洁和专业的来回答用户的问题，如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    
            问题: {question}
            =========
            {context}
            =========
            Assistant:
"""

claude_rag_prompt_cn_tc = """
Human: 基於以下已知信息，簡潔和專業的來回答用戶的問題，如果無法從中得到答案，請說 "根據已知信息無法回答該問題" 或 "沒有提供足夠的相關信息"，不允許在答案中添加編造成分，答案請使用繁體中文回答
    
            問題: {question}
            =========
            {context}
            =========
            Assistant:
"""

claude_rag_prompt_english = """
Human: Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
{context}

Question: {question}
Assistant:
"""

api = invoke_url + '/langchain_processor_qa?query='
bedrock_url += '/bedrock?'

def get_answer(task_type,question,sessionId,language,modelType,prompt,searchEngine,index,searchMethod,vecTopK,txtTopK,vecDocsScoreThresholds,txtDocsScoreThresholds,score_type_checklist):
    
    question=question.replace('AWS','亚马逊云科技').replace('aws','亚马逊云科技').replace('Aws','亚马逊云科技')
    print('question:',question)

    if len(question) > 0:
        url = api + question
    else:
        url = api + "hello"
    
    url += '&requestType=https'
    #task type: qa,chat
    if task_type == "Knowledge base Q&A":
        task = 'qa'
    else:
        task = 'chat'
    url += ('&task='+task)
    
    if len(responseIfNoDocsFound) > 0:
        url += ('&responseIfNoDocsFound='+responseIfNoDocsFound)

    if language == "english":
        url += '&language=english'
        url += ('&embeddingEndpoint='+en_embedding_endpoint)
        if modelType == "llama2(english)":
            url += ('&sagemakerEndpoint='+llama2_llm_endpoint)
        else:
            url += ('&sagemakerEndpoint='+en_llm_endpoint)
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        url += ('&sagemakerEndpoint='+cn_llm_endpoint)
     
    elif language == "chinese-tc":
        url += '&language=chinese-tc'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        url += ('&sagemakerEndpoint='+cn_llm_endpoint)
    
    if len(sessionId) > 0:
        url += ('&sessionId='+sessionId)
    
    if modelType == "claude2_api":
        url += ('&modelType=bedrock_api')
        url += ('&urlOrApiKey='+bedrock_url)
        url += ('&modelName=anthropic.claude-v2')
    elif modelType == "claude2":
        url += ('&modelType=bedrock')
        url += ('&modelName=anthropic.claude-v2')
    elif modelType == "llama2(english)":
        url += ('&modelType=llama2')

    if len(prompt) > 0:
        url += ('&prompt='+prompt)
    elif modelType == "claude2":
        if task_type == "Knowledge base Q&A":
            if language == "english":
                url += ('&prompt='+claude_rag_prompt_english)
            elif language == "chinese":
                url += ('&prompt='+claude_rag_prompt_cn)
            elif language == "chinese-tc":
                url += ('&prompt='+claude_rag_prompt_cn_tc)
        else:
            if language == "english":
                url += ('&prompt='+claude_chat_prompt_english)
            elif language == "chinese":
                url += ('&prompt='+claude_chat_prompt_cn)
            elif language == "chinese-tc":
                url += ('&prompt='+claude_chat_prompt_cn_tc)

    if searchEngine == "OpenSearch":
        url += ('&searchEngine=opensearch')
        if len(index) > 0:
            url += ('&index='+index)
        else:
            if language.find("chinese") >= 0 and len(chinese_index) >0:
                url += ('&index='+chinese_index)
            elif language == "english" and len(english_index) >0:
                url += ('&index='+english_index)

    elif searchEngine == "Kendra":
        url += ('&searchEngine=kendra')
        if len(index) > 0:
            url += ('&kendraIndexName='+index)

    elif searchEngine == "Zilliz":
        url += ('&searchEngine=zilliz')

    if int(vecTopK) > 0:
        url += ('&topK='+str(vecTopK))

    url += ('&searchMethod='+searchMethod)

    if int(txtTopK) > 0:
        url += ('&txtDocsNum='+str(txtTopK))

    if float(vecDocsScoreThresholds) > 0:
        url += ('&vecDocsScoreThresholds='+str(vecDocsScoreThresholds))

    if float(txtDocsScoreThresholds) > 0:
        url += ('&txtDocsScoreThresholds='+str(txtDocsScoreThresholds))

    for score_type in score_type_checklist:
        if score_type == "query_answer_score":
            url += ('&isCheckedScoreQA=true')
        elif score_type == "answer_docs_score":
            url += ('&isCheckedScoreAD=true')

    print("url:",url)

    now1 = datetime.now()#begin time
    response = requests.get(url)
    now2 = datetime.now()#endtime
    request_time = now2-now1
    print("request takes time:",request_time)

    result = response.text
    print('result0:',result)
    
    result = json.loads(result)
    print('result:',result)
    
    answer = result['text']
    source_list = []
    if 'sourceData' in result.keys():
        source_list = result['sourceData']
    
    print("answer:",answer)
    print('source_list:',source_list)

    source_str = ""
    query_docs_score_list = []
    answer_docs_score_list = []
    for i in range(len(source_list)):
        item = source_list[i]
        print('item:',item)
        _id = "num:" + str(item['id'])
        try:
            source = ''
            if 'source' in item.keys():
                source = "source:" + item['source']
            elif 'title' in item.keys():
                source = "source:" + item['title']
        except KeyError:
            source ="source:unknown"
            print("KeyError:source file not found")
        qd_score = "qd score:" + str(item['scoreQueryDoc'])
        query_docs_score_list.append(item['scoreQueryDoc'])

        ad_score = "ad score:" + str(item['scoreAnswerDoc'])
        answer_docs_score_list.append(item['scoreAnswerDoc'])

        sentence = "sentence:" + item['sentence']
        paragraph = "paragraph:" + item['paragraph']

        source_str += (_id + "      " + source + "      " + qd_score + '\n')
        # source_str += sentence + '\n'
        source_str += paragraph + '\n\n'
    
    confidence = ""
    if len(list(query_docs_score_list)) > 0 and float(query_docs_score_list[0]) > 0:
        confidence += ("query_docs_score:" + str(query_docs_score_list) + '\n')

    query_answer_score = -1
    if 'scoreQueryAnswer' in result.keys():
        query_answer_score =  float(result['scoreQueryAnswer'])
    if query_answer_score >= 0:
        confidence += ("query_answer_score:" + str(query_answer_score) + '\n')

    answer_docs_score = -1
    if len(list(answer_docs_score_list)) > 0 and float(answer_docs_score_list[0]) > 0:
        confidence += ("answer_docs_score:" + str(answer_docs_score_list) + '\n')

    return answer,confidence,source_str,url,request_time
    
    
def get_summarize(texts,language,modelType,prompt):

    url = api + texts
    url += '&task=summarize'
    url += '&requestType=https'

    if language == "english":
        url += '&language=english'
        url += ('&embeddingEndpoint='+en_embedding_endpoint)
        url += ('&sagemakerEndpoint='+en_llm_endpoint)
        
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embeddingEndpoint='+cn_embedding_endpoint)
        url += ('&sagemakerEndpoint='+cn_llm_endpoint)

    if modelType == "claude2":
        url += ('&modelType=bedrock')
        url += ('&urlOrApiKey='+bedrock_url)
        url += ('&modelName=anthropic.claude-v2')

    if len(prompt) > 0:
        url += ('&prompt='+prompt)
    else:
        if language == "english":
            url += ('&prompt='+english_summarize_prompt)
        elif language == "chinese":
            url += ('&prompt='+chinses_summarize_prompt)
    
    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print('result1:',result)
    
    answer = result['summarize']

    return answer

demo = gr.Blocks(title="AWS Intelligent Q&A Solution Guide")
with demo:
    gr.Markdown(
        "# <center>AWS Intelligent Q&A Solution Guide"
    )

    with gr.Tabs():
        with gr.TabItem("Question Answering"):

            with gr.Row():
                with gr.Column():
                    qa_task_radio = gr.Radio(["Knowledge base Q&A","Chat"],value="Knowledge base Q&A",label="Task")
                    query_textbox = gr.Textbox(label="Query")
                    sessionId_textbox = gr.Textbox(label="Session ID")
                    qa_button = gr.Button("Summit")

                    qa_language_radio = gr.Radio(["chinese","chinese-tc", "english"],value="chinese",label="Language")
                    qa_modelType_radio = gr.Radio(["claude2","claude2_api", "llama2(english)","other"],value="other",label="Model type")
                    qa_prompt_textbox = gr.Textbox(label="Prompt( must include {context} and {question} )",placeholder=chinese_prompt,lines=2)
                    qa_searchEngine_radio = gr.Radio(["OpenSearch","Kendra","Zilliz"],value="OpenSearch",label="Search engine")
                    qa_index_textbox = gr.Textbox(label="OpenSearch index OR Kendra index id")
                    # qa_em_ep_textbox = gr.Textbox(label="Embedding Endpoint")
                    
                    search_method_radio = gr.Radio(["vector","text","mix"],value="vector",label="Search Method")
                    vec_topK_slider = gr.Slider(label="The number of related documents by vector search",value=1, minimum=1, maximum=10, step=1)
                    txt_topK_slider = gr.Slider(label="The number of related documents by text search",value=1, minimum=1, maximum=10, step=1)
                    vec_score_thresholds_radio = gr.Slider(label="Vector search score thresholds",value=0.01, minimum=0.01, maximum=1, step=0.01)
                    txt_score_thresholds_radio = gr.Slider(label="Text search score thresholds",value=0.01, minimum=0.01, maximum=1, step=0.01)

                    # qa_temperature_slider = gr.Slider(label="Temperature parameter of LLM",value=0.01, minimum=0.01, maximum=1, step=0.01)
                    score_type_checklist = gr.CheckboxGroup(["query_answer_score", "answer_docs_score"],value=["query_answer_score"],label="Confidence score type")

                with gr.Column():
                    qa_output = [gr.outputs.Textbox(label="Answer"), gr.outputs.Textbox(label="Confidence"), gr.outputs.Textbox(label="Source"), gr.outputs.Textbox(label="Url"), gr.outputs.Textbox(label="Request time")]
                                

        with gr.TabItem("Summarize"):
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(label="Input texts",lines=4)
                    summarize_button = gr.Button("Summit")
                    sm_language_radio = gr.Radio(["chinese", "english"],value="chinese",label="Language")
                    sm_modelType_radio = gr.Radio(["claude2","other"],value="other",label="Model type")
                    sm_prompt_textbox = gr.Textbox(label="Prompt",lines=4, placeholder=chinses_summarize_prompt)
                with gr.Column():
                    text_output = gr.Textbox()
            
    qa_button.click(get_answer, inputs=[qa_task_radio,query_textbox,sessionId_textbox,qa_language_radio,qa_modelType_radio,qa_prompt_textbox,qa_searchEngine_radio,qa_index_textbox,\
        search_method_radio,vec_topK_slider,txt_topK_slider,vec_score_thresholds_radio,txt_score_thresholds_radio,score_type_checklist], outputs=qa_output)
    summarize_button.click(get_summarize, inputs=[text_input,sm_language_radio,sm_modelType_radio,sm_prompt_textbox], outputs=text_output)

# demo.launch()
demo.launch(share=True)
