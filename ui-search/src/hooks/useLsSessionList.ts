import { useCallback } from 'react';
import { LSK } from 'src/constants';
import useLsArray from './useLsArray';
import PROMPT_TEMPLATES from 'src/utils/PROMPT_TEMPLATES';
import { ILocConvo, ILocSession } from 'src/types';

const useLsSessionList = () => {
  const {
    value: lsSessionList,
    setValue: setLsSessionList,
    add: lsAddOneSession,
    clear: lsClearSessionList,
    getById: lsGetOneSession,
    delById: lsDelOneSession,
    updateById: lsUpdateOneSession,
  } = useLsArray<ILocSession>(
    LSK.sessionList,
    'sessionId',
    // FIX ME LATER
    PROMPT_TEMPLATES as unknown as ILocSession[]
  );

  const lsAddContentToOneSession = useCallback(
    (sessionId: string, sessionList: ILocSession[], newConvos: ILocConvo[]) => {
      const newSessionList = sessionList.map((s) => {
        if (s.sessionId === sessionId) {
          s.conversations = s.conversations.concat(newConvos);
        }
        return s;
      });
      setLsSessionList(newSessionList);
      return newSessionList;
    },
    []
  );

  const lsUpdateContentOfLastConvoInOneSession = useCallback(
    (
      sessionId: string,
      sessionList: ILocSession[],
      newContent: ILocConvo['content']
    ) => {
      const newSessionList = sessionList.map((s) => {
        if (s.sessionId === sessionId) {
          s.conversations[s.conversations.length - 1].content = newContent;
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
