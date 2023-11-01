import { useCallback } from 'react';
import { LSK } from 'src/constants';
import useLsArray from './useLsArray';

const useLsSessionList = () => {
  const {
    value: lsSessionList,
    setValue: setLsSessionList,
    add: lsAddSessionItem,
    clear: lsClearSessionList,
    getById: lsGetSessionItem,
    delById: lsDelSessionItem,
    updateById: lsUpdateSessionItem,
  } = useLsArray(LSK.sessionList, 'sessionId');

  const lsGetCurSessionConfig = useCallback((sessionId, sessionList) => {
    let configs = null;
    const curSession = lsGetSessionItem(sessionId, sessionList);
    if (curSession) configs = curSession.configs;
    return configs;
  }, []);

  const lsAddContentToSessionItem = useCallback(
    (sessionId, sessionList, newConvo) => {
      const curSession = lsGetSessionItem(sessionId, sessionList);
      if (curSession) {
        curSession.conversations = curSession.conversations.concat(newConvo);
        lsUpdateSessionItem(sessionId, curSession);
        // const { conversations = [] } = curSession;
        // conversations.push(newConvo);
        // lsUpdateSessionItem(sessionId, { ...curSession, conversations });
      } else {
        throw new Error(`No session found with ID: ${sessionId}`);
      }
    },
    []
  );

  return {
    // NOTE (CAUTION: these functions have to be pure functions wrapped in useCallback WITHOUT any dependencies
    lsGetCurSessionConfig,
    lsAddContentToSessionItem,
    lsSessionList,
    setLsSessionList,
    lsAddSessionItem,
    lsClearSessionList,
    lsGetSessionItem,
    lsDelSessionItem,
    lsUpdateSessionItem,
  };
};

export default useLsSessionList;
