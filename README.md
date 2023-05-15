## GCR Guidance for Intelligent Search on AWS

## Description

This Guidance demonstrates how to build a one-stop and multi-dimensional data search platform based on Amazon OpenSearch and Amazon Kendra. Deep cooperation with Hugging Face through Amazon Sagemaker allows us to quickly deploy inference nodes, including large language models (LLMs), and combine search services to directly give answers to search questions based on the enterprise knowledge base, empowering customers in various industries. This solution guidance will include five key elements: 1） Intelligent Search Building a search engine based on Amazon OpenSearch and Amazon Kendra. Providing word segmentation search, fuzzy queries, and AI/ML-assisted search capabilities. 2） Intelligent Guide Using methods such as manual labeling, unsupervised clustering, supervised classification, and LLM to extract guide words. Using guide words to guide users to enrich their search input. 3） Intelligent Optimization Optimizing the search engine based on user behavior (e.g. rating/click frequency). 4） Intelligent Q&A Directly providing question answers based on LLM search content from enterprise knowledge base. 5） Unstructured Data Injection Automatically splitting docs into paragraphs, and vector encoding unstructured text to establish a structured enterprise knowledge base.

More Details can be found in [Builder Space](https://builderspace.proto.sa.aws.dev/project/13af5660-1e55-4527-b5c9-9e8ff21a5c32)

## Deployment Guide

**AWS Service Deployment :** 

* Change directory to ./deployment folder
```
cd ./deployment
```

* Follow the instruction of README.md in the deployment folder


**Model Deployment :** 

* Open Amazon Sagemaker Notebook，find the notebook with the name of SmartSearchNotebook.

* Embedding Model Deployment
(1)	shibing624_text2vec-base-chinese: Open Embedding Model/ EmbbedingModel_shibing624_text2vec-base-chinese.ipynb
(2)	Run the first two cell to deploy
(3)	Run the third cell to validate

* LLM Model Deployment
(1)	Chatglm: Open LLM_Model/chatglm/chatglm_sagemaker_byos.ipynb
(2)	Run the first two cell to deploy
(3)	Run the following cell to validate

Tips 1: The LLM model endpoint still needs some time to download the model artifacts after the endpoint is in service status. You could check the downloading status in CloudWatch logs of the endpoint.
Tips 2: The Embedding and LLM models's deployment could be doing, simultaneously.

**Data Preprocessing and Data ingestion :** 

(1)	You must make sure the embedding model was deployed successfully.
(2)	Upload your testing data files (docx formation) to Sagemaker Notebook
(3)	Open Script-Doc.ipynb, and run the first two cell
(4)	In hyperparameter part, input the following parameter and run the cell:
    a.	index_name: The name of your index (database) in OpenSearch
    b.	folder_path: The original data file folder path
        folder_path
            ---file1.docx
            ---file2.docx	
(5)	Run the following cell

**Validation :** 
(1)	Go to Amazon ApiGateway, find the api with the name of opensearch-api
(2)	Chose the /search_knn_doc/GET
(3)	Click TEST
(4)	Input: q="123"&ind="docs"&knn="1", where q is the input question, ind is the index_name which you set in "Data Preprocessing and Data ingestion", knn="1" means using embbeding model while knn="0" means not.
(5)	Status 200 means you deploy successfully.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

