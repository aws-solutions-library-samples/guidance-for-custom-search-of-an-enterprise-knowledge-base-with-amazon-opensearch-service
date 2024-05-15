import {
  Button,
  Container,
  FileUpload,
  Input,
  StatusIndicator,
} from '@cloudscape-design/components';
import { useCallback, useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { useParams } from 'react-router-dom';
import { DEFAULT_WORK_MODE } from 'src/constants';
import useApiOrchestration from 'src/hooks/useApiOrchestration';
import styled from 'styled-components';
import AudioRecorder from '../AudioRecorder';
import AutoScrollToDiv from '../AutoScrollToDiv';
import ChatIcon from './ChatIcon';

/**
 * Placeholder string for image in 'query'
 */
const genFileNameTag = (fileName) => `<_${fileName}_>`;
const TEMP_STR = '_#<placeholder>#_';

const SessionInput = () => {
  const { sessionId } = useParams();
  const [query, setQuery] = useState('');
  const [imgArr, setImgArr] = useState([]);
  const [isRecording, setIsRecording] = useState(false);

  const resetQuery = useCallback(() => {
    setQuery('');
    setImgArr([]);
  }, []);
  const { handleOnEnterSearch, configs, loading, isWssConnected } =
    useApiOrchestration(sessionId, resetQuery);
  useEffect(() => {
    return resetQuery;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const [secondsTaken, setSecondsTaken] = useState(0);
  useEffect(() => {
    if (loading) {
      const interval = setInterval(
        () => setSecondsTaken((prev) => prev + 100),
        100
      );
      return () => clearInterval(interval);
    }
    setSecondsTaken(0);
  }, [loading]);

  const inputRef = useRef(null);

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
              disabled={!isWssConnected || loading || isRecording}
              autoFocus
              value={query}
              onChange={({ detail }) => {
                setQuery(detail.value);
              }}
              data-corner-style="rounded"
              placeholder="Search Input"
              // onKeyUp={(e) =>
              //   e.detail.key === 'Enter' ? handleOnEnterSearch(query) : null
              // }
            />
            <div
              style={{
                alignSelf: 'flex-start',
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
              }}
            >
              {imgArr.length
                ? imgArr.map((data, index) => {
                    if (data.type !== 'image') return <div key={index} />;
                    return (
                      <ImageRenderer
                        key={index}
                        data={data}
                        removeImg={() => {
                          setImgArr((prev) =>
                            prev.filter((_, i) => i !== index)
                          );
                          setQuery((prev) =>
                            prev.replace(genFileNameTag(data.fileName), '')
                          );
                          inputRef.current.focus();
                        }}
                      />
                    );
                  })
                : null}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          {
            // @ts-ignore
            configs?.workMode !== DEFAULT_WORK_MODE ? (
              <FileUpload
                // multiple
                // constraintText="File format: txt, csv"
                showFileLastModified
                showFileSize
                showFileThumbnail
                tokenLimit={3}
                accept=".jpg,.png,.jpeg"
                value={[]}
                onChange={({ detail }) => {
                  const file = detail.value[0];
                  const fileName = file.name;
                  inputRef.current.focus();
                  setQuery((prev) => `${prev} ${genFileNameTag(fileName)} `);
                  convertToBase64(file, (base64) => {
                    setImgArr((prev) =>
                      prev.concat({ type: 'image', base64, fileName })
                    );
                  });
                }}
                i18nStrings={{
                  uploadButtonText: (e) => (e ? '' : ''),
                  dropzoneText: (e) =>
                    e ? 'Drop files to upload' : 'Drop file to upload',
                  removeFileAriaLabel: (e) => `Remove file ${e + 1}`,
                  limitShowFewer: 'Show fewer files',
                  limitShowMore: 'Show more files',
                  errorIconAriaLabel: 'Error',
                }}
              />
            ) : null
          }
          <AudioRecorder
            isRecording={isRecording}
            // @ts-ignore
            language={configs?.language}
            setIsRecording={setIsRecording}
            setQuery={setQuery}
          />
          <Button
            variant="primary"
            disabled={!isWssConnected || isRecording}
            loading={loading}
            onClick={() => {
              let tempQ = query?.trim();
              if (!tempQ)
                return toast('Please enter your query first!', { icon: '🦥' });

              const question = [];
              if (imgArr.length) {
                // if images involved: dissect query
                imgArr.forEach(({ base64, fileName }) => {
                  let [item0, item1] = [null, null];
                  if (tempQ) {
                    [item0, item1] = tempQ
                      .replace(genFileNameTag(fileName), TEMP_STR)
                      .split(TEMP_STR);

                    item0 = item0?.trim();
                    item1 = item1?.trim();
                  }
                  if (item0) {
                    question.push({ type: 'text', text: item0.trim() });
                    question.push({ type: 'image', base64 });
                  } else {
                    question.push({ type: 'image', base64 });
                  }
                  tempQ = item1;
                });
              }

              if (tempQ) question.push({ type: 'text', text: tempQ });

              console.warn({ query, question });
              handleOnEnterSearch(query, question);
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
  );
};

export default SessionInput;

const convertToBase64 = (file, cb) => {
  const fileReader = new FileReader();

  fileReader.readAsDataURL(file);

  fileReader.onload = () => {
    const base64 = fileReader.result;
    cb(base64);
  };

  fileReader.onerror = (error) => {
    console.error('Error converting file to base64:', error);
  };
};

const SButton = styled(Button)`
  color: #bfbfbf !important;
  &:hover {
    color: #d80000 !important;
  }
`;

function ImageRenderer({ data, removeImg }) {
  const { fileName, base64 } = data;

  return (
    <div
      style={{
        display: 'flex',
        gap: '6px',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <img
        style={{ height: '100px', width: '100px' }}
        src={base64}
        alt={fileName}
      />
      <span>
        {fileName.slice(0, 10)}
        {fileName.length > 11 ? '...' : ''}
      </span>
      <SButton iconName="remove" variant="icon" onClick={removeImg} />
    </div>
  );
}
