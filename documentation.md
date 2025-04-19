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
- Python (FastAPI)
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
- Google Cloud Secret Manager
- Google Cloud Run

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
   - Port: 8000 (development) / 8080 (production)
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

### Google Cloud Run Deployment
The backend is deployed to Google Cloud Run, which provides:
- Automatic scaling
- HTTPS endpoints
- Container-based deployment
- Integration with Google Cloud services

#### Deployment Configuration
1. Docker Configuration:
   - `Dockerfile`: Defines the container image
   - `.dockerignore`: Excludes unnecessary files
   - Base image: Python 3.11-slim
   - Port: 8080 (Cloud Run standard)

2. Cloud Build Configuration:
   - `cloudbuild.yaml`: Automated build and deployment
   - Builds Docker image
   - Pushes to Container Registry
   - Deploys to Cloud Run
   - Sets environment variables

3. Environment Variables:
   - `GOOGLE_CLOUD_PROJECT`: Set automatically
   - Firebase credentials: Managed via Secret Manager
   - Other service credentials: Managed via Secret Manager

4. Deployment Process:
   ```bash
   # Build and deploy using Cloud Build
   gcloud builds submit --config cloudbuild.yaml
   ```

5. Local Testing:
   ```bash
   # Build Docker image locally
   docker build -t story-weaver-api .
   
   # Run container locally
   docker run -p 8080:8080 story-weaver-api
   ```

## Secret Management

### Google Cloud Secret Manager Integration
The application uses Google Cloud Secret Manager to securely store sensitive credentials:

1. Secret Manager Setup:
   - Firebase private key stored as a secret in Secret Manager
   - Secret named `firebase-private-key`
   - Accessible via project ID and secret ID

2. Local Development:
   - Service account created for local development
   - Service account key stored as `local-dev-key.json`
   - Key file added to `.gitignore` to prevent accidental commits
   - Environment variable `GOOGLE_APPLICATION_CREDENTIALS` points to key file

3. Production Deployment:
   - Cloud Run service account granted access to Secret Manager
   - Application automatically uses service account credentials in production
   - No need to manage environment variables for secrets

4. Implementation Details:
   - `secret_manager.py`: Module for retrieving secrets from Secret Manager
   - `firebase_admin.py`: Updated to use Secret Manager for credentials
   - `test_secret_manager.py`: Script to verify Secret Manager integration

5. Security Considerations:
   - Secrets are never stored in code or environment variables
   - Access to secrets is controlled via IAM permissions
   - Local development uses a separate service account with limited permissions
