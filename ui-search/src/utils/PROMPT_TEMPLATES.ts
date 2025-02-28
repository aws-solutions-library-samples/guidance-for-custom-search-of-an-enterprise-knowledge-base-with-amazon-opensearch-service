export const DEFAULT_CHAT_SYSTEM_PROMPT = ``;

const TEMPLATE_1 = {
  text: 'Template_1_文档型内部知识库问答',
  sessionId: 'template_1',
  configs: {
    workMode: 'text',
    searchEngine: 'opensearch',
    isCheckedKnowledgeBase: true,
    searchMethod: 'mix',
    contextRounds: 0,
    vecTopK: 3,
    txtTopK: 2,
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: true,
    isCheckedScoreQD: true,
    isCheckedScoreAD: true,
    isCheckedEditPrompt: true,
    prompt: fStr(`<任务定义>
    下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。
    1. 若可以从“已知信息”中获取答案，请直接简洁得输出最终答案，请不要输出推导或者思考过程。
    2. 若不可以从“已知信息”中获取答案，请直接回答“根据已知信息无法回答”，请不要输出其他信息
    </任务定义>
    <输出设定>
    1.  你是一个公司的行政人员，请尽可能礼貌得回答问题
    2. 不要输出推导过程，或者复述原始”已知信息“，请直接给出最终答案
    3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸
    </输出设定>
     <已知信息>
    {context}
     </已知信息>
    <问题>{question}<问题>
    AI:`),
    sessionId: 'template_1',
  },
} as const;

const TEMPLATE_2 = {
  text: 'Template_2_表格型(QA问题对)内部知识库问答',
  sessionId: 'template_2',
  configs: {
    workMode: 'text',
    searchEngine: 'opensearch',
    isCheckedKnowledgeBase: true,
    searchMethod: 'mix',
    contextRounds: 0,
    vecTopK: 3,
    txtTopK: 2,
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: true,
    isCheckedScoreQD: true,
    isCheckedScoreAD: true,
    isCheckedEditPrompt: true,
    prompt: fStr(`<任务定义>
    1. 请根据以下“已知信息”回答问题。
    2. 如果无法从“已知信息”中获取答案，请回答“无法根据已知信息回答”，不得虚构答案。
    </任务定义>
    <已知信息结构说明>
    1. 已知信息由多个 JSON 格式条目组成，每个条目包含三个字段。
    2. 这三个字段分别是“问题”和“答案”。
    3. 信息中的某些字段可能为空。
    </已知信息结构说明>
    <输出设置>
    1. 你是一个公司的行政人员，请在可能的情况下提供礼貌回答。
    2. 不要包括推理过程或重述原始“已知信息”。请直接提供最终答案。
    3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸
    </输出设置>
    <已知信息>
    {context}
    </已知信息>
    <问题>{question} <问题>
    AI:`),
    sessionId: 'template_2',
  },
} as const;

const TEMPLATE_3 = {
  text: 'Template_3_表格型(维保)内部知识库问答',
  sessionId: 'template_3',
  configs: {
    workMode: 'text',
    searchEngine: 'opensearch',
    isCheckedKnowledgeBase: true,
    searchMethod: 'mix',
    contextRounds: 0,
    vecTopK: 3,
    txtTopK: 2,
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: true,
    isCheckedScoreQD: true,
    isCheckedScoreAD: true,
    isCheckedEditPrompt: true,
    prompt: fStr(`<任务定义>
    1. 请根据以下“已知信息”回答问题。
    2. 如果无法从“已知信息”中获取答案，请回答“无法根据已知信息回答”，不得虚构答案。
    </任务定义>
    <已知信息结构说明>
    1. 已知信息由多个 JSON 格式条目组成，每个条目包含三个字段。
    2. 这三个字段分别是“问题”，“根本原因”和“解决方案”。
    3. 信息中的某些字段可能为空。
    </已知信息结构说明>
    <输出设置>
    1. 你是一个维保工程师，请在可能的情况下提供礼貌回答。
    2. 不要包括推理过程或重述原始“已知信息”。请直接提供最终答案。
    3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸
    </输出设置>
    <已知信息>
    {context}
    </已知信息>
    <问题>{question} <问题>
    AI:`),
    sessionId: 'template_3',
  },
} as const;

const TEMPLATE_4 = {
  text: 'Template_4_文档型分析/摘要',
  sessionId: 'template_4',
  configs: {
    workMode: 'text',
    searchEngine: 'opensearch',
    isCheckedKnowledgeBase: true,
    searchMethod: 'mix',
    contextRounds: 0,
    vecTopK: 4,
    txtTopK: 1,
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: true,
    isCheckedScoreQD: true,
    isCheckedScoreAD: true,
    isCheckedEditPrompt: true,
    prompt: fStr(`<任务定义>
    下面将给你一个“摘要分析任务”和一些“已知信息”，请判断“摘要分析任务”是否可以根据“已知信息”完成。
    1. 若可以完成，根据任务指示完成输出。
    2. 若不可以完成，请直接回答“根据已知信息无法回答”，请不要输出其他信息
    </任务定义>
    <输出设定>
    1.  请尽可能礼貌得回答问题
    2. 不要输出推导过程，或者复述原始”已知信息“，请直接给出最终答案
    3. 回答开头使用“根据已知信息”，结尾使用一个笑脸
    </输出设定>
     <已知信息>
    {context}
     </已知信息>
    <摘要分析任务>{question}<摘要分析任务>
    AI:`),
    sessionId: 'template_4',
  },
} as const;

const TEMPLATE_5_MULTI_MODAL = {
  text: 'Template_5_Multi_Modal_文档型内部知识库问答',
  sessionId: 'template_5_multi_modal',
  configs: {
    sessionId: 'template_5_multi_modal',
    searchEngine: 'opensearch',
    isCheckedKnowledgeBase: true,
    searchMethod: 'mix',
    contextRounds: 0,
    vecTopK: 3,
    txtTopK: 2,
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: true,
    isCheckedScoreQD: true,
    isCheckedScoreAD: true,
    isCheckedEditPrompt: true,
    workMode: 'multi-modal',
    workFlow: ['CHAT', 'RAG'],
    chatSystemPrompt: DEFAULT_CHAT_SYSTEM_PROMPT,
    prompt: fStr(`<任务定义>
    下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。
    1. 若可以从“已知信息”中获取答案，请直接简洁得输出最终答案，请不要输出推导或者思考过程。
    2. 若不可以从“已知信息”中获取答案，请直接回答“根据已知信息无法回答”，请不要输出其他信息
    </任务定义>
    <输出设定>
    1.  你是一个公司的行政人员，请尽可能礼貌得回答问题
    2. 不要输出推导过程，或者复述原始”已知信息“，请直接给出最终答案
    3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸
    </输出设定>`),
  },
} as const;

let PROMPT_TEMPLATES = [
  TEMPLATE_5_MULTI_MODAL,
  TEMPLATE_1,
  TEMPLATE_2,
  TEMPLATE_3,
  TEMPLATE_4,
];

export const DEMO_SESSION_1 = {
  type: 'link',
  href: '/session/demo_session_1',
  text: 'dishwasher (multi-modal)',
  sessionId: 'demo_session_1',
  configs: {
    name: 'dishwasher (multi-modal)',
    searchEngine: 'opensearch',
    workMode: 'multi-modal',
    workFlow: ['CHAT', 'RAG'],
    llmData: {
      strategyName: 'claude3_bge_strategy',
      type: 'third_party_api',
      embeddingEndpoint: 'bge-m3-2024-05-15-14-47-26-255-endpoint',
      modelType: 'bedrock',
      modelName: 'anthropic.claude-3-sonnet-20240229-v1:0',
      recordId: 'anthropic.claude-3-sonnet-20240229-v1:0-98550',
      apiUrl: '',
      apiKey: '',
      secretKey: '',
    },
    role: '',
    language: 'english',
    taskDefinition: '',
    outputFormat: '',
    isCheckedGenerateReport: false,
    isCheckedContext: false,
    isCheckedKnowledgeBase: true,
    indexName: 'multi-model-dishwasher',
    vecTopK: '3',
    searchMethod: 'vector',
    txtTopK: '2',
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: false,
    isCheckedScoreQD: false,
    isCheckedScoreAD: false,
    contextRounds: 0,
    isCheckedEditPrompt: true,
    chatSystemPrompt: DEFAULT_CHAT_SYSTEM_PROMPT,
    prompt:
      '<任务定义>\n下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。\n1. 若可以从“已知信息”中获取答案，请直接简洁得输出最终答案，请不要输出推导或者思考过程。\n2. 若不可以从“已知信息”中获取答案，请直接回答“根据已知信息无法回答”，请不要输出其他信息\n</任务定义>\n<输出设定>\n1. 你是一个洗碗机客服人员，请尽可能礼貌得回答问题\n2. 不要输出推导过程，或者复述原始”已知信息“，请直接给出最终答案\n3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸\n4. 回答使用英文\n</输出设定>',
    responseIfNoDocsFound: 'Cannot find the answer',
    sessionId: 'demo_session_1',
  },
  conversations: [],
};
const DEMO_SESSION_2 = {
  type: 'link',
  href: '/session/demo_session_2',
  text: 'dishwasher',
  sessionId: 'demo_session_2',
  configs: {
    name: 'dishwasher',
    searchEngine: 'opensearch',
    workMode: 'text',
    workFlow: ['RAG'],
    llmData: {
      strategyName: 'claude3_bge_strategy',
      type: 'third_party_api',
      embeddingEndpoint: 'bge-m3-2024-05-15-14-47-26-255-endpoint',
      modelType: 'bedrock',
      modelName: 'anthropic.claude-3-sonnet-20240229-v1:0',
      recordId: 'anthropic.claude-3-sonnet-20240229-v1:0-98550',
      apiUrl: '',
      apiKey: '',
      secretKey: '',
    },
    role: '',
    language: 'english',
    taskDefinition: '',
    outputFormat: '',
    isCheckedGenerateReport: false,
    isCheckedContext: false,
    isCheckedKnowledgeBase: true,
    indexName: 'dishwasher',
    vecTopK: '3',
    searchMethod: 'vector',
    txtTopK: '2',
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: false,
    isCheckedScoreQD: false,
    isCheckedScoreAD: false,
    contextRounds: 0,
    isCheckedEditPrompt: true,
    prompt:
      '<任务定义>\n下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。\n1. 若可以从“已知信息”中获取答案，请直接简洁得输出最终答案，请不要输出推导或者思考过程。\n2. 若不可以从“已知信息”中获取答案，请直接回答“根据已知信息无法回答”，请不要输出其他信息\n</任务定义>\n<输出设定>\n1. 你是一个洗碗机客服人员，请尽可能礼貌得回答问题\n2. 不要输出推导过程，或者复述原始”已知信息“，请直接给出最终答案\n3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸\n4. 回答使用英文\n</输出设定>',
    responseIfNoDocsFound: 'Cannot find the answer',
    sessionId: 'demo_session_2',
  },
  conversations: [],
};
const DEMO_SESSION_3 = {
  type: 'link',
  href: '/session/demo_session_3',
  text: 'air compressor',
  sessionId: 'demo_session_3',
  configs: {
    name: 'air compressor',
    searchEngine: 'opensearch',
    workMode: 'text',
    workFlow: ['RAG'],
    llmData: {
      strategyName: 'claude3_bge_strategy',
      type: 'third_party_api',
      embeddingEndpoint: 'bge-m3-2024-05-15-14-47-26-255-endpoint',
      modelType: 'bedrock',
      modelName: 'anthropic.claude-3-sonnet-20240229-v1:0',
      recordId: 'anthropic.claude-3-sonnet-20240229-v1:0-98550',
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
    indexName: 'air_compressor',
    vecTopK: '3',
    searchMethod: 'vector',
    txtTopK: '2',
    vecDocsScoreThresholds: 0,
    txtDocsScoreThresholds: 0,
    isCheckedScoreQA: false,
    isCheckedScoreQD: false,
    isCheckedScoreAD: false,
    contextRounds: 0,
    isCheckedEditPrompt: true,
    prompt:
      '<任务定义>\n下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。\n1. 若可以从“已知信息”中获取答案，请直接简洁得输出最终答案，请不要输出推导或者思考过程。\n2. 若不可以从“已知信息”中获取答案，请直接回答“根据已知信息无法回答”，请不要输出其他信息\n</任务定义>\n<输出设定>\n1. 你是一个空压机维保助手，请尽可能礼貌得回答问题\n2. 不要输出推导过程，或者复述原始”已知信息“，请直接给出最终答案\n3. 回答开头使用“感谢你的提问”，在回答请一定杜绝使用类似“根据已知信息”的字眼，结尾使用一个笑脸\n</输出设定>',
    responseIfNoDocsFound: 'Cannot find the answer',
    sessionId: 'demo_session_3',
  },
  conversations: [],
};

const DEMO_SESSIONS = [DEMO_SESSION_1, DEMO_SESSION_2, DEMO_SESSION_3];
if (JSON.parse(process.env.REACT_APP_DEMO)) {
  // @ts-ignore
  PROMPT_TEMPLATES = PROMPT_TEMPLATES.concat(DEMO_SESSIONS);
}
export default PROMPT_TEMPLATES;

function fStr(str) {
  // @ts-ignore
  return JSON.parse(JSON.stringify(str).replaceAll(' ', ''));
}
