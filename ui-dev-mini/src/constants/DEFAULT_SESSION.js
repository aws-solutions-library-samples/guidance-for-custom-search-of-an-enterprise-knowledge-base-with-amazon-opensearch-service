const sessionId = process.env.REACT_APP_DEFAULT_SESSION_ID
const indexName = process.env.REACT_APP_KB_INDEX_NAME

/**
 * Please checkout [User Guide v3.3](https://quip-amazon.com/4YEBAuvWd3GQ/Intelligent-Search-V33) API section for more details re how to configure each value.
 */
const DEFAULT_SESSION = {
  sessionId: sessionId ?? 'default_session_0',
  conversations: [],
  configs: {
    searchEngine: 'opensearch',
    llmData: {
      type: 'third_party_api',
      embeddingEndpoint: 'cohere.embed-multilingual-v3',
      modelType: 'bedrock',
      modelName: 'anthropic.claude-3-sonnet-20240229-v1:0',

      strategyName: 'test', // frontend ui usage only
      recordId: '123456', // frontend ui usage only
      apiUrl: '',
      apiKey: '',
      secretKey: '',
    },
    language: 'chinese',
    isCheckedKnowledgeBase: true,
    indexName: indexName ?? 'index_would_prompt_error',
    topK: '2',
    searchMethod: 'mix',
    txtDocsNum: '2',
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: false,
    isCheckedScoreQD: false,
    isCheckedScoreAD: false,
    contextRounds: '0',
    prompt:
      "<Task Defination>\n下面会给你一些“告警码或者告警信息”，请根据上述内容从以下“备选告警信息集“根据“匹配规则”选择匹配的条目，并输出对应的“指定字段”。若不能够从”备选告警信息集“中获取匹配的条目，请回答”没有找到相关告警信息和维修指南“，请不要自行编造。\n\n<告警码或者告警信息结构>\n1. 输入的信息可能同时包含告警码和告警信息，也可能仅包含其中一个\n2. 每个告警码由4位数字组成，输入的告警码可能包含一个或者多个\n</告警码或者告警信息结构>\n\n<匹配规则>\n1. 对于输入的为告警码：\na. 若是单个4位告警码，则必须要完全匹配，例如输入为0001，则“备选告警信息集”中寻找告警码为0001的条目\nb. 若是多个4位告警码，则分别进行匹配，例如输入为0001和0021，则分别从“备选告警信息集”中寻找告警码为0001和0021的条目\n2. 对于输入是告警信息描述，则根据语意进行匹配，注意只要语意符合即可，不必追求完全的字段匹配\n</匹配规则>\n\n<备选告警信息集结构>\n1. 备选告警信息集由一条或者多条备选告警信息组成\n2. 每条告警信息格式位JSON格式\n3. 包含的字段有：'告警码','告警信息-CN', '判断条件-CN', '维修指引(运营商家端)-CN', '远程维修指引(桩企)-CN', '现场维修指引(桩企)-CN'\n</备选告警信息集结构>\n\n<指定字段>\n“告警码”，“告警信息”，“维修指引(运营商家端)”，“远程维修指引(桩企)”和“现场维修指引(桩企)”\n</指定字段>\n</Task Defination>\n\n<备选告警信息集>\n{context}\n</备选告警信息集>\n\n<告警码或者告警信息>\n{question}\n</告警码或者告警信息>\n\n<Output Rules>\n1. 若告警码或者告警信息能够匹配备选告警信息，按照”指定字段“依次直接输出内容\n2. 若告警码或者告警信息不能够从”备选告警信息集“中获取匹配的条目，请回答”没有找到相关告警信息和维修指南“\n<Output Rules>\n\nAI:",
    tokenContentCheck: '',
    responseIfNoDocsFound: 'Cannot find the answer',
    workMode: 'text',
    sessionId: sessionId ?? 'default_session_0',

    //**** key-values can be kindly ignored ****/
    name: 'Default Session 0', // frontend ui usage only
    role: '', // warning: to be deprecated
    taskDefinition: '', // warning: to be deprecated
    outputFormat: '', // warning: to be deprecated
    isCheckedGenerateReport: false,
    isCheckedContext: false,
    isCheckedEditPrompt: true, // frontend ui usage only
  },
}

export default DEFAULT_SESSION
