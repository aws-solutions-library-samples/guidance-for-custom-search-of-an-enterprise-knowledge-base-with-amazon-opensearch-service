import { useCallback } from 'react';
import { LSK } from 'src/constants';
import useLsArray from './useLsArray';
import PROMPT_TEMPLATES from 'src/utils/PROMPT_TEMPLATES';
import backup_convo from 'src/utils/backup';

const useLsSessionList = () => {
  const {
    value: lsSessionList,
    setValue: setLsSessionList,
    add: lsAddOneSession,
    clear: lsClearSessionList,
    getById: lsGetOneSession,
    delById: lsDelOneSession,
    updateById: lsUpdateOneSession,
  } = useLsArray(LSK.sessionList, 'sessionId', PROMPT_TEMPLATES);
  // } = useLsArray(LSK.sessionList, 'sessionId', backup_convo);

  const lsAddContentToOneSession = useCallback(
    (sessionId, sessionList, newConvo) => {
      const newSessionList = sessionList.map((s) => {
        if (s.sessionId === sessionId) {
          s.conversations = s.conversations.concat(newConvo);
        }
        return s;
      });
      setLsSessionList(newSessionList);
      return newSessionList;
    },
    []
  );

  const lsUpdateContentOfLastConvoInOneSession = useCallback(
    (sessionId, sessionList, data) => {
      const newSessionList = sessionList.map((s) => {
        if (s.sessionId === sessionId) {
          s.conversations[s.conversations.length - 1].content = data;
        }
        return s;
      });
      setLsSessionList(newSessionList);
      return newSessionList;
    },
    []
  );

  return {
    // NOTE (CAUTION: these functions have to be pure functions wrapped in useCallback WITHOUT any dependencies
    lsAddContentToOneSession,
    lsSessionList,
    setLsSessionList,
    lsAddOneSession,
    lsClearSessionList,
    lsGetOneSession,
    lsDelOneSession,
    lsUpdateOneSession,
    lsUpdateContentOfLastConvoInOneSession,
  };
};

export default useLsSessionList;
