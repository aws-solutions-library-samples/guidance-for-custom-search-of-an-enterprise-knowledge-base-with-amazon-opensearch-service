import { useCallback, useContext, useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { StreamingContext } from 'src/components/Session';
import useLsAppConfigs from './useLsAppConfigs';
import useLsSessionList from './useLsSessionList';
import { useParams } from 'react-router-dom';
import {
  CONVO_TYPE,
  ILocSession,
  IWSResponse,
  IWSSearch,
  WSS_MESSAGE,
} from 'src/types';

const GENERAL_WSS_ERROR_MSG = 'Error on receiving Websocket data';

const useWSS = (resetQuery, setLoading, answerTimer) => {
  const { urlWss } = useLsAppConfigs();
  const socket = useRef(null);
  const [isWssConnected, setIsWssConnected] = useState(false);
  const { sessionId } = useParams();
  const { lsUpdateContentOfLastConvoInOneSession, lsAddContentToOneSession } =
    useLsSessionList();

  // NOTE: what to do when websocket connection is established
  const onSocketOpen = useCallback(() => {
    setIsWssConnected(true);
    // socket.current?.send(
    //   JSON.stringify({ action: 'createSession', sessionData })
    // );
  }, []);

  // NOTE: what to do when websocket connection is closed
  const onSocketClose = useCallback(() => {
    setIsWssConnected(false);
  }, []);

  const { setStreaming, setStreamingText } = useContext(StreamingContext);

  // NOTE: what to do when web receives a message from websocket connection
  const onSocketMessage = useCallback(
    (dataStr: string, apiConfigs: IWSSearch, newSessionList: ILocSession[]) => {
      try {
        const data: IWSResponse = JSON.parse(dataStr);

        if (data.message === WSS_MESSAGE.streaming) {
          // TESTING: delete this ls update and update on streaming_end
          lsUpdateContentOfLastConvoInOneSession(
            sessionId,
            newSessionList,
            data
          );
          setStreaming(true);
          setStreamingText(data.text);
          return;
        }

        newSessionList = lsUpdateContentOfLastConvoInOneSession(
          sessionId,
          newSessionList,
          {
            ...data,
            answerTook: Date.now() - answerTimer.current,
          }
        );
        setLoading(false);

        switch (data.message) {
          case WSS_MESSAGE.streaming_end:
            resetQuery();
            setStreamingText(data.text);
            setStreaming(false);
            if (data.modulesLeftToCall.length) {
              const newConvos = [
                {
                  type: CONVO_TYPE.robot,
                  content: {
                    text: 'Processing your query...',
                    timestamp: Date.now(),
                  },
                },
              ];
              const nextSessionList = lsAddContentToOneSession(
                sessionId,
                newSessionList,
                newConvos
              );
              socketSendSearch(apiConfigs, nextSessionList);
            }
            return;
          case WSS_MESSAGE.success:
            resetQuery();
            return;
          case WSS_MESSAGE.error:
            toast.error(
              data.errorMessage || data.text || GENERAL_WSS_ERROR_MSG
            );
            return;
          default:
            resetQuery();
            toast(
              '⚠️ WARNING: WSS data message is not following the api contract'
            );
            return;
        }
      } catch (error) {
        toast.error(error?.message || GENERAL_WSS_ERROR_MSG);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [resetQuery, sessionId]
  );

  const initSocket = useCallback(() => {
    try {
      console.info('init WSS');
      if (!urlWss) throw new Error('urlWss is not defined');

      if (socket.current?.readyState !== WebSocket.OPEN) {
        socket.current = new WebSocket(urlWss);
        socket.current.addEventListener('open', onSocketOpen);
        socket.current.addEventListener('close', onSocketClose);
      }
      return true;
    } catch (error) {
      setIsWssConnected(false);
      console.error(error);
      toast.error(
        error.message ||
          'Websocket connection can NOT be initiated! Please check browser console for more info.'
      );
      return false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlWss, sessionId]);

  useEffect(() => {
    // create websocket connection
    if (socket.current?.readyState !== WebSocket.OPEN) initSocket();
    return () => {
      console.info('WSS closed');
      socket.current?.close();
    };
  }, [initSocket]);

  // NOTE: send query through websocket connection
  const socketSendSearch = useCallback(
    (apiConfigs: IWSSearch, newSessionList: ILocSession[]) => {
      try {
        if (socket.current?.readyState !== WebSocket.OPEN) {
          const success = initSocket();
          if (!success)
            throw new Error('Socket connection can not be established...');
        }

        socket.current.addEventListener('message', (event) =>
          onSocketMessage(event.data, apiConfigs, newSessionList)
        );
        // eslint-disable-next-line react-hooks/exhaustive-deps
        // answerTimer = Date.now();
        socket.current?.send(
          JSON.stringify({ action: 'search', ...apiConfigs })
        );
      } catch (error) {
        console.error('Error socketSendSearch: ', error);
        toast.error(error?.message);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [sessionId, initSocket, onSocketMessage]
  );

  // const onDisconnect = useCallback(() => {
  //   if (isWssConnected) socket.current?.close();
  // }, [isWssConnected]);

  return { isWssConnected, socketSendSearch };
};

export default useWSS;
