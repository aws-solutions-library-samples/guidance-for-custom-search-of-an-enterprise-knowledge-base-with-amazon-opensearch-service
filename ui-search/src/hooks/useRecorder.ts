import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';

interface IUseRecorderProps {
  isRecording: boolean;
  setIsRecording: (boolean) => void;
  url: string;
  language?: string | 'chinese' | 'english';
  processData: (data: string) => void;
  readAfterRecord?: boolean;
  base64?: boolean;
}

const useRecorder = ({
  isRecording,
  setIsRecording,
  url,
  language = 'chinese',
  processData,
  readAfterRecord = false,
  base64 = false,
}: IUseRecorderProps) => {
  // recorder registers and controls the start and stop mechanism
  const [mediaRecorder, setMediaRecorder] = useState(null);
  // the audio stream from the browser, which is used to initiate the recorder
  const [mediaStream, setMediaStream] = useState(null);
  const [waiting, setWaiting] = useState(false);

  const sendAudioToBackend = useCallback(
    async (audioBlob) => {
      setWaiting(true);
      try {
        let res = null;
        if (base64) {
          const base64 = await blobToBase64(audioBlob);
          res = await fetch(url, {
            method: 'POST',
            body: JSON.stringify({ audio: base64, language }),
          });
        } else {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.mp3');
          formData.append('language', language);
          res = await fetch(url, { method: 'POST', body: formData });
        }

        if (res.ok) {
          console.info('Audio sent successfully');
          const data = await res.json();
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
      } finally {
        setWaiting(false);
      }

      function blobToBase64(blob) {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(blob);
          // @ts-ignore
          reader.onload = () => resolve(reader.result.split(',')[1]);
          reader.onerror = (error) => reject(error);
        });
      }
    },
    [language, base64, url, processData, setIsRecording]
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

  return { startRecording, stopRecording, waiting };
};

export default useRecorder;
