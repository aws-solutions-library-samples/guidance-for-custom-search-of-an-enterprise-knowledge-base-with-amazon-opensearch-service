import { createStore } from 'hox';
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import useLsSessionList from 'src/hooks/useLsSessionList';
import services from 'src/services';
import fakeDelay from 'src/utils/FakeDelay';
import genUID from 'src/utils/genUID';

export const [useSessionStore, SessionStoreProvider] = createStore(() => {
  const navigate = useNavigate();
  const { lsSessionList, lsDelSessionItem, lsAddSessionItem } =
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
        const { configs, conversations } = sessionData;
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
        lsAddSessionItem(processedSessionData);

        await fakeDelay(200);

        navigate(href);
      } catch (error) {
        console.error(error);
      }
    },
    [lsAddSessionItem, navigate]
  );

  /**
   * delete a session from the existing sessions state as well as from localStorage
   * @param {String} sessionId
   */
  const delSession = useCallback(async (sessionId) => {
    try {
      lsDelSessionItem(sessionId);
    } catch (error) {
      console.error(error);
    }
  }, []);

  return {
    sessionList: lsSessionList,
    addSession,
    delSession,
  };
});

const mockConversations = Array(10)
  .fill()
  .map((_, i) =>
    i % 2 === 0
      ? {
          type: 'customer',
          content: {
            text: 'Enim sunt voluptate sit cupidatat excepteur excepteur consectetur. Do aliqua officia fugiat eiusmod minim incididunt magna non incididunt nostrud qui laborum magna irure.',
            timestamp: '1693884718573',
          },
        }
      : {
          type: 'robot',
          content: {
            text: 'Enim sunt voluptate sit cupidatat excepteur excepteur consectetur. Do aliqua officia fugiat eiusmod minim incididunt magna non incididunt nostrud qui laborum magna irure. Minim laborum anim labore dolor voluptate ad reprehenderit incididunt non cupidatat esse ex nulla. Sint pariatur Lorem esse nulla anim eu aliquip et do laborum eu culpa. Non nostrud occaecat laborum nostrud ullamco elit laboris nostrud nisi.',
            timestamp: '1693884718573',
            scoreQueryAnswer: 0.902,
            link: 'https://#',
            sourceData: [
              {
                id: 'abc',
                title:
                  'Exercitation voluptate enim officia proident elit et laborum quis.',
                scoreQueryDoc: 0.402,
                scoreAnswerDoc: 0.302,
                paragraph:
                  'Deserunt fugiat proident officia ut non reprehenderit velit veniam laborum. Ad sit laboris pariatur nulla tempor Lorem adipisicing. Cupidatat non cupidatat ex ullamco aute. Et culpa anim id deserunt',
              },
              {
                id: 'abcd',
                title:
                  'Exercitation qui ipsum laborum amet sunt magna laborum aliquip.',
                scoreQueryDoc: 0.402,
                scoreAnswerDoc: 0.302,
                paragraph:
                  'Deserunt fugiat proident officia ut non reprehenderit velit veniam laborum. Ad sit laboris pariatur nulla tempor Lorem adipisicing. Cupidatat non cupidatat ex ullamco aute. Et culpa anim id deserunt',
              },
              {
                id: 'abcde',
                title:
                  'Ut cupidatat laborum adipisicing ad irure ut deserunt elit veniam id Lorem.',
                scoreQueryDoc: 0.402,
                scoreAnswerDoc: 0.302,
                paragraph:
                  'Deserunt fugiat proident officia ut non reprehenderit velit veniam laborum. Ad sit laboris pariatur nulla tempor Lorem adipisicing. Cupidatat non cupidatat ex ullamco aute. Et culpa anim id deserunt',
              },
            ],
          },
        }
  );
