## GCR Guidance for Intelligent Search on AWS

## Description

This Guidance demonstrates how to build a one-stop and multi-dimensional data search platform based on Amazon OpenSearch and Amazon Kendra. Deep cooperation with Hugging Face through Amazon Sagemaker allows us to quickly deploy inference nodes, including large language models (LLMs), and combine search services to directly give answers to search questions based on the enterprise knowledge base, empowering customers in various industries. This solution guidance will include five key elements: 1） Intelligent Search Building a search engine based on Amazon OpenSearch and Amazon Kendra. Providing word segmentation search, fuzzy queries, and AI/ML-assisted search capabilities. 2） Intelligent Guide Using methods such as manual labeling, unsupervised clustering, supervised classification, and LLM to extract guide words. Using guide words to guide users to enrich their search input. 3） Intelligent Optimization Optimizing the search engine based on user behavior (e.g. rating/click frequency). 4） Intelligent Q&A Directly providing question answers based on LLM search content from enterprise knowledge base. 5） Unstructured Data Injection Automatically splitting docs into paragraphs, and vector encoding unstructured text to establish a structured enterprise knowledge base.

More Details can be found in [AWS Solutions Library](https://aws.amazon.com/cn/solutions/guidance/custom-search-of-an-enterprise-knowledge-base-on-aws/?did=sl_card&trk=sl_card)

## Deployment Guide


* Follow the deployment guide in [AWS Solutions Library](https://catalog.us-east-1.prod.workshops.aws/workshops/3973557a-0853-41f6-9678-00ae171ba1f6/zh-CN/03cdkinstall/30preinstall)



## Update
2023.08.27: Add the function to call Bedrock LLM(claude and titan) api

2023.08.27: Add the bge chinese and english embbeding model deployment scripts

2023.08.18: Add the streamlit webpage for multiple rounds of conversation demo

2023.08.15: Add the function to call llama2, llama2 model can be deployed in SageMaker jumpstart 

2023.08.07: Add the baichuan 7B LLM deployment scripts


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

