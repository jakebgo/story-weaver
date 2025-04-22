import React, { useState, useCallback } from 'react';
import AudioRecorder from '../components/AudioRecorder';
import TranscriptDisplay from '../components/TranscriptDisplay';
import ErrorMessage from '../components/ErrorMessage';
import OutlineDisplay from '../components/OutlineDisplay';
import { useAuth } from '../contexts/AuthContext';

interface Outline {
  title: string;
  sections: {
    heading: string;
    points: {
      text: string;
      segment_ids: string[];
    }[];
  }[];
}

export default function StoryPage() {
  const { currentUser } = useAuth();
  const [transcript, setTranscript] = useState<string>('');
  const [outline, setOutline] = useState<Outline | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [segmentIds, setSegmentIds] = useState<string[]>([]);
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false);

  const handleTranscriptUpdate = (newTranscript: string) => {
    setTranscript(newTranscript);
  };

  const generateOutline = useCallback(async () => {
    if (!segmentIds.length) {
      setError('No transcript segments available for outline generation');
      return;
    }

    setIsGeneratingOutline(true);
    setError(null);

    try {
      const response = await fetch('/api/outline/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await currentUser?.getIdToken()}`
        },
        body: JSON.stringify({ segment_ids: segmentIds })
      });

      if (!response.ok) {
        throw new Error('Failed to generate outline');
      }

      const data = await response.json();
      setOutline(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate outline');
    } finally {
      setIsGeneratingOutline(false);
    }
  }, [segmentIds, currentUser]);

  const handleRecordingComplete = async (audioBlob: Blob) => {
    try {
      // The AudioRecorder component handles transcription and outline generation internally
      // We don't need to do anything here since the component manages its own state
      console.log('Recording completed, audio blob:', audioBlob);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error processing recording');
    }
  };

  const processAudioBlob = async (audioBlob: Blob): Promise<string[]> => {
    // This function would handle the actual processing of the audio blob
    // and return the segment IDs. For now, we'll return a mock implementation
    return ['segment1', 'segment2', 'segment3'];
  };

  const dismissError = () => setError(null);

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Record Your Story</h1>
      
      {error && <ErrorMessage message={error} onDismiss={dismissError} />}
      
      <div className="space-y-8">
        <AudioRecorder 
          onRecordingComplete={handleRecordingComplete}
          onTranscriptUpdate={handleTranscriptUpdate}
          onOutlineUpdate={setOutline}
        />
        
        {transcript && (
          <>
            <TranscriptDisplay 
              transcript={transcript}
              onTranscriptUpdate={handleTranscriptUpdate}
            />
            {outline && <OutlineDisplay outline={outline} />}
          </>
        )}
      </div>
    </div>
  );
} 