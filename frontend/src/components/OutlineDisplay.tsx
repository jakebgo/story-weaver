import React from 'react';

interface OutlinePoint {
  text: string;
  segment_ids: string[];
}

interface OutlineSection {
  heading: string;
  points: OutlinePoint[];
}

interface Outline {
  title: string;
  sections: OutlineSection[];
}

interface OutlineDisplayProps {
  outline: Outline | null;
  isLoading?: boolean;
  error?: string;
}

export default function OutlineDisplay({ 
  outline, 
  isLoading = false, 
  error
}: OutlineDisplayProps) {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i}>
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="space-y-2">
                  {[1, 2].map((j) => (
                    <div key={j} className="h-3 bg-gray-200 rounded w-3/4"></div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-red-600 mb-4">
          <p className="font-semibold">Error generating outline</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!outline) {
    return null;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">{outline.title}</h2>
      <div className="space-y-6">
        {outline.sections.map((section) => (
          <div key={section.heading} className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-700">{section.heading}</h3>
            <div className="pl-4 space-y-2">
              {section.points.map((point, index) => (
                <p key={index} className="text-gray-700">
                  {point.text}
                </p>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 