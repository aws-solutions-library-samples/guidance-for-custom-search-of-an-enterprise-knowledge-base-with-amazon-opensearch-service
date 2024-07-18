import { ILocConvoRobotSourceDatum } from './localStorage';
import {
  ILocConfigs,
  ILocLlmData,
  WORK_MODE,
  WORK_MODULE,
} from './localStorage-configs';

export enum QUESTION_TYPE {
  text = 'text',
  image = 'image',
}
export type IQuestion =
  | {
      type: QUESTION_TYPE.text;
      text: string;
    }
  | {
      type: QUESTION_TYPE.image;
      base64: GI_Base64;
    };

export type IWSTextSearch = {
  workMode: WORK_MODE.text;
  module: WORK_MODULE;
  systemPrompt: string;
  // common api configs between different work mode
  query: string;
  question: Array<IQuestion>;
  streaming: boolean;
} & Pick<
  ILocConfigs,
  // configs -----------------------
  | 'sessionId'
  | 'contextRounds'
  | 'indexName'
  | 'isCheckedKnowledgeBase'
  | 'isCheckedScoreAD'
  | 'isCheckedScoreQA'
  | 'language'
  | 'responseIfNoDocsFound'
  | 'searchEngine'
  | 'searchMethod'
  | 'vecTopK'
  | 'txtTopK'
  | 'txtDocsScoreThresholds'
  | 'vecDocsScoreThresholds'
> &
  // llmData -----------------------
  ILocLlmData;

export type IWorkFLow = readonly WORK_MODULE[];
export type IWSMultiModalSearch = Omit<IWSTextSearch, 'workMode'> & {
  workMode: WORK_MODE.multiModal;
  workFlow: IWorkFLow;
};

export type IWSSearch = IWSTextSearch | IWSMultiModalSearch;

export enum WSS_MESSAGE {
  streaming = 'streaming',
  streaming_end = 'streaming_end',
  error = 'error',
  success = 'success',
}

export type IWSSourceDatum = ILocConvoRobotSourceDatum;

export type IWSResponse =
  | {
      message: WSS_MESSAGE.streaming;
      moduleCalled: WORK_MODULE;
      text: string;
      timestamp: GI_Timestamp;
    }
  | {
      message: WSS_MESSAGE.streaming_end | WSS_MESSAGE.success;
      moduleCalled: WORK_MODULE;
      modulesLeftToCall: WORK_MODULE[];
      timestamp: GI_Timestamp;
      sourceData: IWSSourceDatum[];
      text: string;
      scoreQueryAnswer: number | string;
    }
  | {
      message: WSS_MESSAGE.error;
      moduleCalled: WORK_MODULE;
      timestamp: GI_Timestamp;
      // the value of these two following keys are the same
      errorMessage: string;
      text: string;
    };
