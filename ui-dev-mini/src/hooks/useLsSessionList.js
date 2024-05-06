import { useCallback } from 'react'
import { LSK } from 'src/constants'
import useLsArray from './useLsArray'
// import PROMPT_TEMPLATES from 'src/constants/PROMPT_TEMPLATES'
import DEFAULT_SESSION from 'src/constants/DEFAULT_SESSION'

const useLsSessionList = () => {
  const {
    value: lsSessionList,
    setValue: setLsSessionList,
    add: lsAddOneSession,
    clear: lsClearSessionList,
    getById: lsGetOneSession,
    delById: lsDelOneSession,
    updateById: lsUpdateOneSession,
  } = useLsArray(LSK.sessionList, 'sessionId', [DEFAULT_SESSION])

  const lsAddContentToOneSession = useCallback(
    (sessionId, sessionList, newConvo) => {
      const newSessionList = sessionList.map((s) => {
        if (s.sessionId === sessionId) {
          s.conversations = s.conversations.concat(newConvo)
        }
        return s
      })
      setLsSessionList(newSessionList)
      return newSessionList
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

  const lsUpdateContentOfLastConvoInOneSession = useCallback(
    (sessionId, sessionList, data) => {
      const newSessionList = sessionList.map((s) => {
        if (s.sessionId === sessionId) {
          s.conversations[s.conversations.length - 1].content = data
        }
        return s
      })
      setLsSessionList(newSessionList)
      return newSessionList
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

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
  }
}

export default useLsSessionList
