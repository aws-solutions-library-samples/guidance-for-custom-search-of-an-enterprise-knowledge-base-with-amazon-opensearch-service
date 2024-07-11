import { useCallback, useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { DEFAULT_WORK_FLOW, DEFAULT_WORK_MODE } from 'src/constants';
import useChatModule from './useChatModule';
import useLsSessionList from './useLsSessionList';
import useRAGWebSocket from './useRAGWebSocket';

const useApiOrchestration = (sessionId, resetQuery) => {
  const answerTimer = useRef(Date.now());
  const {
    lsSessionList,
    lsGetOneSession,
    lsAddContentToOneSession,
    setLsSessionList,
  } = useLsSessionList();
  const [configs, setConfigs] = useState();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const { getChatModuleResult } = useChatModule();
  const { socketSendSearch, isWssConnected } = useRAGWebSocket(
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
    curSession.configs.workFlow ||= DEFAULT_WORK_FLOW;
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
    async (query, question) => {
      if (question.length === 0) {
        return toast('Please enter a query to search', { icon: '⚠️' });
      }
      setLoading(true);
      answerTimer.current = Date.now();

      const newConvos = [
        {
          type: 'customer',
          content: { text: query, timestamp: Date.now() },
        },
        {
          type: 'robot',
          content: { text: 'Processing your query...', timestamp: Date.now() },
        },
      ];
      let newSessionList = lsAddContentToOneSession(
        sessionId,
        lsSessionList,
        newConvos
      );

      // // TESTING: bypassing multi-modal process by checking if there's any image in the question
      const isMultiModalQuery = question.some((q) => q.type === 'image');
      // if (!isMultiModalQuery) {
      //   return socketSendSearch(query, question, configs, newSessionList);
      // }

      let newQuery = '';

      const goThroughChatModule = () => {
        if (!configs) return false;
        const {
          workFlow,
          isCheckedTextRAGOnlyOnMultiModal: bypassChat = true,
        } = configs;
        // @ts-ignore
        // TODO: change this to check 'CHAT' in new 4.0 api
        const hasChatInWorkFlow = workFlow?.length > 1;
        if (!hasChatInWorkFlow) return false;
        // if do NOT bypass, always go through chat module
        if (!bypassChat) return true;
        // if bypass, only go through chat module if it's a multi-modal query
        if (isMultiModalQuery) return true;
        return false;
      };

      // TODO: dynamic work flow
      if (goThroughChatModule()) {
        newQuery = await getChatModuleResult({ configs, question });
        if (newQuery) {
          // TODO: add newQuery text to existing user query text
          newSessionList = newSessionList.map((s) => {
            if (s.sessionId === sessionId) {
              s.conversations[s.conversations.length - 2].content.text =
                `${query}\n\nQuery processed by CHAT Module:\n${newQuery}`;
            }
            return s;
          });
          setLsSessionList(newSessionList);
        }
      }
      socketSendSearch(newQuery || query, question, configs, newSessionList);
    },
    [
      lsAddContentToOneSession,
      sessionId,
      lsSessionList,
      configs,
      socketSendSearch,
      getChatModuleResult,
      setLsSessionList,
    ]
  );

  return { handleOnEnterSearch, loading, setLoading, isWssConnected, configs };
};

export default useApiOrchestration;
