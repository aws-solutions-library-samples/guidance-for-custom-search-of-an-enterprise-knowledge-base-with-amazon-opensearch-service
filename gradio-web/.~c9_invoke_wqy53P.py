import requests
import json
import gradio as gr
from datetime import datetime

#Fill in your correct configuration
invoke_url = 'https://pocflul6r4.execute-api.us-west-1.amazonaws.com/prod'
bedrock_url = 'https://bx2kc13ys3.execute-api.us-east-1.amazonaws.com/prod/bedrock?'

chinese_index = 'smart_search_qa_test'
english_index = 'smart_search_qa_test_0826_en_3'

cn_embedding_endpoint = 'huggingface-inference-eb'
cn_llm_endpoint = 'pytorch-inference-llm-v1'
en_embedding_endpoint = 'huggingface-inference-eb-bge-en'
en_llm_endpoint = ''


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



api = invoke_url + '/langchain_processor_qa?query='

def get_answer(task_type,question,session_id,language,model_type,prompt,search_engine,index,top_k,temperature,score_type_checklist):
    
    if len(question) > 0:
        url = api + question
    else:
        url = api + "hello"

    #task type: qa,chat
    if task_type == "Knowledge base Q&A":
        task = 'qa'
    else:
        task = 'chat'
    url += ('&task='+task)

    if language == "english":
        url += '&language=english'
        url += ('&embedding_endpoint_name='+en_embedding_endpoint)
        url += ('&llm_embedding_name='+en_llm_endpoint)
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embedding_endpoint_name='+cn_embedding_endpoint)
        url += ('&llm_embedding_name='+cn_llm_endpoint)
     
    elif language == "chinese-tc":
        url += '&language=chinese-tc'
        url += ('&embedding_endpoint_name='+cn_embedding_endpoint)
        url += ('&llm_embedding_name='+cn_llm_endpoint)
    
    if len(session_id) > 0:
        url += ('&session_id='+session_id)
    
    if model_type == "claude2":
        url += ('&model_type=bedrock')
        url += ('&bedrock_api_url='+bedrock_url)
        url += ('&bedrock_model_id=anthropic.claude-v2')
    elif model_type == "titan(english)":
        url += ('&model_type=bedrock')
        url += ('&bedrock_api_url='+bedrock_url)
        url += ('&bedrock_model_id=amazon.titan-tg1-large')
    elif model_type == "llama2(english)":
        url += ('&model_type=llama2')

    if len(prompt) > 0:
        url += ('&prompt='+prompt)

    if search_engine == "OpenSearch":
        url += ('&search_engine=opensearch')
        if len(index) > 0:
            url += ('&index='+index)
        else:
            if language.find("chinese") >= 0 and len(chinese_index) >0:
                url += ('&index='+chinese_index)
            elif language == "english" and len(english_index) >0:
                url += ('&index='+english_index)
    elif search_engine == "Kendra":
        url += ('&search_engine=kendra')
        if len(index) > 0:
            url += ('&kendra_index_id='+index)

    if int(top_k) > 0:
        url += ('&top_k='+str(top_k))

    if float(temperature) > 0.01:
        url += ('&temperature='+str(temperature))

    for score_type in score_type_checklist:
        url += ('&cal_' + score_type +'=true')

    print("url:",url)

    now1 = datetime.now()#begin time
    response = requests.get(url)
    now2 = datetime.now()#endtime
    request_time = now2-now1
    print("request takes time:",request_time)

    result = response.text
    
    result = json.loads(result)
    print('result:',result)
    
    answer = result['suggestion_answer']
    source_list = []
    if 'source_list' in result.keys():
        source_list = result['source_list']
    
    print("answer:",answer)

    source_str = ""
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
        query_answer_score =  float(result['query_answer_score'])
        score = "score:" + str(item['score'])
        sentence = "sentence:" + item['sentence']
        paragraph = "paragraph:" + item['paragraph']
        source_str += (_id + "      " + source + "      " + score + '\n')
        # source_str += sentence + '\n'
        source_str += paragraph + '\n\n'
    
    confidence = ""
    query_docs_score = -1
    if 'query_docs_score' in result.keys():
        query_docs_score =  float(result['query_docs_score'])
    if query_docs_score >= 0:
        confidence += ("query_docs_score:" + str(query_docs_score) + '\n')

    query_answer_score = -1
    if 'query_answer_score' in result.keys():
        query_answer_score =  float(result['query_answer_score'])
    if query_answer_score >= 0:
        confidence += ("query_answer_score:" + str(query_answer_score) + '\n')

    answer_docs_score = -1
    if 'answer_docs_score' in result.keys():
        answer_docs_score =  float(result['answer_docs_score'])
    if answer_docs_score >= 0:
        confidence += ("answer_docs_score:" + str(answer_docs_score) + '\n')

    docs_list_overlap_score = -1
    if 'docs_list_overlap_score' in result.keys():
        docs_list_overlap_score =  float(result['docs_list_overlap_score'])
    if docs_list_overlap_score >= 0:
        confidence += ("docs_list_overlap_score:" + str(docs_list_overlap_score) + '\n')


    return answer,confidence,source_str,url,request_time
    
    
def get_summarize(texts,language,prompt):

    url = api + texts
    url += '&task=summarize'

    if language == "english":
        url += '&language=english'
        url += ('&embedding_endpoint_name='+en_embedding_endpoint)
        url += ('&llm_embedding_name='+en_llm_endpoint)
        
    elif language == "chinese":
        url += '&language=chinese'
        url += ('&embedding_endpoint_name='+cn_embedding_endpoint)
        url += ('&llm_embedding_name='+cn_llm_endpoint)

    
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

    # if language == 'english' and answer.find('The Question and Answer are:') > 0:
    #     answer=answer.split('The Question and Answer are:')[-1].strip()

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
                    session_id_textbox = gr.Textbox(label="Session ID")
                    qa_button = gr.Button("Summit")

                    qa_language_radio = gr.Radio(["chinese","chinese-tc", "english"],value="chinese",label="Language")
                    qa_model_type_radio = gr.Radio(["claude2","titan(english)", "llama2(english)","other"],value="other",label="Model type")
                    qa_prompt_textbox = gr.Textbox(label="Prompt( must include {context} and {question} )",placeholder=chinese_prompt,lines=2)
                    qa_search_engine_radio = gr.Radio(["OpenSearch","Kendra"],value="OpenSearch",label="Search engine")
                    qa_index_textbox = gr.Textbox(label="OpenSearch index OR Kendra index id")
                    qa_top_k_slider = gr.Slider(label="Top_k of source text to LLM",value=1, minimum=1, maximum=20, step=1)
                    qa_temperature_slider = gr.Slider(label="Temperature parameter of LLM",value=0.01, minimum=0.01, maximum=1, step=0.01)
                    score_type_checklist = gr.CheckboxGroup(["query_answer_score", "answer_docs_score","docs_list_overlap_score"],value=["query_answer_score"],label="Confidence score type")

                with gr.Column():
                    qa_output = [gr.outputs.Textbox(label="Answer"), gr.outputs.Textbox(label="Confidence"), gr.outputs.Textbox(label="Source"), gr.outputs.Textbox(label="Url"), gr.outputs.Textbox(label="Request time")]
                                

        with gr.TabItem("Summarize"):
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(label="Input texts",lines=4)
                    summarize_button = gr.Button("Summit")
                    sm_language_radio = gr.Radio(["chinese", "english"],value="chinese",label="Language")
                    sm_prompt_textbox = gr.Textbox(label="Prompt",lines=4, placeholder=chinses_summarize_prompt)
                with gr.Column():
                    text_output = gr.Textbox()
            
    qa_button.click(get_answer, inputs=[qa_task_radio,query_textbox,session_id_textbox,qa_language_radio,qa_model_type_radio,qa_prompt_textbox,qa_search_engine_radio,qa_index_textbox,qa_top_k_slider,qa_temperature_slider,score_type_checklist], outputs=qa_output)
    summarize_button.click(get_summarize, inputs=[text_input,sm_language_radio,sm_prompt_textbox], outputs=text_output)

# demo.launch()
demo.launch(share=True)
