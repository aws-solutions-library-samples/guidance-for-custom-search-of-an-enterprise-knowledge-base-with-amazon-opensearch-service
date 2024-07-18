import { WSS_MESSAGE } from './api';
import { ILocConfigs } from './localStorage-configs';

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

export enum CONVO_TYPE {
  customer = 'customer',
  robot = 'robot',
}

export type ILocConvoCustomer = {
  type: CONVO_TYPE.customer;
  content: {
    text: string;
    timestamp: GI_Timestamp;
  };
};
export type ILocConvoRobot = {
  type: CONVO_TYPE.robot;
  content: {
    timestamp: GI_Timestamp;
    text: string;
    errorMessage?: string;
    sourceData?: Array<ILocConvoRobotSourceDatum>;
    message?: WSS_MESSAGE;
    // e.g. 1825, this is number in milliseconds
    answerTook?: number;

    /**
     * @deprecated values
     */
    // contentCheckLabel: 'Pass';
    // contentCheckSuggestion: 'Pass';
  };
};

export type ILocConvo = ILocConvoCustomer | ILocConvoRobot;
export type ILocSession = {
  type: 'link';
  /**
   * @href_example '/session/demo_session_3'
   */
  href: string;
  text: string;
  sessionId: GI_UUID;
  configs: ILocConfigs;
  conversations: ILocConvo[];
};
