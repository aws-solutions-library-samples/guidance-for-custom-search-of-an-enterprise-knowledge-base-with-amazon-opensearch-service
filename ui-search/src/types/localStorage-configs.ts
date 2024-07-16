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

export type ILocConfigs = {
  name: string;
  searchEngine: 'opensearch';
  workMode: WORK_MODE;
  workFlowLocal: Array<{ module: WORK_MODULE; systemPrompt: string }>;
  llmData: ILocLlmData;
  role?: string;
  taskDefinition?: string;
  outputFormat?: string;
  language: ILanguageValues;
  isCheckedGenerateReport: boolean;
  isCheckedContext: boolean;
  isCheckedKnowledgeBase: boolean;
  indexName: string; // # can NOT be empty when RAG search
  searchMethod: ISearchMethodValues;
  vecTopK: string | number; //                      #renamedFrom - topK
  txtTopK: string | number; //                #renameFrom - txtDocsNum
  vecDocsScoreThresholds: number;
  txtDocsScoreThresholds: number;
  contextRounds: number;
  isCheckedScoreQA: boolean;
  isCheckedScoreQD: boolean;
  isCheckedScoreAD: boolean;
  isCheckedEditPrompt: true;
  chatSystemPrompt?: string;
  tokenContentCheck?: string;
  responseIfNoDocsFound: string;
  sessionId: GI_UUID;
};

export enum LLM_DATA_TYPE {
  sagemaker = 'sagemaker_endpoint',
  thirdParty = 'third_party_api',
}
export type ILocLlmData = {
  strategyName: string;
  type: LLM_DATA_TYPE;
  embeddingEndpoint: string;
  modelType: ISagemakerModelTypeValues & IThirdPartyApiModelTypeValues;
  modelName: IThirdPartyApiModelNameValues;
  recordId: GI_UUID;
  apiUrl?: GI_Href;
  apiKey?: string;
  secretKey?: string;
};
