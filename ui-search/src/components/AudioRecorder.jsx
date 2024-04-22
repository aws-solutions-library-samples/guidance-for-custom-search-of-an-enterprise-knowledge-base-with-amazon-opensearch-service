import { Button, Spinner } from '@cloudscape-design/components';
import useRecorder from 'src/hooks/useRecorder';

const url =
  'https://6jk35wanck.execute-api.us-west-2.amazonaws.com/prod/asr_processing_job';

const AudioRecorder = ({ isRecording, setIsRecording, setQuery, language }) => {
  const { startRecording, stopRecording } = useRecorder({
    isRecording,
    setIsRecording,
    url,
    language,
    processData: (data) => setQuery((prev) => `${prev} ${data}`),
  });

  return (
    <div>
      {isRecording ? (
        <Button onClick={stopRecording}>
          <Spinner /> Recording
        </Button>
      ) : (
        <Button iconName="microphone" onClick={startRecording} />
      )}
    </div>
  );
};

export default AudioRecorder;
