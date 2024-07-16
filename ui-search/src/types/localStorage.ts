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

export type ILocConvoRobotSourceDatum = {};
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
