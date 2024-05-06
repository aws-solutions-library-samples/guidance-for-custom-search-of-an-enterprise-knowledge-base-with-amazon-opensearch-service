import { AppLayout, Header, SpaceBetween } from '@cloudscape-design/components'
import { createContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useLsSessionList from 'src/hooks/useLsSessionList'
// import SessionBrief from './SessionBrief';
import SessionChats from './SessionChats'
import SessionInput from './SessionInput'

export const StreamingContext = createContext(null)
const sessionId = process.env.REACT_APP_DEFAULT_SESSION_ID ?? '12345'

const Session = () => {
  // const { sessionId } = useParams();
  const { lsSessionList } = useLsSessionList()
  const [data, setData] = useState()
  const navigate = useNavigate()
  const [streamingText, setStreamingText] = useState('')
  const [streaming, setStreaming] = useState(false)

  useEffect(() => {
    const sessionData = lsSessionList.find((s) => s.sessionId === sessionId)
    if (sessionData) setData(sessionData)
    else navigate('/')
  }, [lsSessionList, navigate])

  return (
    <AppLayout
      navigationHide
      toolsHide
      contentHeader={
        <Header>
          {process.env.REACT_APP_WEBSITE_NAME}{' '}
          <small>
            (for websocket api demonstration only - API{' '}
            {process.env.REACT_APP_UI_VERSION})
          </small>
        </Header>
      }
      maxContentWidth={1200}
      minContentWidth={800}
      content={
        <StreamingContext.Provider
          value={{ streamingText, setStreamingText, streaming, setStreaming }}
        >
          <SpaceBetween size='l'>
            {/* <SessionBrief configs={data?.configs} /> */}
            {/* @ts-ignore */}
            <SessionChats conversations={data?.conversations} />
            {data ? <SessionInput /> : null}
          </SpaceBetween>
        </StreamingContext.Provider>
      }
    ></AppLayout>
  )
}

export default Session
