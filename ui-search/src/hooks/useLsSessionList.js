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
      } else {
        throw new Error(`No session found with ID: ${sessionId}`);
      }
    },
    []
  );

  const lsUpdateContentOfLastConvoInOneSessionItem = useCallback(
    (sessionId, sessionList, data, firstStream = false) => {
      const curSession = lsGetSessionItem(sessionId, sessionList);
      if (curSession) {
        if (firstStream) {
          curSession.conversations = curSession.conversations.concat({
            type: 'robot',
            content: data,
          });
          lsUpdateSessionItem(sessionId, curSession);
        } else {
          curSession.conversations[curSession.conversations.length - 1] = {
            type: 'robot',
            content: data,
          };
        }
        // TESTING: see if this works
        // curSession.conversations[curSession.conversations.length - 1].content =
        //   data;
        lsUpdateSessionItem(sessionId, curSession);
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
    lsUpdateContentOfLastConvoInOneSessionItem,
  };
};

export default useLsSessionList;
