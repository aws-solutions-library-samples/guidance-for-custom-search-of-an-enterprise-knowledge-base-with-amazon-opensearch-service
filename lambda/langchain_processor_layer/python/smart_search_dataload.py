import os
import shutil
from langchain.document_loaders import TextLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts.prompt import PromptTemplate
from langchain.embeddings import SagemakerEndpointEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import ContentHandlerBase
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from chinese_text_splitter import ChineseTextSplitter
import json
from typing import Dict, List, Tuple, Optional,Any
from tqdm import tqdm
from datetime import datetime
import boto3
import numpy as np

def load_file(filepath,language,chunk_size: int=100, chunk_overlap: int=10):
    
    print('begin to load ' + filepath + ' file')
    if filepath.lower().endswith(".pdf"):
        loader = PyPDFLoader(filepath)
    elif filepath.lower().endswith(".docx"):
        loader = Docx2txtLoader(filepath)
    elif filepath.lower().endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(filepath)
    elif filepath.lower().endswith(".csv"):
        loader = CSVLoader(filepath)
    elif filepath.lower().endswith(".txt"):
        loader = TextLoader(filepath)
    elif filepath.lower().endswith(".html"):
        loader = UnstructuredHTMLLoader(filepath)
    else:
        loader = TextLoader(filepath)

    if language.find("chinese")>=0:
        if filepath.lower().endswith(".pdf"):
            textsplitter = ChineseTextSplitter(pdf=True)
        else:
            textsplitter = ChineseTextSplitter()
    elif language == "english":
        textsplitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        
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


class SmartSearchDataload:
    
    def init_cfg(self,
                 opensearch_index_name,
                 opensearch_user_name,
                 opensearch_user_password,
                 opensearch_host,
                 opensearch_port,
                 embedding_endpoint_name,
                 region,
                 language: str = "chinese",
                ):
        self.language = language
        self.embeddings = init_embeddings(embedding_endpoint_name,region,self.language)
        self.vector_store = init_vector_store(self.embeddings,
                                             opensearch_index_name,
                                             opensearch_host,
                                             opensearch_port,
                                             opensearch_user_name,
                                             opensearch_user_password)

        
    def init_knowledge_vector(self,filepath: str or List[str], 
                                   bulk_size: int = 10000, 
                                   chunk_size: int=500, 
                                   chunk_overlap: int=50,
                                   sep_word_len: int=2000):
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
                texts = [d.page_content.strip().replace('\n','') for d in docs]
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
                        text = texts[i].strip().replace('\n','')
                        metadata = dict(metadatas[i])
                        row = int(metadata['row'])
                        title=''
                        # if text.find('question') >= 0 and text.find('answer') >= 0:
                        #     title = text.split('question:')[1].split('answer:')[0].strip()

                        if i == 0:
                            pre_metadata = metadata
                            pre_title = title

                        if row == pre_row:
                            phase_text += (text + sep)
                            sen_texts.append(text)
                            word_len = 0
                            for sen in sen_texts:
                                word_len += len(sen)
                            if word_len > sep_word_len:
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
