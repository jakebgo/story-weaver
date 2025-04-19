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

### Firebase Admin SDK Configuration
The backend uses Firebase Admin SDK for authentication and database operations. Setup requires:

1. Service Account Configuration:
   - Download service account JSON from Firebase Console
   - Save as `service-account.json` in backend directory
   - Run `setup_firebase.py` to configure environment variables

2. Environment Variables:
   ```
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY="your-private-key"
   FIREBASE_CLIENT_EMAIL=your-client-email
   FIREBASE_CLIENT_ID=your-client-id
   FIREBASE_CLIENT_X509_CERT_URL=your-client-x509-cert-url
   ```

### Backend Server
The backend server is built with FastAPI and includes:

1. Server Configuration:
   - Host: 0.0.0.0
   - Port: 8000
   - Hot-reloading enabled for development
   - Firebase Admin SDK initialization on startup

2. Development Tools:
   - `setup_firebase.py`: Configures Firebase credentials
   - `test_firebase.py`: Verifies Firebase Admin SDK setup
   - `run.py`: Main server entry point with Firebase initialization

3. Server Features:
   - Automatic Firebase Admin SDK initialization
   - Environment variable validation
   - Error handling for missing credentials
   - Hot-reloading for development

## Deployment
[To be added as deployment is configured]
