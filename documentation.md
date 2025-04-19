# Story Weaver Documentation

## Project Overview
Story Weaver is a web application designed to help writers' rooms by automatically transcribing recorded discussions and using AI to generate structured story outlines with links back to the relevant transcript context.

## Core Features
- Audio recording and transcription
- AI-powered transcript analysis
- Interactive transcript correction
- Structured story outline generation
- Clickable links between outline and transcript
- Export capabilities (Text, DOCX)

## Technical Architecture

### Frontend
- React (Vite)
- TypeScript
- Firebase Authentication
- Web Audio API for recording

### Backend
- Python (Flask/FastAPI)
- Firebase Admin SDK
- Transcription API integration
- Sentence-BERT for embeddings
- Qdrant Cloud for vector storage
- LlamaIndex for RAG
- Gemini API for LLM tasks

### External Services
- Firebase Authentication (Spark Plan)
- Transcription API (e.g., Gladia)
- Qdrant Cloud
- Google Gemini API

## Development Workflow
1. User authentication
2. Audio recording
3. Transcription processing
4. Transcript correction
5. AI analysis and outline generation
6. Interactive navigation between outline and transcript
7. Export functionality

## Getting Started
[To be added as development progresses]

## API Documentation
[To be added as endpoints are implemented]

## Environment Setup
[To be added as configuration is established]

## Deployment
[To be added as deployment is configured]
