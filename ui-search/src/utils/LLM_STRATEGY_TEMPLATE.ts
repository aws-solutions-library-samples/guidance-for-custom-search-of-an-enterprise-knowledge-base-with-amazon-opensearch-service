import { ILocLlmData, LLM_DATA_TYPE } from 'src/types';

const LLM_STRATEGY_TEMPLATE: ILocLlmData[] = [
  {
    strategyName: 'claude3_bge_strategy',
    type: LLM_DATA_TYPE.thirdParty,
    embeddingEndpoint: 'bge-m3-2024-05-15-14-47-26-255-endpoint',
    modelType: 'bedrock',
    temperature: 0.2,
    maxTokens: 2048,
    modelName: 'anthropic.claude-3-sonnet-20240229-v1:0',
    recordId: 'anthropic.claude-3-sonnet-20240229-v1:0-98550',
    apiUrl: '',
    apiKey: '',
    secretKey: '',
  },
];

export default LLM_STRATEGY_TEMPLATE;
