import { Button, Spinner } from '@cloudscape-design/components';
import useRecorder from 'src/hooks/useRecorder';

const url =
  'https://saz4e0dw21.execute-api.us-east-1.amazonaws.com/prod/asr_processing_job';

const AudioRecorder = ({ isRecording, setIsRecording, setQuery, language }) => {
  const { startRecording, stopRecording, waiting } = useRecorder({
    isRecording,
    setIsRecording,
    url,
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
