import { useCallback, useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import useLsSessionList from './useLsSessionList'
import useRAGWebSocket from './useRAGWebSocket'

let answerTimer = Date.now()

const useApiOrchestration = (sessionId, resetQuery) => {
  const { lsSessionList, lsGetOneSession, lsAddContentToOneSession } =
    useLsSessionList()
  const [configs, setConfigs] = useState()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const { socketSendSearch, isWssConnected } = useRAGWebSocket(
    resetQuery,
    setLoading,
    answerTimer,
  )

  useEffect(() => {
    const curSession = lsGetOneSession(sessionId, lsSessionList)
    if (!curSession) {
      toast(`Session not found with ID: ${sessionId}`)
      navigate('/')
    }
    setConfigs(curSession.configs)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

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
        return toast('Please enter a query to search', { icon: '⚠️' })
      }
      setLoading(true)

      const newConvos = [
        {
          type: 'customer',
          content: { text: query, timestamp: Date.now() },
        },
        {
          type: 'robot',
          content: { text: 'Processing your query...', timestamp: Date.now() },
        },
      ]
      let newSessionList = lsAddContentToOneSession(
        sessionId,
        lsSessionList,
        newConvos,
      )

      socketSendSearch(query, question, configs, newSessionList)
    },
    [
      lsAddContentToOneSession,
      sessionId,
      lsSessionList,
      configs,
      socketSendSearch,
    ],
  )

  return { handleOnEnterSearch, loading, isWssConnected, configs }
}

export default useApiOrchestration
