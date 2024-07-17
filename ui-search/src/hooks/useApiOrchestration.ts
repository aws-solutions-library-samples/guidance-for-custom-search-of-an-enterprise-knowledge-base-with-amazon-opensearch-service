import { useCallback, useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { DEFAULT_WORK_FLOW, DEFAULT_WORK_MODE } from 'src/constants';
import useLsSessionList from './useLsSessionList';
import {
  CONVO_TYPE,
  ILocConfigs,
  IQuestion,
  IWSMultiModalSearch,
  IWSTextSearch,
  WORK_MODE,
  WORK_MODULE,
} from 'src/types';
import useWss from './useWss';

const useApiOrchestration = (sessionId, resetQuery) => {
  const navigate = useNavigate();
  const answerTimer = useRef(Date.now());
  const {
    lsSessionList,
    lsGetOneSession,
    lsAddContentToOneSession,
    setLsSessionList,
  } = useLsSessionList();

  const [configs, setConfigs] = useState<ILocConfigs>();
  const [loading, setLoading] = useState(false);
  const { socketSendSearch, isWssConnected } = useWss(
    resetQuery,
    setLoading,
    answerTimer
  );

  useEffect(() => {
    const curSession = lsGetOneSession(sessionId, lsSessionList);
    if (!curSession) {
      toast(`Session not found with ID: ${sessionId}`);
      navigate('/');
    }
    curSession.configs.workMode ||= DEFAULT_WORK_MODE;
    curSession.configs.workFlowLocal ||= DEFAULT_WORK_FLOW.map((mod) => ({
      module: mod,
      systemPrompt: '',
    }));
    setConfigs(curSession.configs);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  /**
   * @param_example question:
   * [
   *    { type: 'text', text: "What's in this image?" },
   *    { type: 'image', base64: 'iVBORw...' },
   *    { type: 'text', text: 'and in this image' },
   *    { type: 'image', base64: 'iVBORw...' },
   * ],
   */
  const handleOnEnterSearch = useCallback(
    async (query: string, question: IQuestion[]) => {
      if (question.length === 0) {
        return toast('Please enter a query to search', { icon: '⚠️' });
      }
      setLoading(true);
      answerTimer.current = Date.now();

      const newConvos = [
        {
          type: CONVO_TYPE.customer,
          content: { text: query, timestamp: Date.now() },
        },
        {
          type: CONVO_TYPE.robot,
          content: { text: 'Processing your query...', timestamp: Date.now() },
        },
      ];
      let newSessionList = lsAddContentToOneSession(
        sessionId,
        lsSessionList,
        newConvos
      );

      const {
        workMode,
        workFlowLocal,
        contextRounds,
        indexName,
        isCheckedKnowledgeBase,
        isCheckedScoreAD,
        isCheckedScoreQA,
        language,
        responseIfNoDocsFound,
        searchEngine,
        searchMethod,
        vecTopK,
        txtTopK,
        txtDocsScoreThresholds,
        vecDocsScoreThresholds,
        llmData,
      } = configs;
      const commonApiConfigs = { query, question, streaming: true };

      switch (workMode) {
        case WORK_MODE.text: {
          // CALL Module: RAG - with text search config format
          const apiConfigs: IWSTextSearch = {
            workMode,
            module: WORK_MODULE.RAG,
            systemPrompt: getSystemPrompt(WORK_MODULE.RAG, workFlowLocal),
            sessionId,
            contextRounds,
            indexName,
            isCheckedKnowledgeBase,
            isCheckedScoreAD,
            isCheckedScoreQA,
            language,
            responseIfNoDocsFound,
            searchEngine,
            searchMethod,
            vecTopK,
            txtTopK,
            txtDocsScoreThresholds,
            vecDocsScoreThresholds,
            ...llmData,
            ...commonApiConfigs,
          };

          if (!configs.isCheckedKnowledgeBase) {
            // CALL Module: CHAT - with text search config format
            apiConfigs.module = WORK_MODULE.CHAT;
          }
          socketSendSearch(apiConfigs, newSessionList);
          break;
        }

        case WORK_MODE.multiModal: {
          // const apiConfigs: IWSMultiModalSearch = {};

          /**
           * Firstly, call CHAT module, then RAG module
           * @reused in 2 places on multi-modal search
           */
          const callChatThenRAG = () => {
            // CALL module: CHAT
            // pre-process the query/question into {query: 'xxx'} format
          };

          const isMultiModalQuery = question.some((q) => q.type === 'image');
          if (isMultiModalQuery) {
            // query contains images
            callChatThenRAG();
          } else {
            // text search only
            if (configs.isCheckedTextRAGOnlyOnMultiModal) {
              if (configs.isCheckedKnowledgeBase) {
                // CALL Module: RAG - with multi-modal search config format
              } else {
                // This condition should never be matched unless errors in store
                toast(
                  'LocalStorage Error! Please use the latest configs or create a new session. Check console for more info...',
                  { icon: '🫨' }
                );
                console.error({
                  Error_Configs: {
                    configs,
                    isCheckedTextRAGOnlyOnMultiModal:
                      configs.isCheckedTextRAGOnlyOnMultiModal,
                    isCheckedKnowledgeBase: configs.isCheckedKnowledgeBase,
                  },
                });
              }
            } else {
              // Call CHAT module, then RAG module
              callChatThenRAG();
            }
          }
          break;
        }

        default:
          break;
      }

      // // TESTING: bypassing multi-modal process by checking if there's any image in the question
      // const isMultiModalQuery = question.some((q) => q.type === 'image');
      // // if (!isMultiModalQuery) {
      // //   return socketSendSearch(query, question, configs, newSessionList);
      // // }

      // let newQuery = '';

      // const goThroughChatModule = () => {
      //   if (!configs) return false;
      //   const {
      //     workFlow,
      //     isCheckedTextRAGOnlyOnMultiModal: bypassChat = true,
      //   } = configs;
      //   // @ts-ignore
      //   // TODO: change this to check 'CHAT' in new 4.0 api
      //   const hasChatInWorkFlow = workFlow?.length > 1;
      //   if (!hasChatInWorkFlow) return false;
      //   // if do NOT bypass, always go through chat module
      //   if (!bypassChat) return true;
      //   // if bypass, only go through chat module if it's a multi-modal query
      //   if (isMultiModalQuery) return true;
      //   return false;
      // };

      // // TODO: dynamic work flow
      // if (goThroughChatModule()) {
      //   newQuery = await getChatModuleResult({ configs, question });
      //   if (newQuery) {
      //     // TODO: add newQuery text to existing user query text
      //     newSessionList = newSessionList.map((s) => {
      //       if (s.sessionId === sessionId) {
      //         s.conversations[s.conversations.length - 2].content.text =
      //           `${query}\n\nQuery processed by CHAT Module:\n${newQuery}`;
      //       }
      //       return s;
      //     });
      //     setLsSessionList(newSessionList);
      //   }
      // }
      // socketSendSearch(newQuery || query, question, configs, newSessionList);
    },
    [
      lsAddContentToOneSession,
      sessionId,
      lsSessionList,
      configs,
      socketSendSearch,
      setLsSessionList,
    ]
  );

  return { handleOnEnterSearch, loading, setLoading, isWssConnected, configs };
};

export default useApiOrchestration;

/**
 * Get system prompt from workFlowLocal in configs
 */
function getSystemPrompt(
  module: WORK_MODULE,
  workFlowLocal: ILocConfigs['workFlowLocal']
) {
  const flow = workFlowLocal.find((flow) => flow.module === module);
  if (!flow)
    toast(
      `LocalStorage data corrupted! Can NOT find work flow with module: ${module}`
    );
  return flow?.systemPrompt;
}
