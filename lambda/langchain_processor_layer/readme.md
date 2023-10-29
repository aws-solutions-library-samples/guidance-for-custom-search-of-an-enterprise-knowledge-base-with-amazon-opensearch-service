1、layer使用python3.9环境，运行requirement.txt部署，部署好后以下依赖包可能需要降级：
numpy==1.25.0
pydantic==1.10.10
pydantic_core==2.0.1

2、langchain修改的文件包括：
langchain/vectorstores/opensearch_vector_search.py
langchain/embeddings/sagemaker_endpoint.py
langchain/chains/conversational_retrieval/base.py
langchain/llms/__init__.py
langchain/llms/amazon_api_gateway_bedrock.py(新增)

