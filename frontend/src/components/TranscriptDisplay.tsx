import React from 'react';

interface TranscriptDisplayProps {
  transcript: string;
}

export default function TranscriptDisplay({ transcript }: TranscriptDisplayProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Transcript</h2>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <pre className="whitespace-pre-wrap font-sans text-gray-700">
          {transcript}
        </pre>
      </div>
    </div>
  );
} 