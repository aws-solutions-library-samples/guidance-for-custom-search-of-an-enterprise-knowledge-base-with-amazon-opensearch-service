import {
  ISagemakerModelTypeValues,
  IThirdPartyApiModelNameValues,
  IThirdPartyApiModelTypeValues,
} from 'src/components/LanguageModelStrategy';
import {
  ILanguageValues,
  ISearchMethodValues,
} from 'src/components/ModalCreateSession';

export enum WORK_MODE {
  multiModal = 'multi-modal',
  text = 'text',
}
export enum WORK_MODULE {
  CHAT = 'CHAT',
  RAG = 'RAG',
}
export enum SEARCH_ENGINE {
  opensearch = 'opensearch',
  kendra = 'kendra',
}

export type ILocConfigs = {
  name: string;
  searchEngine: SEARCH_ENGINE;
  workMode: WORK_MODE;
  workFlowLocal: Array<{ module: WORK_MODULE; systemPrompt: string }>;
  llmData: ILocLlmData;
  role?: string;
  taskDefinition?: string;
  outputFormat?: string;
  language: ILanguageValues;
  isCheckedKnowledgeBase: boolean;
  indexName: string; //               # can NOT be empty when RAG search
  searchMethod: ISearchMethodValues;
  vecTopK: string | number; //        # renamedFrom - topK
  txtTopK: string | number; //        # renameFrom - txtDocsNum
  vecDocsScoreThresholds: number;
  txtDocsScoreThresholds: number;
  contextRounds: number;
  isCheckedScoreQA: boolean;
  isCheckedScoreQD: boolean;
  isCheckedScoreAD: boolean;
  chatSystemPrompt?: string;
  responseIfNoDocsFound: string;
  sessionId: GI_UUID;

  // Only Frontend Feature needs the following values
  isCheckedTextRAGOnlyOnMultiModal?: boolean;
  isCheckedEditPrompt: boolean;
};

export enum LLM_DATA_TYPE {
  sagemaker = 'sagemaker_endpoint',
  thirdParty = 'third_party_api',
}

export type ILocLlmData = {
  strategyName: string;
  type: LLM_DATA_TYPE;
  embeddingEndpoint: string;
  sagemakerEndpoint?: string;
  temperature: number;
  maxTokens: number;
  modelType: ISagemakerModelTypeValues | IThirdPartyApiModelTypeValues;
  modelName: IThirdPartyApiModelNameValues;
  recordId: GI_UUID;
  apiUrl?: GI_Href;
  apiKey?: string;
  secretKey?: string;
};
