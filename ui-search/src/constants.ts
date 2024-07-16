import { IWorkFLow, SEARCH_ENGINE, WORK_MODE, WORK_MODULE } from './types';

/**
 * localStorage Keys
 */
export const LSK = {
  sessionList: 'sessionList',
  sessionSelected: 'sessionSelected',
  languageModelList: 'languageModelList',
  appConfigs: 'appConfigs',
} as const;

export const OPTIONS_SEARCH_ENGINE = [
  {
    value: SEARCH_ENGINE.opensearch,
    label: 'Open Search',
    description:
      'OpenSearch is an open source, distributed search and analytics suite derived from Elasticsearch.',
  },

  // {
  //   value: SEARCH_ENGINE.kendra,
  //   label: 'Kendra',
  //   description:
  //     'Amazon Kendra is an intelligent search service powered by machine learning (ML)',
  //   disabled: true,
  // },
] as const;

export const DEFAULT_WORK_FLOW: IWorkFLow = [WORK_MODULE.RAG] as const;

export const OPTIONS_WORK_MODE = [
  {
    label: 'Text Search',
    value: WORK_MODE.text,
    description: 'User query -- RAG module',
    workFlow: DEFAULT_WORK_FLOW,
    // description: (
    //   <div style={{ display: 'flex', gap: '12px' }}>
    //     <div
    //       style={{
    //         borderRadius: '8px',
    //         border: '1px solid grey',
    //         padding: '0 6px',
    //       }}
    //     >
    //       User Input
    //     </div>
    //     <div>»</div>
    //     <div
    //       style={{
    //         borderRadius: '8px',
    //         border: '1px solid grey',
    //         padding: '0 6px',
    //       }}
    //     >
    //       RAG Module
    //     </div>
    //   </div>
    // ),
  },
  {
    label: 'Multi-modal',
    value: WORK_MODE.multiModal,
    description: 'User query -- CHAT module -- RAG module',
    workFlow: [WORK_MODULE.CHAT, WORK_MODULE.RAG],
  },
  // {
  //   label: 'Customize',
  //   value: 'customize',
  //   description: 'User can customize their work flow in the future',
  //   workFlow: [],
  //   disabled: true,
  // },
] as const;
export const DEFAULT_WORK_MODE = OPTIONS_WORK_MODE[0].value;
