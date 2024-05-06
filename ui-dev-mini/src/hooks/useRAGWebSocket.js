import { useCallback, useContext, useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { StreamingContext } from 'src/Session'
import useLsSessionList from './useLsSessionList'

const GENERAL_WSS_ERROR_MSG = 'Error on receiving Websocket data'
const DEFAULT_SESSION_ID = process.env.REACT_APP_DEFAULT_SESSION_ID ?? ''
const DEFAULT_URL_WSS = process.env.REACT_APP_URL_WSS || ''

const useRAGWebSocket = (
  resetQuery,
  setLoading,
  answerTimer,
  sessionId = DEFAULT_SESSION_ID,
  urlWss = DEFAULT_URL_WSS,
) => {
  const socket = useRef(null)
  const [isWssConnected, setIsWssConnected] = useState(false)
  const { lsUpdateContentOfLastConvoInOneSession } = useLsSessionList()

  // NOTE: what to do when websocket connection is established
  const onSocketOpen = useCallback(() => {
    setIsWssConnected(true)
  }, [])

  // NOTE: what to do when websocket connection is closed
  const onSocketClose = useCallback(() => {
    setIsWssConnected(false)
  }, [])

  const { setStreaming, setStreamingText } = useContext(StreamingContext)

  // NOTE: what to do when web receives a message from websocket connection
  const onSocketMessage = useCallback(
    (dataStr, newSessionList) => {
      try {
        const data = JSON.parse(dataStr)

        if (data.message === 'streaming') {
          lsUpdateContentOfLastConvoInOneSession(
            sessionId,
            newSessionList,
            data,
          )
          setStreaming(true)
          setStreamingText(data.text)
          return
        }

        lsUpdateContentOfLastConvoInOneSession(sessionId, newSessionList, {
          ...data,
          answerTook: Date.now() - answerTimer,
        })
        setLoading(false)

        switch (data.message) {
          case 'streaming_end':
            resetQuery()
            setStreamingText(data.text)
            setStreaming(false)
            return
          case 'success':
            resetQuery()
            return
          case 'error':
            toast.error(data.errorMessage || data.text || GENERAL_WSS_ERROR_MSG)
            return
          default:
            resetQuery()
            toast(
              '⚠️ WARNING: WSS data message is not following the api contract',
            )
            return
        }
      } catch (error) {
        toast.error(error?.message || GENERAL_WSS_ERROR_MSG)
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [resetQuery, sessionId],
  )

  const initSocket = useCallback(() => {
    try {
      console.info('init WSS')
      if (!urlWss) throw new Error('urlWss is not defined')

      if (socket.current?.readyState !== WebSocket.OPEN) {
        socket.current = new WebSocket(urlWss)
        socket.current.addEventListener('open', onSocketOpen)
        socket.current.addEventListener('close', onSocketClose)
      }
      return true
    } catch (error) {
      setIsWssConnected(false)
      console.error(error)
      toast.error(
        error.message ||
          'Websocket connection can NOT be initiated! Please check browser console for more info.',
      )
      return false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlWss, sessionId])

  useEffect(() => {
    // create websocket connection
    if (socket.current?.readyState !== WebSocket.OPEN) {
      initSocket()
    }
    return () => {
      console.info('WSS closed')
      socket.current?.close()
    }
  }, [initSocket])

  // NOTE: send query through websocket connection
  const socketSendSearch = useCallback(
    (query, question, configs, newSessionList) => {
      try {
        if (socket.current?.readyState !== WebSocket.OPEN) {
          const success = initSocket()
          if (!success)
            throw new Error('Socket connection can not be established...')
        }

        socket.current.addEventListener('message', (event) =>
          onSocketMessage(event.data, newSessionList),
        )
        // eslint-disable-next-line react-hooks/exhaustive-deps
        answerTimer = Date.now()
        socket.current?.send(
          JSON.stringify({ action: 'search', configs, query, question }),
        )
      } catch (error) {
        console.error('Error socketSendSearch: ', error)
        toast.error(error?.message)
      }
    },
    [sessionId, initSocket, onSocketMessage],
  )

  return { isWssConnected, socketSendSearch }
}

export default useRAGWebSocket
