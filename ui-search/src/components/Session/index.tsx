import { SpaceBetween } from '@cloudscape-design/components';
import { createContext, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import useLsSessionList from 'src/hooks/useLsSessionList';
import SessionBrief from './SessionBrief';
import SessionChats from './SessionChats';
import SessionInput from './SessionInput';
import { ILocSession } from 'src/types';

export const StreamingContext = createContext(null);

const Session = () => {
  const { sessionId } = useParams();
  const { lsSessionList } = useLsSessionList();
  const [data, setData] = useState<ILocSession>();
  const navigate = useNavigate();
  const [streamingText, setStreamingText] = useState('');
  const [streaming, setStreaming] = useState(false);

  useEffect(() => {
    const sessionData = lsSessionList.find((s) => s.sessionId === sessionId);
    if (sessionData) setData(sessionData);
    else navigate('/');
  }, [lsSessionList, navigate, sessionId]);

  return (
    <StreamingContext.Provider
      value={{ streamingText, setStreamingText, streaming, setStreaming }}
    >
      <SpaceBetween size="l">
        {/* @ts-ignore */}
        <SessionBrief configs={data?.configs} />
        {/* @ts-ignore */}
        <SessionChats conversations={data?.conversations} />
        {data ? <SessionInput /> : null}
      </SpaceBetween>
    </StreamingContext.Provider>
  );
};

export default Session;
