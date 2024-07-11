/**
 * localStorage Keys
 */
export const LSK = {
  sessionList: 'sessionList',
  sessionSelected: 'sessionSelected',
  languageModelList: 'languageModelList',
  appConfigs: 'appConfigs',
};

export const OPTIONS_SEARCH_ENGINE = [
  {
    value: 'opensearch',
    label: 'Open Search',
    description:
      'OpenSearch is an open source, distributed search and analytics suite derived from Elasticsearch.',
  },
  {
    value: 'kendra',
    label: 'Kendra',
    description:
      'Amazon Kendra is an intelligent search service powered by machine learning (ML)',
  },
];

export const WORK_MODULES = {
  CHAT: 'CHAT',
  RAG: 'RAG',
};
export const DEFAULT_WORK_FLOW = [WORK_MODULES.RAG];

export const OPTIONS_WORK_MODE = [
  {
    label: 'Text Search',
    value: 'text',
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
    value: 'multi-modal',
    description: 'User query -- CHAT module -- RAG module',
    workFlow: [WORK_MODULES.CHAT, WORK_MODULES.RAG],
  },
  {
    label: 'Customize',
    value: 'customize',
    description: 'User can customize their work flow in the future',
    disabled: true,
  },
];
export const DEFAULT_WORK_MODE = OPTIONS_WORK_MODE[0].value;
