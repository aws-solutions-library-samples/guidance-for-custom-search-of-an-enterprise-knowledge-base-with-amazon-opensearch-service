import { useState, useCallback, useEffect } from 'react';
import toast from 'react-hot-toast';

const useRecorder = ({
  isRecording,
  setIsRecording,
  url,
  language = 'chinese',
  processData,
  readAfterRecord = false,
  base64 = false,
}) => {
  // recorder registers and controls the start and stop mechanism
  const [mediaRecorder, setMediaRecorder] = useState(null);
  // the audio stream from the browser, which is used to initiate the recorder
  const [mediaStream, setMediaStream] = useState(null);

  const sendAudioToBackend = useCallback(
    async (audioBlob) => {
      try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.mp3');
        formData.append('language', language);

        const res = await fetch(url, {
          method: 'POST',
          body: formData,
        });

        if (res.ok) {
          console.log('Audio sent successfully');
          const data = res.json();
          processData(data);
        } else {
          throw new Error(res.statusText);
        }
      } catch (error) {
        console.error('Error sending audio: ', error);
        toast.error(
          'Error sending audio: check browser console for more error info!'
        );
        setIsRecording(false);
      }
    },
    [url, processData, setIsRecording, language]
  );

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Store the media stream
      setMediaStream(stream);
      const recorder = new MediaRecorder(stream);
      let chunks = [];

      recorder.addEventListener('dataavailable', (event) => {
        chunks.push(event.data);
      });

      recorder.addEventListener('stop', () => {
        if (!chunks.length) return;
        const blob = new Blob(chunks, { type: 'audio/mp3' });
        sendAudioToBackend(blob);
        chunks = [];

        if (readAfterRecord) {
          const audioUrl = URL.createObjectURL(blob);
          const audio = new Audio(audioUrl);
          audio.play();
        }
      });

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error(
        'Error accessing microphone: check browser console for more error info!'
      );
      setIsRecording(false);
    }
  }, [readAfterRecord, sendAudioToBackend, setIsRecording]);

  const stopRecording = useCallback(() => {
    if (mediaRecorder) {
      mediaRecorder?.stop();
      setIsRecording(false);
    }
    if (mediaStream) {
      // Stop all tracks
      mediaStream.getTracks().forEach((track) => track.stop());
      // Reset the media stream
      setMediaStream(null);
    }
  }, [mediaRecorder, setIsRecording, mediaStream]);

  useEffect(() => {
    // when error occurs, mediaRecorder will stop automatically
    if (!isRecording) mediaRecorder?.stop();
  }, [isRecording, mediaRecorder]);

  return { startRecording, stopRecording };
};

export default useRecorder;
