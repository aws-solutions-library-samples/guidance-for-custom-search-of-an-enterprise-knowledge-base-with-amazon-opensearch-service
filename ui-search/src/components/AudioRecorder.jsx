import { Button, Spinner } from '@cloudscape-design/components';
import useLsAppConfigs from 'src/hooks/useLsAppConfigs';
import useRecorder from 'src/hooks/useRecorder';

const url = '';
// const url =
//   'https://saz4e0dw21.execute-api.us-east-1.amazonaws.com/prod/asr_processing_job';
const DEFAULT_LANG = 'chinese';

const AudioRecorder = ({
  isRecording,
  setIsRecording,
  setQuery,
  language = DEFAULT_LANG,
}) => {
  const { urlApiGateway } = useLsAppConfigs();
  const { startRecording, stopRecording, waiting } = useRecorder({
    isRecording,
    setIsRecording,
    url: url || `${urlApiGateway}/asr_processing_job`,
    language,
    base64: true,
    processData: (data) => setQuery((prev) => `${prev} ${data}`),
  });

  return (
    <div>
      {isRecording ? (
        <Button onClick={stopRecording}>
          <Spinner /> Recording
        </Button>
      ) : waiting ? (
        <Button disabled>
          <Spinner />
        </Button>
      ) : (
        <Button iconName="microphone" onClick={startRecording} />
      )}
    </div>
  );
};

export default AudioRecorder;
