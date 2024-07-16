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
  query: string;
  question: Array<IQuestion>;
  streaming: boolean;
  systemPrompt: string;
} & Pick<
  ILocConfigs,
  // configs -----------------------
  | 'sessionId'
  | 'contextRounds'
  | 'indexName'
  | 'isCheckedKnowledgeBase'
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

export type IWSMultiModalSearch = Omit<IWSTextSearch, 'workMode'> & {
  workMode: WORK_MODE.multiModal;
  workFlow: Array<WORK_MODULE>;
};

export type IWSSearch = IWSTextSearch | IWSMultiModalSearch;

export enum WS_MESSAGE_TYPE {
  streaming = 'streaming',
  streaming_end = 'streaming_end',
  error = 'error',
}

export type IWSSourceDatum = ILocConvoRobotSourceDatum;

export type IWSResponse =
  | {
      message: WS_MESSAGE_TYPE.streaming;
      moduleCalled: WORK_MODULE;
      text: string;
    }
  | {
      message: WS_MESSAGE_TYPE.streaming_end;
      moduleCalled: WORK_MODULE;
      modulesLeftToCall: WORK_MODULE[];
      timestamp: GI_Timestamp;
      sourceData: IWSSourceDatum[];
      text: string;
      scoreQueryAnswer: number | string;
    }
  | {
      message: WS_MESSAGE_TYPE.error;
      moduleCalled: WORK_MODULE;
      timestamp: GI_Timestamp;
      // the value of these two following keys are the same
      errorMessage: string;
      text: string;
    };
