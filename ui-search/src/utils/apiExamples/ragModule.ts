export const configs = {
  name: 'debug2',
  searchEngine: 'opensearch',
  workMode: 'multi-modal',
  chatSystemPrompt:
    '"任务要求:\\n  1. 接受图片和文字作为输入,输入格式不作限制\\n  2. 根据输入的图片和文字信息生成一句综合描述\\n  3. 描述内容尽可能详尽\\n  \\n  输出要求:\\n  输出必须严格符合以下JSON格式,不包含任何其他多余的文字或说明,只输出JSON数据\\n  {\\n    \\"query\\": \\"一句综合描述\\"\\n  }\\n  \\n  其中,\\"query\\"字段的值为根据输入图片和文字生成的一句综合描述\\n  \\n  示例输入:\\n  图片1, 图片2\\n  文字 \\"这是一段关于旅游的介绍,描述了某个城市的地理位置、景点等信息。\\"\\n  \\n  示例输出(注意,下面的输出中只包含JSON数据,没有其他多余信息):\\n  {\\"query\\": \\"这是一张展示户外自然景观的图片,图中有蓝天、绿树和溪流,并附有一段关于某个城市旅游景点和地理位置的文字介绍。\\"}\\n  \\n  注意事项:\\n  1. 输出格式必须严格遵守给定的JSON格式\\n  2. 除JSON数据外,不输出任何其他多余的文字或说明"',
  llmData: {
    strategyName: 'test',
    type: 'third_party_api',
    embeddingEndpoint: 'huggingface-inference-eb',
    modelType: 'bedrock',
    modelName: 'anthropic.claude-3-sonnet-20240229-v1:0',
    recordId: 'anthropic.claude-3-sonnet-20240229-v1:0-59695',
    apiUrl: '',
    apiKey: '',
    secretKey: '',
  },
  role: '',
  language: 'chinese',
  taskDefinition: '',
  outputFormat: '',
  isCheckedGenerateReport: false,
  isCheckedContext: false,
  isCheckedKnowledgeBase: true,
  indexName: 'mihoyo_cs_all',
  vecTopK: '2',
  searchMethod: 'vector',
  txtTopK: 0,
  vecDocsScoreThresholds: 0,
  txtDocsScoreThresholds: 0,
  isCheckedScoreQA: true,
  isCheckedScoreQD: true,
  isCheckedScoreAD: true,
  contextRounds: 3,
  isCheckedEditPrompt: true,
  prompt:
    '<Task Definition>\n1. Please answer the question based on the following "known information".\n2. If the answer cannot be obtained from the "known information", please answer "Unable to answer based on known information" and do not invent an answer.\n</Task Definition>\n\n\n<Output Settings>\n1. You are an Mihoyo IT engineering, please provide polite responses whenever possible.\n2. Do not include the reasoning process or restate the original "known information." Please provide the final answer directly.\n3. Answer In English\n</Output Settings>\n\n<Known Information>\n{context}\n</Known Information>\n\nQuestion: {question} <output rule>Please Answer In English, start with "Thanks for your asking" and end with a smile. Don\'t include any sentences like"provided information" at the beginning<output rule>\n\nAI(Answer In English):',
  responseIfNoDocsFound: 'Cannot find the answer',
  sessionId: '1710921970499-49189',
};

/**
 * RAG module: websocket protocol
 */
export const ragModuleRequest = {
  // Websocket action
  action: 'search',

  configs,
  // multi-modal: CHAT module return
  query: "What's in this image? <img> and in this image <img>",
  // multi-modal: user input
  question: [
    { type: 'text', text: "What's in this image?" },
    { type: 'image', base64: 'iVBORw...' },
    { type: 'text', text: 'and in this image' },
    { type: 'image', base64: 'iVBORw...' },
  ],
};

/**
 * response data same as v3.2
 */
export const ragModuleResponse = {
  message: 'streaming_end',
  timestamp: 1713154398296.923,
  sourceData: [
    {
      id: 0,
      title: 'Model Cases',
      titleLink: 'http://#',
      paragraph:
        'Model CasesIn-game issue regarding the upgrade of Statue of the Seven. In this ticket, the CS did well in helping the player understand that there was no bug or issue by asking relevant information and clearly explaining the screenshots provided by the player. It is really important for the CS to utilize the tools and know where to look if an issue was encountered. Player: I gathered 19 dendroculi to upgrade my statue with, but when i tried to do it they justdisapeared. Before i tried to upgrade',
      sentence: 'None',
      scoreQueryDoc: 0.631,
      scoreAnswerDoc: 0.475,
    },
    {
      id: 1,
      title: ' Aihelp',
      titleLink: 'http://#',
      paragraph:
        "CS work tool - AihelpPreparation before using AihelpIntroductionPermissionLink and LoginAihelp is the platform we use to reply to emails sent by players to our CS mailboxes. Unlike the CSC customer complaint platform, when we reply to players on Aihelp, they will receive an individual email, which is different from the conversation format on the CSC platform. In terms of emails, we need to strictly adhere to the format of regular emails. Additionally, it's important to note that emails in Aihelp",
      sentence: 'None',
      scoreQueryDoc: 0.603,
      scoreAnswerDoc: 0.458,
    },
  ],
  text: 'Thanks for your asking! The statement "The player\'s email address is already linked to another HoYoverse account and cannot be linked to the desired HoYoverse account at the same time" is correct. An email address can only be linked to one HoYoverse account at a time. :)\n\nB: ',
  scoreQueryAnswer: '0.243',
};
