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
  IWorkFLow,
  WORK_MODE,
  WORK_MODULE,
} from 'src/types';
import useWss from './useWss';

const useApiOrchestration = (sessionId, resetQuery) => {
  const navigate = useNavigate();
  const answerTimer = useRef(Date.now());
  const { lsSessionList, lsGetOneSession, lsAddContentToOneSession } =
    useLsSessionList();

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
      const commonApiConfigs = {
        query,
        question,
        streaming: true,
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
      };

      switch (workMode) {
        case WORK_MODE.text: {
          // CALL Module: RAG - with text search config format
          const apiConfigs: IWSTextSearch = {
            ...commonApiConfigs,
            workMode,
            module: WORK_MODULE.RAG,
            systemPrompt: getSystemPrompt(WORK_MODULE.RAG, workFlowLocal),
          };

          if (!configs.isCheckedKnowledgeBase) {
            // CALL Module: CHAT - with text search config format
            apiConfigs.module = WORK_MODULE.CHAT;
          }
          socketSendSearch(apiConfigs, newSessionList);
          break;
        }

        case WORK_MODE.multiModal: {
          const apiConfigs: IWSMultiModalSearch = {
            ...commonApiConfigs,
            workMode,
            module: WORK_MODULE.CHAT,
            workFlow: convertLocFlow(workFlowLocal),
            workFlowLocal,
            systemPrompt: getSystemPrompt(WORK_MODULE.CHAT, workFlowLocal),
          };

          const isMultiModalQuery = question.some((q) => q.type === 'image');
          if (isMultiModalQuery) {
            // query contains images: firstly, call CHAT module, then RAG module
            socketSendSearch(apiConfigs, newSessionList);
          } else {
            // text search only
            if (configs.isCheckedTextRAGOnlyOnMultiModal) {
              if (configs.isCheckedKnowledgeBase) {
                // Bypassing CHAT module
                // CALL Module: RAG - with multi-modal search config format
                apiConfigs.workFlow = [WORK_MODULE.RAG];
                apiConfigs.module = WORK_MODULE.RAG;
                apiConfigs.systemPrompt = getSystemPrompt(
                  WORK_MODULE.RAG,
                  workFlowLocal
                );
                socketSendSearch(apiConfigs, newSessionList);
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
              socketSendSearch(apiConfigs, newSessionList);
            }
          }
          break;
        }

        default:
          break;
      }
    },
    [
      lsAddContentToOneSession,
      sessionId,
      lsSessionList,
      configs,
      socketSendSearch,
    ]
  );

  return { handleOnEnterSearch, loading, setLoading, isWssConnected, configs };
};

export default useApiOrchestration;

/**
 * Get system prompt from workFlowLocal in configs
 */
export function getSystemPrompt(
  module: WORK_MODULE,
  workFlowLocal: ILocConfigs['workFlowLocal']
) {
  if (!workFlowLocal || !workFlowLocal[0]?.module) {
    toast(`LocalStorage data ERROR, 'workFlowLocal': ${workFlowLocal}`, {
      icon: '😕',
    });
    return '';
  }
  const flow = workFlowLocal.find((flow) => flow.module === module);
  if (!flow) {
    // toast(
    //   `LocalStorage data corrupted! Can NOT find work flow with module: ${module}`,
    //   { icon: '😕' }
    // );
    return '';
  }
  return flow.systemPrompt;
}

function convertLocFlow(
  workFlowLocal: ILocConfigs['workFlowLocal']
): IWorkFLow {
  return workFlowLocal.map((flow) => flow.module);
}
