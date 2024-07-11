import { createStore } from 'hox';
import { useCallback } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import useLsSessionList from 'src/hooks/useLsSessionList';
import fakeDelay from 'src/utils/FakeDelay';
import genUID from 'src/utils/genUID';

export const [useSessionStore, SessionStoreProvider] = createStore(() => {
  const navigate = useNavigate();
  const { lsSessionList, lsDelOneSession, lsAddOneSession } =
    useLsSessionList();

  /**
   * add a session item in the state as well as in localStorage
   * @param {Object} sessionData
   */
  const addSession = useCallback(
    async (sessionData) => {
      try {
        const id = genUID();
        const name = sessionData?.name || `Session ${id}`;
        const href = `/session/${id}`;
        const processedSessionData = {
          type: 'link',
          href,
          text: name,
          sessionId: id,
          configs: {
            name,
            ...sessionData,
            sessionId: id,
          },
          conversations: [],
          // // TESTING
          // conversations: mockConversations,
        };
        lsAddOneSession(processedSessionData);
        await fakeDelay(200);
        toast.success(`Session ${name} created`);

        navigate(href);
      } catch (error) {
        console.error(error);
      }
    },
    [lsAddOneSession, navigate]
  );

  /**
   * delete a session from the existing sessions state as well as from localStorage
   * @param {String} sessionId
   */
  const delSession = useCallback(
    async (sessionId) => {
      try {
        lsDelOneSession(sessionId);
        toast.success(`Session ${sessionId} deleted`);
      } catch (error) {
        console.error(error);
      }
    },
    [lsDelOneSession]
  );

  return {
    sessionList: lsSessionList,
    addSession,
    delSession,
  };
});
