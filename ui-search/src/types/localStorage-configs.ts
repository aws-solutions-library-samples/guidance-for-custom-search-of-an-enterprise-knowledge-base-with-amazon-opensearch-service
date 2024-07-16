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
export enum WORK_FLOW {
  CHAT = 'CHAT',
  RAG = 'RAG',
}

export type ILocConfigs = {
  name: string;
  searchEngine: 'opensearch';
  workMode: WORK_MODE;
  workFlow: Array<WORK_FLOW>;
  llmData: ILocLlmData;
  role?: string;
  taskDefinition?: string;
  outputFormat?: string;
  language: ILanguageValues;
  isCheckedGenerateReport: boolean;
  isCheckedContext: boolean;
  isCheckedKnowledgeBase: boolean;
  indexName: string;
  searchMethod: ISearchMethodValues;
  topK: string | number;
  txtDocsNum: string | number;
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

export type ILocLlmData = {
  strategyName: string;
  type: ILlmDataTYPE;
  embeddingEndpoint: string;
  modelType: ISagemakerModelTypeValues & IThirdPartyApiModelTypeValues;
  modelName: IThirdPartyApiModelNameValues;
  recordId: GI_UUID;
  apiUrl?: GI_Href;
  apiKey?: string;
  secretKey?: string;
};

export enum ILlmDataTYPE {
  sagemaker = 'sagemaker_endpoint',
  thirdParty = 'third_party_api',
}
