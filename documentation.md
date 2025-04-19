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

### Git Workflow
1. Feature branches follow the pattern `feature/<task-name>`
2. Branches are created from and merged back into `main`
3. Each task completion includes:
   - Code implementation
   - Documentation updates
   - Progress tracking
   - Branch cleanup

### Deployment Strategy
1. Local Development:
   - Hot-reloading enabled
   - Environment variables managed via .env
   - Secret Manager integration for credentials
   - Firebase Admin SDK for authentication

2. Production Deployment (Google Cloud Run):
   - Container-based deployment
   - Automated builds via Cloud Build
   - Environment variables managed via Secret Manager
   - Service account-based authentication
   - Automatic scaling and HTTPS

3. Deployment Process:
   ```bash
   # Local testing
   docker build -t story-weaver-api .
   docker run -p 8080:8080 story-weaver-api

   # Production deployment
   gcloud builds submit --config cloudbuild.yaml
   ```

4. Configuration Files:
   - `Dockerfile`: Container configuration
   - `.dockerignore`: Build optimization
   - `cloudbuild.yaml`: Automated deployment
   - Environment-specific configurations

### Security Considerations
1. Credential Management:
   - No secrets in code or environment files
   - Secret Manager for production credentials
   - Local development keys in .gitignore
   - Service account-based access control

2. API Security:
   - Firebase Authentication for user access
   - CORS configuration for frontend access
   - Environment-specific security settings
   - Regular security audits

3. Deployment Security:
   - Container security best practices
   - Minimal base image usage
   - Regular dependency updates
   - Secure environment variable handling

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

### Firebase Web API Key Configuration
The Firebase Web API Key is used for client-side authentication and token verification:

1. Key Location:
   - Stored in `backend/.env` as `FIREBASE_WEB_API_KEY`
   - Used by the frontend for Firebase Authentication
   - Required for token exchange in development testing

2. Usage:
   - Frontend Firebase Authentication
   - Token verification in development
   - API authentication flow
   - Test token generation

3. Security Considerations:
   - Key is public and safe to include in client-side code
   - Protected by Firebase Security Rules
   - Different from Firebase Admin SDK private key
   - Should be included in environment variables for deployment

4. Implementation:
   ```python
   # Example usage in get_test_token.py
   response = requests.post(
       "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken",
       params={"key": os.getenv("FIREBASE_WEB_API_KEY")},
       json={"token": custom_token, "returnSecureToken": True}
   )
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

## Firebase Authentication Testing

### Test User Setup
A test user has been created for development purposes:
- Email: test@example.com
- Password: testpassword123
- UID: zMRHGi6cwJRKwO3lnQLPS0YLBOs1

### Token Generation
Two methods are available for obtaining Firebase ID tokens:

1. Using get-token.html:
   - Located at `frontend/public/get-token.html`
   - Provides a simple UI for token generation
   - Includes copy-to-clipboard functionality
   - Uses Firebase JS SDK directly

2. Using get_test_token.py:
   - Located at `backend/get_test_token.py`
   - Creates/retrieves test user
   - Outputs token generation instructions
   - Useful for backend testing

### Token Usage
The Firebase ID token should be included in API requests as a Bearer token:
```
Authorization: Bearer <token>
```

### Frontend Development
Current frontend setup includes:
- React with Vite
- TypeScript configuration
- Tailwind CSS (configuration in progress)
- Firebase JS SDK integration
- Environment variables for Firebase config

### Known Issues
1. Tailwind CSS Configuration:
   - Current error: PostCSS plugin configuration needs updating
   - Required package: @tailwindcss/postcss
   - Configuration file: postcss.config.js
   - Status: In progress

2. Development Environment:
   - Frontend server needs proper configuration
   - Backend server running with hot-reloading
   - Firebase Authentication working correctly
   - Token generation utilities in place

### Transcription Service
The transcription service handles audio file processing and transcription using the Gladia API:

1. Service Configuration:
   ```python
   class TranscriptionService:
       def __init__(self):
           self.api_key = os.getenv("GLADIA_API_KEY")
           self.api_url = "https://api.gladia.io/audio/text/audio-transcription/"
           self.api_params = {
               "language_behaviour": "automatic single language",
               "model_size": "large",
               "diarization": "true",
               "timestamps": "true",
               "max_duration": "300",
               "language": "en"
           }
   ```

2. Audio Processing Pipeline:
   - File validation (size, format)
   - Temporary file storage
   - API request preparation
   - Response processing
   - Cleanup of temporary files

3. Error Handling:
   - AudioValidationError: Invalid file format or size
   - RateLimitError: API rate limit exceeded
   - TranscriptionError: General transcription failures
   - Network errors and timeouts

4. Response Format:
   ```json
   {
       "success": true,
       "transcript": "Full transcript text",
       "language": "en",
       "duration": 4.972,
       "speakers": ["speaker_1", "speaker_2"],
       "segments": [
           {
               "text": "Segment text",
               "start": 0.124,
               "end": 0.985,
               "speaker": "speaker_1",
               "confidence": 0.142,
               "words": [
                   {
                       "word": "word",
                       "time_begin": 0.124,
                       "time_end": 0.244,
                       "confidence": 0.11
                   }
               ]
           }
       ]
   }
   ```

5. Logging and Monitoring:
   - Detailed debug logging throughout pipeline
   - Error tracking and reporting
   - Performance monitoring
   - API response validation

6. Security Considerations:
   - API key management
   - Temporary file cleanup
   - Input validation
   - Error message sanitization
