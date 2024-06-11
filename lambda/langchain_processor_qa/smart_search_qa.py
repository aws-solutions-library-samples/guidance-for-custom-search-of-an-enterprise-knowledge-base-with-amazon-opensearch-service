import os
import shutil
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import AmazonKendraRetriever
from langchain.prompts.prompt import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain
# from langchain.llms import AmazonAPIGateway
from amazon_api_gateway import AmazonAPIGateway
import json
import numpy as np
from model import *
from session import *
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class SmartSearchQA:

    def init_cfg(self,
             opensearch_index_name,
             opensearch_user_name,
             opensearch_user_password,
             opensearch_or_kendra_host,
             opensearch_port,
             region,
             zilliz_endpoint,
             zilliz_token,
             embedding_endpoint_name: str = 'huggingface-inference-eb',
             llm_endpoint_name: str = 'pytorch-inference-llm-v1',
             temperature: float = 0.01,
             language: str = "chinese",
             search_engine: str = "opensearch",
             model_type:str = "normal",
             api_url:str = "",
             model_name:str="anthropic.claude-v2",
             api_key:str = "",
             secret_key:str = "",
             max_tokens:int=512,
             streaming:bool=True,
             callbackHandler: StreamingStdOutCallbackHandler = StreamingStdOutCallbackHandler()
                ):
        self.language = language
        self.search_engine = search_engine
        self.embedding_type = 'bedrock' if (embedding_endpoint_name.find('amazon.titan') >=0 or embedding_endpoint_name.find('cohere.embed') >= 0) else 'sagemaker'

        #add aos parmeter
        self.aos_index = opensearch_index_name
        self.aos_username = opensearch_user_name
        self.aos_passwd = opensearch_user_password
        self.aos_host = opensearch_or_kendra_host
        self.aos_port = opensearch_port
        #when streaming output, this llm should be different from self.llm
        self.condense_question_llm=None

        printTime("before init llm")
        #init LLM
        if model_type == "llama2":
            self.llm = init_model_llama2(llm_endpoint_name,region,temperature)
        elif model_type == "bedrock_api":
            self.llm = AmazonAPIGateway(api_url=api_url)
            parameters={
                "modelId":model_name,
                "temperature":temperature,
                "max_tokens":max_tokens
            }       
            self.llm.model_kwargs = parameters
        elif model_type == "bedrock":
            if streaming:
                self.llm = init_model_bedrock_withstreaming(model_name,callbackHandler)
                self.condense_question_llm=init_model_bedrock(model_name)
            else:
                self.llm = init_model_bedrock(model_name)
            parameters={
                "temperature":temperature,
                "max_tokens":max_tokens
            }
            self.llm.model_kwargs = parameters
        elif model_type == 'llm_api':
            if model_name.find('Baichuan2') >= 0:
                self.llm = AmazonAPIGateway(api_url=api_url)
                parameters={
                    "modelId":model_name,
                    "api_key":api_key,
                    "secret_key":secret_key,
                }
                self.llm.model_kwargs = parameters
            elif model_name.find('chatglm') >= 0:
                self.llm = AmazonAPIGateway(api_url='')
                parameters={
                    "modelId":model_name,
                    "api_key":api_key,
                }
                self.llm.model_kwargs = parameters
        else:
            if streaming:
                self.llm = init_model_withstreaming(llm_endpoint_name,region,temperature=temperature,callbackHandler=callbackHandler)
                self.condense_question_llm=init_model(llm_endpoint_name,region,temperature)
            else:
                self.llm = init_model(llm_endpoint_name,region,temperature)

        printTime("before init embedding")
        #init embedding model
        if self.search_engine != "kendra":
            if self.embedding_type == 'sagemaker':
                self.embeddings = init_embeddings(embedding_endpoint_name, region, self.language)
            elif self.embedding_type == 'bedrock':
                self.embeddings = init_embeddings_bedrock(embedding_endpoint_name)

        printTime("before init vector store")
        #init vector store
        if self.search_engine == "opensearch":
            print("init opensearch vector store")
            self.vector_store = init_vector_store(self.embeddings,
                                                  opensearch_index_name,
                                                  opensearch_or_kendra_host,
                                                  opensearch_port,
                                                  opensearch_user_name,
                                                  opensearch_user_password)
        elif self.search_engine == "kendra":
            self.vector_store = None
            self.kendra_host = opensearch_or_kendra_host
        elif self.search_engine == 'zilliz':
            print("init zilliz vector store")
            self.vector_store = init_zilliz_vector_store(self.embeddings,
                                                         zilliz_endpoint,
                                                         zilliz_token)
    def get_qa_relation_score(self,query,answer):
        
        if self.embedding_type == 'bedrock':
            query_answer_emb = np.array(self.embeddings.embed_documents([query,answer]))
        else:
            query_answer_emb = np.array(self.embeddings._embedding_func([query,answer]))
        query_emb = query_answer_emb[0]
        answer_emb = query_answer_emb[1]
        dot = query_emb * answer_emb 
        query_emb_len = np.linalg.norm(query_emb)
        answer_emb_len = np.linalg.norm(answer_emb)
        cos = dot.sum()/(query_emb_len * answer_emb_len)
        return cos

    def get_summarize(self,texts,
                        chain_type: str = "stuff",
                        prompt_template: str = "请根据{text}，总结一段摘要",
                        combine_prompt_template: str = "请根据{text}，总结一段摘要"
                        ):
                            
        texts = texts.split(';')
        texts_len = len(texts)
        print("texts len:",texts_len)
        
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
        COMBINE_PROMPT = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
        
        print('prompt:',PROMPT)
        
        if chain_type == "stuff":
            docs = [Document(page_content=t) for t in texts]
            chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=PROMPT)
            result = chain.run(docs)
            
        else:
            new_texts = []
            num = 20
            for i in range(0,texts_len,num):
                if i + num < texts_len:
                    end = i + num
                else:
                    end = texts_len - i
                if len(texts[i:end]) > 0:
                    new_texts.append(";".join(texts[i:end]))
            docs = [Document(page_content=t) for t in new_texts]
            
            chain = load_summarize_chain(self.llm, 
                                         chain_type=chain_type, 
                                         map_prompt=PROMPT,
                                         combine_prompt=COMBINE_PROMPT)
            result = chain({"input_documents": docs}, return_only_outputs=True)
            result = result['output_text']
        
        return result

    def get_chat(self,query,language,prompt_template,table_name,session_id,model_type):
            
        prompt = PromptTemplate(
            input_variables=["history", "human_input"], 
            template=prompt_template
        )
        
        memory = ConversationBufferMemory(return_messages=True)
        session_info = ""
        if len(session_id) > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "chat":
                        memory.chat_memory.add_user_message(item[0])
                        memory.chat_memory.add_ai_message(item[1])
            
        chat_chain = LLMChain(
            llm=self.llm,
            prompt=prompt, 
            # verbose=True, 
            memory=memory,
        )
            
        output = chat_chain.predict(human_input=query)

        if len(session_id) > 0:
            update_session_info(table_name, session_id, query, output, "chat")
        
        return output
    
    def get_retriever(self,top_k,
                           search_method: str="vector",
                           txt_docs_num: int=0,
                           vec_docs_score_thresholds: float=0,
                           txt_docs_score_thresholds: float=0,
                           text_field: str="text",
                           vector_field: str="vector_field",
                           image_field: str="image_base64",
                           work_mode: str="text-modal"
                     ):
        
        if self.search_engine == "opensearch":
            retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k,
                                                                      "search_method":search_method,
                                                                      "txt_docs_num":txt_docs_num,
                                                                      "vec_docs_score_thresholds":vec_docs_score_thresholds,
                                                                      "txt_docs_score_thresholds":txt_docs_score_thresholds,
                                                                      "text_field":text_field,
                                                                      "vector_field":vector_field,
                                                                      "embedding_type":self.embedding_type,
                                                                      "image_field":image_field,
                                                                      "work_mode":work_mode
                                                                      }
                                                       )
        elif self.search_engine == "kendra":
            retriever = AmazonKendraRetriever(index_id=self.kendra_host,top_k=top_k)
        elif self.search_engine == "zilliz":
            retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k,
                                                                      "search_method":search_method,
                                                                      "txt_docs_num":txt_docs_num,
                                                                      "vec_docs_score_thresholds":vec_docs_score_thresholds,
                                                                      "txt_docs_score_thresholds":txt_docs_score_thresholds,
                                                                      "text_field":text_field,
                                                                      "vector_field":vector_field,
                                                                      "embedding_type":self.embedding_type,
                                                                      "image_field":image_field,
                                                                      "work_mode":work_mode
                                                                      }
                                                       )
            
        return retriever
         

    def get_answer_from_conversational(self,query,
                                        session_id: str='',
                                        table_name: str='',
                                        language: str='chinese',
                                        prompt_template: str = "请根据{context}，回答{question}",
                                        condense_question_prompt: str="",
                                        top_k: int = 3,
                                        chain_type: str="stuff",
                                        search_method: str="vector",
                                        txt_docs_num: int=0,
                                        response_if_no_docs_found: str="",
                                        vec_docs_score_thresholds: float =0,
                                        txt_docs_score_thresholds: float =0,
                                        contextRounds: int = 3,
                                        text_field: str="text",
                                        vector_field: str="vector_field",
                                        ):
        
        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])
        combine_docs_chain_kwargs={"prompt":prompt}
        printTime("get_answer_from_conversational enter")
        
        history = []
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0 and contextRounds > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                session_info = session_info[-contextRounds:]
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "qa":
                        history.append((item[0],item[1]))
        
        print('history:',history)
        if len(history) > 0:
            self.llm.model_kwargs['history'] = history
        
        retriever = self.get_retriever(top_k,search_method,txt_docs_num,vec_docs_score_thresholds,txt_docs_score_thresholds,text_field,vector_field)
        
        ConversationalRetrievalChain._call = new_conversational_call
        printTime("get_answer_from_conversational before from llm")
        chain = ConversationalRetrievalChain.from_llm(
                    llm = self.llm,
                    condense_question_llm=self.condense_question_llm or self.llm,
                    chain_type=chain_type,
                    retriever=retriever,
                    condense_question_prompt = condense_question_prompt,
                    combine_docs_chain_kwargs = combine_docs_chain_kwargs,
                    return_source_documents = True,
                    return_generated_question = True,
                    response_if_no_docs_found = response_if_no_docs_found
                )
        printTime("get_answer_from_conversational before chain()")
        
#         result = chain({"question": query, "chat_history": history})
        result = chain({
            "question": query, 
            "chat_history": history,
            "search_engine": self.search_engine
        })

        
        answer=result['answer']
        
        # print('answer:',answer)
        # print('response_if_no_docs_found:',response_if_no_docs_found)
        # if answer == response_if_no_docs_found:
        #     vec_docs_score_thresholds = 0
        #     txt_docs_score_thresholds = 0
        #     retriever = self.get_retriever(top_k,search_method,txt_docs_num,vec_docs_score_thresholds,txt_docs_score_thresholds,text_field,vector_field)
        #     docs = retriever.get_relevant_documents(query)
        #     print('docs:',docs)
        #     if len(docs) > 0:
        #         answer = '找不到这个问题的答案，您可以问以下问题：'
        #         title_set = set()
        #         for doc in docs:
        #             title = doc[0].metadata['sentence']
        #             if title.find('标题') >=0 and title.find('内容') >=0:
        #                 title = title.split(':')[1][:-3]
        #             elif title.find('标题') >=0:
        #                 title = title.split(':')[1]
        #             title_set.add(title.strip())
        #         for title in iter(title_set):
        #             answer += ('\n' + title)
        #     print('new answer:',answer)
        #     result['answer'] = answer

        if len(session_id) > 0:
            new_query=result['generated_question']
            update_session_info(table_name, session_id, new_query, answer, "qa")
        
        return result

    def get_answer_from_conversational_llama2(self,query,
                                        session_id: str='',
                                        table_name: str='',
                                        prompt_template: str = "",
                                        condense_question_prompt: str="",
                                        top_k: int = 3,
                                        search_method: str="vector",
                                        txt_docs_num: int=0,
                                        response_if_no_docs_found: str="",
                                        vec_docs_score_thresholds: float =0,
                                        txt_docs_score_thresholds: float =0,
                                        contextRounds: int = 3,
                                        text_field: str="text",
                                        vector_field: str="vector_field",
                                        ):
        history = []
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0 and contextRounds > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                session_info = session_info[-contextRounds:]
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "qa":
                        history.append((string_processor(item[0]),string_processor(item[1])))
        
        print('history:',history)
        
        new_question = string_processor(query)
        if len(history) > 0:
            for question,answer in history:
                condense_question_prompt += ('user:'+question+';')
                condense_question_prompt += ('assistant:'+answer+';')
        
            print('condense_question_prompt:',condense_question_prompt)
            
            query_trans = 'convert this question to be a standalone question:'+string_processor(query)
            prompt={'system_content':string_processor(condense_question_prompt),'query':string_processor(query_trans)}
            prompt_str = json.dumps(prompt)
            print('question trans system prompt',prompt_str)
            new_question_response = self.llm.predict(prompt_str)
            new_question = string_processor(new_question_response)
            print('new_question:',new_question)
        
        retriever = self.get_retriever(top_k,search_method,txt_docs_num,vec_docs_score_thresholds,txt_docs_score_thresholds,text_field,vector_field)
        docs_with_scores = retriever.get_relevant_documents(new_question)

        if len(docs_with_scores) == 0:
            answer = response_if_no_docs_found
        else:
            print('docs_with_scores:',docs_with_scores)
            if self.search_engine == "kendra":
                docs = docs_with_scores
            else:
                docs = [doc[0] for doc in docs_with_scores]
            relate_docs=''
            for i in range(len(docs)):
                page_content = string_processor(docs[i].page_content)
                if len(page_content) > 0:
                    relate_docs += (page_content + ';')
            
            prompt_template += relate_docs
            prompt={'system_content':string_processor(prompt_template),'history':history,'query':new_question}
            prompt_str = json.dumps(prompt)
            print('qa system prompt',prompt_str)
            answer = self.llm.predict(prompt_str)
        
        if len(session_id) > 0:
            update_session_info(table_name, session_id, new_question, string_processor(answer), "qa")
        
        response = {'answer':answer,'source_documents':docs_with_scores}
        return response

    def get_answer_from_chat_llama2(self,query,
                                    prompt_template: str = "",
                                    table_name: str='',
                                    session_id: str=''
                                    ):
        history = []
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "chat":
                        history.append((string_processor(item[0]),string_processor(item[1])))
        
        print('history:',history)
        
        prompt={'system_content':string_processor(prompt_template),'history':history,'query':string_processor(query)}
        prompt_str = json.dumps(prompt)
        print('chat system prompt',prompt_str)
        answer = self.llm.predict(prompt_str)
        
        if len(session_id) > 0:
            update_session_info(table_name, session_id, query, string_processor(answer), "chat")
        
        return answer

    def get_answer_from_multimodel(self,query,
                                        question: list=[],
                                        task: str='qa',
                                        isCheckedKnowledgeBase: bool=True,
                                        system_prompt: str='',
                                        session_id: str='',
                                        table_name: str='',
                                        top_k: int = 3,
                                        search_method: str="vector",
                                        txt_docs_num: int=0,
                                        response_if_no_docs_found: str="can't find the answer",
                                        vec_docs_score_thresholds: float =0,
                                        txt_docs_score_thresholds: float =0,
                                        context_rounds: int = 3,
                                        text_field: str="text",
                                        vector_field: str="vector_field",
                                        image_field: str="image_base64",
                                        ):

        self.llm.model_kwargs['language'] = self.language
        if len(system_prompt) > 0:
            self.llm.model_kwargs['system'] = system_prompt
        
        input_docs = []
        for item in question:
            input_doc = {}
            #item = json.loads(item)
            input_type = ''
            if 'type' in item.keys():
                input_type = item['type']
            if input_type == 'text':
                input_doc['text'] = item['text']
            elif input_type == 'image':
                input_doc['image'] =  item['base64']
            if len(input_doc) > 0:
                input_docs.append(input_doc)
        print('input_docs:',input_docs)
        if len(input_docs) > 0:
            self.llm.model_kwargs['input_docs'] = input_docs
        
        history_str = ''
        session_info = ""
        if len(session_id) > 0 and len(table_name) > 0 and context_rounds > 0:
            session_info = get_session_info(table_name,session_id)
            if len(session_info) > 0:
                session_info = session_info[-context_rounds:]
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "qa":
                        if self.language.find('chinese') >=0:
                            history_str += ( '问题：' + str(item[0]) + '，回复：' + str(item[1]) + ';' )
                        elif self.language == 'english':
                            history_str += ( 'question:' + str(item[0]) + ',answer:' + str(item[1]) + ';' )
        print('history:',history_str)
        if len(history_str) > 0:
            self.llm.model_kwargs['history'] = history_str
        
        result = {}
        if (task == 'qa' or task == 'search') and isCheckedKnowledgeBase:
            work_mode = "multi-modal"
            retriever = self.get_retriever(top_k,search_method,txt_docs_num,vec_docs_score_thresholds,txt_docs_score_thresholds,text_field,vector_field,image_field,work_mode)
            docs = retriever.get_relevant_documents(query)
            
            print('docs:',docs)

            result['source_documents'] = docs
            if len(docs) > 0:
                related_docs = []
                for doc in docs:
                    related_doc = {}
                    related_doc['text'] = doc[0].page_content
                    if 'sources' in  doc[0].metadata.keys():
                        related_doc['title'] = doc[0].metadata['sources'].split('/')[-1]
                    elif 'source' in  doc[0].metadata.keys():
                        related_doc['title'] = doc[0].metadata['source'].split('/')[-1]
                    if len(doc) == 3:
                        related_doc['image'] = doc[2]
                    if len(related_doc) > 0:
                        related_docs.append(related_doc)
                    
                if len(related_docs) > 0:
                    self.llm.model_kwargs['related_docs'] = related_docs
    
                response = self.llm(prompt='')
                result['answer'] = response
            else:
                result['answer'] = response_if_no_docs_found
                
        elif task == 'chat' or not isCheckedKnowledgeBase:
            result = self.llm(prompt='')
            
        print('result:',result)
        return result