import { ILocConfigs } from './localStorage-configs';

export enum IWebSocketMessage {
  error = 'error',
  streaming = 'streaming',
  streaming_end = 'streaming_end',
}
export type ILocConvoCustomer = {
  type: 'customer';
  content: {
    text: string;
    timestamp: GI_Timestamp;
  };
};

export type ILocConvoRobotSourceDatum = {
  id: GI_UUID;
  title: string;
  source: {
    sources: string;
    sentence: string;
    page: number;
  };
  image: GI_Base64;
  titleLink: GI_Href;
  paragraph: string;
  sentence: string;
  scoreQueryDoc: number;
  scoreAnswerDoc: number;
};

export type ILocConvoRobot = {
  type: 'robot';
  content: {
    timestamp: GI_Timestamp;
    text: string;
    errorMessage?: string;
    sourceData: Array<ILocConvoRobotSourceDatum>;
    message: IWebSocketMessage;
    // e.g. 1825, this is number in milliseconds
    answerTook: number;

    /**
     * @deprecated values
     */
    // contentCheckLabel: 'Pass';
    // contentCheckSuggestion: 'Pass';
  };
};

export type ILocSession = {
  type: 'link';
  /**
   * @example '/session/demo_session_3'
   */
  href: string;
  text: string;
  sessionId: GI_UUID;
  configs: ILocConfigs;
  conversations: Array<ILocConvoCustomer | ILocConvoRobot>;
};
