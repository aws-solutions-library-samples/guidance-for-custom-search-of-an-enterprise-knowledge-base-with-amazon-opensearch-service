import genUID from './genUID';

const DEFAULT_SESSIONS = [
  {
    type: 'link',
    href: '/session/1697076696219-00001',
    text: 'Test1',
    sessionId: '1697076696219-00001',
    conversations: [],
    configs: {
      name: 'Test1',
      sessionTemplateId: '',
      searchEngine: 'opensearch',
      llmData: {
        type: 'sagemaker_endpoint',
        sagemakerEndpoint: 'sage_end1',
        embeddingEndpoint: 'embedding_end1',
        modelType: 'llama2',
        modelName: 'sage_end1',
        recordId: '-63626',
      },
      role: 'footwear vendor',
      language: 'english',
      taskDefinition: 'help the customer to find the right shoes',
      outputFormat: 'answer in English',
      isCheckedGenerateReport: false,
      isCheckedContext: false,
      isCheckedKnowledgeBase: true,
      isCheckedMapReduce: false,
      indexName: 'index1',
      vecTopK: 3,
      isCheckedScoreQA: true,
      isCheckedScoreQD: true,
      isCheckedScoreAD: true,
      prompt:
        'You are a footwear vendor. help the customer to find the right shoes. answer in English\n\nQuestion:{question}\n=========\n{context}\n=========\nAnswer:',
      sessionId: '1697076696219-00001',
    },
  },
];

export default function genDefaultSessions() {
  return DEFAULT_SESSIONS.map((session) => {
    const sessionId = genUID();
    return {
      ...session,
      href: `/session/${sessionId}`,
      sessionId,
      configs: { ...session.configs, sessionId },
    };
  });
}
