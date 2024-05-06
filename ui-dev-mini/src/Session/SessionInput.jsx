import {
  Button,
  Container,
  Input,
  StatusIndicator,
} from '@cloudscape-design/components'
import { useCallback, useEffect, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import useApiOrchestration from 'src/hooks/useApiOrchestration'
import AutoScrollToDiv from '../AutoScrollToDiv'
import ChatIcon from './ChatIcon'

const sessionId = process.env.REACT_APP_DEFAULT_SESSION_ID ?? '12345'

const SessionInput = () => {
  const [query, setQuery] = useState('')
  const resetQuery = useCallback(() => setQuery(''), [])

  const { handleOnEnterSearch, loading, isWssConnected } = useApiOrchestration(
    sessionId,
    resetQuery,
  )

  useEffect(() => {
    return () => {
      resetQuery()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  const [secondsTaken, setSecondsTaken] = useState(0)
  useEffect(() => {
    if (loading) {
      const interval = setInterval(
        () => setSecondsTaken((prev) => prev + 100),
        100,
      )
      return () => clearInterval(interval)
    }
    setSecondsTaken(0)
  }, [loading])

  const inputRef = useRef(null)

  return (
    <Container>
      <AutoScrollToDiv />
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
        <div style={{ marginTop: '6px' }}>
          <ChatIcon />
        </div>
        <div style={{ flex: 1 }}>
          <div
            style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}
          >
            <Input
              ref={inputRef}
              disabled={!isWssConnected || loading}
              autoFocus
              value={query}
              onChange={({ detail }) => {
                setQuery(detail.value)
              }}
              data-corner-style='rounded'
              placeholder='Search Input'
            />
          </div>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <Button
            variant='primary'
            disabled={!isWssConnected}
            loading={loading}
            onClick={() => {
              let tempQ = query?.trim()
              if (!tempQ)
                return toast('Please enter your query first!', { icon: '🦥' })
              const question = [{ type: 'text', text: tempQ }]
              handleOnEnterSearch(query, question)
            }}
          >
            {loading ? 'Searching' : 'Search'}
          </Button>
        </div>
        <div style={{ minWidth: '50px', marginTop: '6px' }}>
          {loading ? (
            `${Number(secondsTaken / 1000).toFixed(1)} s`
          ) : (
            <StatusIndicator type={isWssConnected ? 'success' : 'stopped'}>
              WSS
            </StatusIndicator>
          )}
        </div>
      </div>
    </Container>
  )
}

export default SessionInput
