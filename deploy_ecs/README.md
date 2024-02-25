按照https://github.com/xusenlinzy/api-for-open-llm/tree/master 打包镜像，上传ecr。

把镜像路径填入app.py的第148行，例如： image=ecs.ContainerImage.from_registry("310850127430.dkr.ecr.us-west-2.amazonaws.com/llm-api:pytorch")

在deploy_ecs下运行cdk deploy --all  --no-roll-back --require-approval never.

    注意：

    便于调试，目前ecs stack在public vpc, 之后会改到private vpc

    目前需要手动把数据上传到efs, 可以把模型上传到s3, ecs node上面装了cli, 可以直接进行s3 sync操作。

记录生成的alb的url，在/lambda/langchain_processor_qa/smart_search_qa.py line 20行替换

例如：os.environ["OPENAI_API_BASE"] = "http://xxx.us-east-2.elb.amazonaws.com/v1"

按照deployment进行其他组件部署。

测试请求范例：

{"action":"search","configs":{"name":"smart_search_qa_test","searchEngine":"opensearch","embedding_type":"ecs","llmData":{"type":"xxx","modelType":"ecs","modelName":"xxx","recordId":"pytorch-inference-llm-v1-68684"},"role":"","language":"chinese","taskDefinition":"","outputFormat":"","isCheckedGenerateReport":false,"isCheckedContext":false,"isCheckedKnowledgeBase":true,"indexName":"smart_search_qa_ecs","topK":1,"searchMethod":"vector","txtDocsNum":0,"vecDocsScoreThresholds":0,"txtDocsScoreThresholds":0,"isCheckedScoreQA":false,"isCheckedScoreQD":true,"isCheckedScoreAD":true,"tokenContentCheck":"","responseIfNoDocsFound":"Cannot find the answer","sessionId":"anbei"},"query":"怎么部署聊天机器人？"}
