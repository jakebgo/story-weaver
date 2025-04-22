import React, { useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import TranscriptDisplay from './TranscriptDisplay.tsx';
import OutlineDisplay from './OutlineDisplay.tsx';
import ErrorMessage from './ErrorMessage.tsx';
import LoadingSpinner from './LoadingSpinner.tsx';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  onTranscriptUpdate?: (transcript: string) => void;
  onOutlineUpdate?: (outline: any) => void;
}

export default function AudioRecorder({ 
  onRecordingComplete,
  onTranscriptUpdate,
  onOutlineUpdate 
}: AudioRecorderProps) {
  const { currentUser, logout } = useAuth();
  const [recording, setRecording] = useState(false);
  const [timer, setTimer] = useState(0);
  const timerRef = useRef<number | null>(null);
  const [processing, setProcessing] = useState(false);
  const [transcript, setTranscript] = useState<string>('');
  const [outline, setOutline] = useState<any>(null);
  const [transcriptUpdated, setTranscriptUpdated] = useState(false);
  const [segmentIds, setSegmentIds] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [recordingError, setRecordingError] = useState<string | null>(null);
  const [processingError, setProcessingError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);

  const startRecording = async () => {
    try {
      setRecordingError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('Got audio stream:', stream);
      
      // Create MediaRecorder with specific options
      const options = { mimeType: 'audio/webm' };
      const mediaRecorder = new MediaRecorder(stream, options);
      console.log('Created MediaRecorder with options:', options);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      // Set up data available handler
      mediaRecorder.ondataavailable = (event) => {
        console.log('Data available event fired, data size:', event.data.size);
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      // Start recording with a timeslice to ensure we get data
      mediaRecorder.start(1000); // Collect data every second
      console.log('Started recording');
      
      setRecording(true);
      setTimer(0);
      timerRef.current = window.setInterval(() => setTimer(t => t + 1), 1000);
    } catch (err) {
      console.error('Failed to start recording:', err);
      setRecordingError('Failed to start recording. Please check your microphone permissions and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      console.log('Stopping recording, chunks collected:', audioChunksRef.current.length);
      
      // Request final data chunk
      mediaRecorderRef.current.requestData();
      
      // Stop the recorder
      mediaRecorderRef.current.stop();
      setRecording(false);
      
      if (timerRef.current !== null) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      // Stop all tracks
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      
      // Process the recording after a short delay to ensure all data is collected
      setTimeout(() => {
        processRecording();
      }, 500);
    }
  };

  // Function to convert WebM audio to WAV format
  const convertToWav = async (webmBlob: Blob): Promise<Blob> => {
    console.log('Converting WebM to WAV...');
    
    // Create an audio context
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    audioContextRef.current = audioContext;
    
    // Convert the WebM blob to an ArrayBuffer
    const arrayBuffer = await webmBlob.arrayBuffer();
    console.log('WebM converted to ArrayBuffer, size:', arrayBuffer.byteLength);
    
    try {
      // Decode the audio data
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      console.log('Audio decoded successfully, duration:', audioBuffer.duration);
      
      // Create a WAV file from the audio buffer
      const wavBlob = await audioBufferToWav(audioBuffer);
      
      console.log('Conversion complete, WAV size:', wavBlob.size);
      return wavBlob;
    } catch (error) {
      console.error('Error decoding audio:', error);
      throw new Error('Failed to process audio. The file may be corrupted or in an unsupported format.');
    }
  };

  // Function to convert AudioBuffer to WAV format
  const audioBufferToWav = (buffer: AudioBuffer): Promise<Blob> => {
    return new Promise((resolve) => {
      const numOfChannels = buffer.numberOfChannels;
      const length = buffer.length * numOfChannels * 2;
      const sampleRate = buffer.sampleRate;
      const wavBuffer = new ArrayBuffer(44 + length);
      const view = new DataView(wavBuffer);
      
      // Write WAV header
      writeString(view, 0, 'RIFF');
      view.setUint32(4, 36 + length, true);
      writeString(view, 8, 'WAVE');
      writeString(view, 12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, 1, true);
      view.setUint16(22, numOfChannels, true);
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * numOfChannels * 2, true);
      view.setUint16(32, numOfChannels * 2, true);
      view.setUint16(34, 16, true);
      writeString(view, 36, 'data');
      view.setUint32(40, length, true);
      
      // Write audio data
      const offset = 44;
      const data = new Float32Array(buffer.length);
      const volume = 1;
      let index = 0;
      
      for (let i = 0; i < buffer.numberOfChannels; i++) {
        buffer.copyFromChannel(data, i);
        for (let j = 0; j < data.length; j++) {
          const sample = Math.max(-1, Math.min(1, data[j])) * volume;
          view.setInt16(offset + index, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
          index += 2;
        }
      }
      
      // Create a Blob from the WAV buffer
      const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
      resolve(wavBlob);
    });
  };

  // Helper function to write strings to DataView
  const writeString = (view: DataView, offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const processRecording = async () => {
    if (!currentUser) return;
    setProcessing(true);
    setProcessingError(null);
    try {
      const token = await currentUser.getIdToken();
      console.log('ID Token:', token);
      
      // Check if we have any audio chunks
      if (audioChunksRef.current.length === 0) {
        throw new Error('No audio data collected');
      }
      
      // Combine all audio chunks into a single WebM blob
      const webmBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      console.log('WebM blob size:', webmBlob.size);
      
      if (webmBlob.size === 0) {
        throw new Error('Audio recording is empty');
      }
      
      // Convert WebM to WAV
      const wavBlob = await convertToWav(webmBlob);
      
      // Send the WAV file to the backend
      const formData = new FormData();
      formData.append('audio_file', wavBlob, 'recording.wav');

      const response = await fetch('http://localhost:8000/api/transcription/transcribe', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Transcription failed: ${errorData.detail || response.statusText} (${response.status})`);
      }
      
      const data = await response.json();
      console.log('Transcription response:', data);
      console.log('Segment IDs:', data.segment_ids);
      setTranscript(data.transcription);
      setSegmentIds(data.segment_ids);
      onTranscriptUpdate?.(data.transcription);

      // Generate outline using the new endpoint
      if (!data.segment_ids || data.segment_ids.length === 0) {
        throw new Error('No segment IDs available for outline generation');
      }

      console.log('Sending segment IDs to outline generation:', data.segment_ids);
      const outlineResponse = await fetch(`http://localhost:8000/api/outline/generate?segment_ids=${data.segment_ids.join(',')}&prompt=${encodeURIComponent("Create a detailed outline of the story focusing on key events, characters, and themes.")}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
      
      if (!outlineResponse.ok) {
        const errorData = await outlineResponse.json().catch(() => ({}));
        console.error('Outline generation error details:', errorData);
        throw new Error(`Outline generation failed: ${errorData.detail || outlineResponse.statusText} (${outlineResponse.status})`);
      }
      
      const outlineData = await outlineResponse.json();
      console.log('Outline response:', outlineData);
      setOutline(outlineData);
      onOutlineUpdate?.(outlineData);

      const audioBlob = await convertToWav(webmBlob);
      if (typeof onRecordingComplete === 'function') {
        onRecordingComplete(audioBlob);
      }
    } catch (err) {
      console.error(err);
      setProcessingError(err instanceof Error ? err.message : 'An unexpected error occurred during processing');
    } finally {
      setProcessing(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.error('Failed to log out:', err);
    }
  };

  const handleTranscriptUpdate = (updatedTranscript: string) => {
    setTranscript(updatedTranscript);
    setTranscriptUpdated(true);
  };

  const handleSaveChanges = async () => {
    if (!currentUser || !segmentIds.length) return;
    
    setSaving(true);
    setSaveError(null);
    
    try {
      const token = await currentUser.getIdToken();
      
      // Parse the transcript to get segments
      const segments = transcript.split('\n').map((line, index) => {
        const [speaker, ...textParts] = line.split(':');
        return {
          id: segmentIds[index],
          text: textParts.join(':').trim()
        };
      });
      
      // Save each segment
      const savePromises = segments.map(segment => 
        fetch('http://localhost:8000/api/transcription/save-transcript', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            segment_id: segment.id,
            updated_text: segment.text
          }),
        }).then(response => {
          if (!response.ok) {
            return response.json().then(error => {
              throw new Error(error.detail || 'Failed to save segment');
            });
          }
          return response.json();
        })
      );
      
      await Promise.all(savePromises);
      setTranscriptUpdated(false);
    } catch (err) {
      console.error('Error saving transcript:', err);
      setSaveError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setSaving(false);
    }
  };

  const dismissRecordingError = () => setRecordingError(null);
  const dismissProcessingError = () => setProcessingError(null);
  const dismissSaveError = () => setSaveError(null);

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Story Weaver</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Sign Out
        </button>
      </div>
      
      {recordingError && (
        <ErrorMessage message={recordingError} onDismiss={dismissRecordingError} />
      )}
      
      {processingError && (
        <ErrorMessage message={processingError} onDismiss={dismissProcessingError} />
      )}
      
      {!recording && !processing && !transcript && (
        <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" onClick={startRecording}>
          Start Recording
        </button>
      )}
      
      {recording && (
        <div className="space-y-2">
          <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" onClick={stopRecording}>
            Stop Recording
          </button>
          <p>Recording: {timer}s</p>
        </div>
      )}
      
      {processing && (
        <div className="text-center py-8">
          <LoadingSpinner size="large" text="Processing your recording..." />
        </div>
      )}
      
      {transcript && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <TranscriptDisplay 
            transcript={transcript} 
            onTranscriptUpdate={handleTranscriptUpdate}
          />
          {outline && <OutlineDisplay outline={outline} />}
        </div>
      )}
      
      {transcriptUpdated && (
        <div className="mt-4">
          {saveError && (
            <ErrorMessage message={saveError} onDismiss={dismissSaveError} />
          )}
          
          <button 
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            onClick={handleSaveChanges}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      )}
    </div>
  );
} 