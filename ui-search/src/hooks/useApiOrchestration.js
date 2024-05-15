import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { DEFAULT_WORK_FLOW, DEFAULT_WORK_MODE } from 'src/constants';
import useChatModule from './useChatModule';
import useLsSessionList from './useLsSessionList';
import useRAGWebSocket from './useRAGWebSocket';

let answerTimer = Date.now();

const useApiOrchestration = (sessionId, resetQuery) => {
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
      let newQuery = '';

      // TODO: dynamic work flow
      // @ts-ignore
      if (configs?.workFlow?.length > 1) {
        newQuery = await getChatModuleResult({ configs, question });
        if (newQuery) {
          // TODO: add newQuery text to existing user query text
          newSessionList = newSessionList.map((s) => {
            if (s.sessionId === sessionId) {
              s.conversations[
                s.conversations.length - 2
              ].content.text = `${query}\n[ Query processed by CHAT Module: ${newQuery} ]`;
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

  return { handleOnEnterSearch, loading, isWssConnected, configs };
};

export default useApiOrchestration;
