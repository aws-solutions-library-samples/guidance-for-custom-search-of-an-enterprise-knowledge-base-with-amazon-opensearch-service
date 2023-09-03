import os
import shutil
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import TextLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.embeddings.sagemaker_endpoint import SagemakerEndpointEmbeddings
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.docstore.document import Document
from langchain.text_splitter import NLTKTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import ContentHandlerBase
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from chinese_text_splitter import ChineseTextSplitter
import json
from typing import Dict, List, Tuple
from tqdm import tqdm
from datetime import datetime
import boto3
import numpy as np

def load_file(filepath,language,chunk_size: int=500, chunk_overlap: int=50):
    
    print('begin to load ' + filepath + ' file')
    if filepath.lower().endswith(".pdf"):
        loader = PyPDFLoader(filepath)
    elif filepath.lower().endswith(".docx"):
        loader = Docx2txtLoader(filepath)
    elif filepath.lower().endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(filepath)
    elif filepath.lower().endswith(".csv"):
        print('begin load csv file')
        loader = CSVLoader(filepath)
        print('finish load csv file')
    elif filepath.lower().endswith(".txt"):
        loader = TextLoader(filepath)
    else:
        loader = TextLoader(filepath)

    if language == "chinese":
        if filepath.lower().endswith(".pdf"):
            print("language is chinese and file is pdf")
            textsplitter = ChineseTextSplitter(pdf=True)
        else:
            textsplitter = ChineseTextSplitter()
    elif language == "english":
        print('begin ini spliter,chunk_size:',chunk_size)
        textsplitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        print('finish ini spliter')

    print('begin load and split')
    docs = loader.load_and_split(textsplitter)
    return docs


def init_embeddings(endpoint_name,region_name,language: str = "chinese"):
    
    class ContentHandler(EmbeddingsContentHandler):
        content_type = "application/json"
        accepts = "application/json"

        def transform_input(self, inputs: List[str], model_kwargs: Dict) -> bytes:
            input_str = json.dumps({"inputs": inputs, **model_kwargs})
            return input_str.encode('utf-8')

        def transform_output(self, output: bytes) -> List[List[float]]:
            response_json = json.loads(output.read().decode("utf-8"))
            if language.find("chinese")>=0:
                return response_json[0][0]
            else:
                return response_json


    content_handler = ContentHandler()

    embeddings = SagemakerEndpointEmbeddings(
        endpoint_name=endpoint_name, 
        region_name=region_name, 
        content_handler=content_handler
    )
    return embeddings


def init_vector_store(embeddings,
             index_name,
             opensearch_host,
             opensearch_port,
             opensearch_user_name,
             opensearch_user_password):

    vector_store = OpenSearchVectorSearch(
        index_name=index_name,
        embedding_function=embeddings, 
        opensearch_url="aws-opensearch-url",
        hosts = [{'host': opensearch_host, 'port': opensearch_port}],
        http_auth = (opensearch_user_name, opensearch_user_password),
    )
    return vector_store


def init_model(endpoint_name,
               region_name,
               temperature: float = 0.01):
    try:
        class ContentHandler(LLMContentHandler):
            content_type = "application/json"
            accepts = "application/json"

            def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
                input_str = json.dumps({"ask": prompt, **model_kwargs})
                return input_str.encode('utf-8')

            def transform_output(self, output: bytes) -> str:
                response_json = json.loads(output.read().decode("utf-8"))
                return response_json['answer']

        content_handler = ContentHandler()

        llm=SagemakerEndpoint(
                endpoint_name=endpoint_name, 
                region_name=region_name, 
                model_kwargs={"temperature":temperature},
                content_handler=content_handler,
        )
        return llm
    except Exception as e:
        return None


class SmartSearchQA:
    
    def init_cfg(self,
                 opensearch_index_name,
                 opensearch_user_name,
                 opensearch_user_password,
                 opensearch_host,
                 opensearch_port,
                 embedding_endpoint_name,
                 region,
                 llm_endpoint_name: str = 'pytorch-inference-llm-v1',
                 temperature: float = 0.01,
                 language: str = "chinese"
                ):
        self.language = language
        self.llm = init_model(llm_endpoint_name,region,temperature)
        self.embeddings = init_embeddings(embedding_endpoint_name,region,self.language)
        self.vector_store = init_vector_store(self.embeddings,
                                             opensearch_index_name,
                                             opensearch_host,
                                             opensearch_port,
                                             opensearch_user_name,
                                             opensearch_user_password)
        
        
    def init_knowledge_vector(self,filepath: str or List[str], bulk_size: int = 10000, chunk_size: int=500, chunk_overlap: int=50):
        loaded_files = []
        failed_files = []
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("Path does not exist")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = load_file(filepath,self.language,chunk_size)
                    print(f"{file} Loaded successfully")
                    loaded_files.append(filepath)
                except Exception as e:
                    print(e)
                    print(f"{file} Failed to load")
                    return None
            elif os.path.isdir(filepath):
                docs = []
                min_docs = []
                for file in tqdm(os.listdir(filepath), desc="Load the file"):
                    fullfilepath = os.path.join(filepath, file)
                    try:
                        doc = load_file(fullfilepath,self.language,chunk_size)
                        docs += doc                            
                        loaded_files.append(fullfilepath)
                    except Exception as e:
                        failed_files.append(file)

                if len(failed_files) > 0:
                    print("The following files failed to load:")
                    for file in failed_files:
                        print(file,end="\n")
        else:
            docs = []
            min_docs = []
            for file in filepath:
                try:
                    print("begin to load file, file:",file,self.language)
                    docs = load_file(file,self.language,chunk_size)
                    print(f"{file} Loaded successfully")
                    loaded_files.append(file)
                except Exception as e:
                    print(e)
                    print(f"{file} Failed to load")
        if len(docs) > 0:
            print("The file is loaded and the vector library is being generated")
            if self.vector_store is not None:
                new_texts = []
                new_metadatas = []
                texts = [d.page_content for d in docs]
                metadatas = [d.metadata for d in docs]
                sep = '。'
                if self.language == "english":
                    sep = '.'
                                        
                if len(metadatas) > 0 and 'row' in metadatas[0].keys():
                    pre_row = 0
                    phase_text = ""
                    sen_texts = []
                    pre_metadata = ""
                    pre_title = ""
                    for i in range(len(metadatas)):
                        text = texts[i]
                        # print('text:',text)
                        metadata = dict(metadatas[i])
                        row = int(metadata['row'])
                        title=''
                        if self.language == "english" and text.find('title') >= 0 and text.find('content') >= 0:
                            title = text.split('title:')[1].split('content:')[0].strip()
                        if self.language == "chinese" and text.find('标题') >= 0 and text.find('内容') >= 0:
                            title = text.split('标题:')[1].split('内容:')[0].strip()

                        if i == 0:
                            pre_metadata = metadata
                            pre_title = title

                        if row == pre_row:
                            phase_text += (text + sep)
                            sen_texts.append(text)
                            word_len = 0
                            for sen in sen_texts:
                                word_len += len(sen)
                            if word_len > 2000:
                                if len(pre_title) > 0:
                                    new_text = pre_title + "@@@" + phase_text
                                    new_texts.append(new_text)
                                    new_metadatas.append(pre_metadata)
                                for sen_text in sen_texts:
                                    new_text = sen_text + "@@@" + phase_text
                                    new_texts.append(new_text)
                                    new_metadatas.append(pre_metadata)
                                sen_texts = []
                                phase_text = ''

                        else:
                            if len(pre_title) > 0:
                                new_text = pre_title + "@@@" + phase_text
                                new_texts.append(new_text)
                                new_metadatas.append(pre_metadata)
                            for sen_text in sen_texts:
                                new_text = sen_text + "@@@" + phase_text
                                new_texts.append(new_text)
                                new_metadatas.append(pre_metadata)
                            phase_text = text
                            pre_row = row
                            pre_metadata = metadata
                            pre_title = title
                            sen_texts = []
                            sen_texts.append(text)

                    if(len(sen_texts)>0):
                        if len(pre_title) > 0:
                            new_text = pre_title + "@@@" + phase_text
                            new_texts.append(new_text)
                            new_metadatas.append(pre_metadata)
                        for sen_text in sen_texts:
                            new_text = sen_text + "@@@" + phase_text
                            new_texts.append(new_text)
                            new_metadatas.append(pre_metadata)
                           
                else:
                    new_texts = texts
                    new_metadatas = metadatas
                
                ids = self.vector_store.add_texts(new_texts, new_metadatas, bulk_size=bulk_size, language=self.language)
                return loaded_files
            else:
                print("Vector library is not specified, please specify the vector database")
        else:
            print("None of the files loaded successfully, please check the file to upload again.")
            return loaded_files
        
        
    def get_answer_from_RetrievalQA(self,query,
                                        prompt_template: str = "请根据{context}，回答{question}",
                                        top_k: int = 3):
        
        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])
        
        QA_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": top_k}),
            prompt=prompt)
        
        # QA_chain.combine_documents_chain.document_prompt = PromptTemplate(
        #     input_variables=["page_content"], template="{page_content}")

        QA_chain.return_source_documents = True
        result = QA_chain({"query": query})
        return result
        
    def get_answer_from_load_qa_chain(self,query,
                                        prompt_template: str = "请根据{context}，回答{question}",
                                        top_k: int = 3,
                                        chain_type: str="stuff"):
                                       
        prompt = PromptTemplate(template=prompt_template,
                                input_variables=["context", "question"])
        
        if chain_type == "map_rerank":
            from langchain.output_parsers import RegexParser
            output_parser = RegexParser(
                regex=r"(.*?)\nScore: (.*)",
                output_keys=["answer", "score"],
            )
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"],
                output_parser=output_parser,
            )
            chain = load_qa_chain(self.llm, chain_type="map_rerank", prompt=prompt,return_intermediate_steps=True)
            
        else:
            chain = load_qa_chain(self.llm, chain_type="stuff", prompt=prompt)
        
       
        docs_with_scores = self.vector_store.similarity_search(query,k=top_k)
        docs = [doc[0] for doc in docs_with_scores]
        result = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
        return result,docs_with_scores
    
    def get_qa_relation_score(self,query,answer):
        
        query_answer_emb = np.array(self.embeddings._embedding_func([query,answer]))

        query_emb = query_answer_emb[0]
        answer_emb = query_answer_emb[1]
        dot = query_emb * answer_emb 
        query_emb_len = np.linalg.norm(query_emb)
        answer_emb_len = np.linalg.norm(answer_emb)
        cos = dot.sum()/(query_emb_len * answer_emb_len)
        return cos
