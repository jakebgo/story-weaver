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
- Firebase Authentication
- Transcription API
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

### Firebase Configuration
1. Project Setup:
   - Create a new Firebase project
   - Enable Authentication (Email/Password)
   - Configure Storage for audio files
   - Set up Security Rules

2. Environment Variables:
   ```
   FIREBASE_PROJECT_ID=<project_id>
   FIREBASE_PRIVATE_KEY_ID=<private_key_id>
   FIREBASE_PRIVATE_KEY=<private_key>
   FIREBASE_CLIENT_EMAIL=<client_email>
   FIREBASE_CLIENT_ID=<client_id>
   FIREBASE_CLIENT_X509_CERT_URL=<cert_url>
   ```

3. Testing:
   - Authentication flow verification
   - Service account access testing
   - Environment variable validation
   - API endpoint functionality
   - Security rules enforcement

### Firebase Service Implementation
The Firebase service is implemented in `backend/app/core/firebase_admin.py` and provides core authentication functionality:

1. Service Structure:
   ```python
   # Core functions
   initialize_firebase() -> bool
   verify_token(token: str) -> dict
   ```

2. Implementation Details:
   - Automatic initialization on module import
   - Environment variable-based configuration
   - Comprehensive error handling and logging
   - Secure token verification
   - Service account credential management

3. Security Features:
   - Private key formatting handling
   - Secure credential storage
   - Token verification with error handling
   - Logging with sensitive data protection
   - Environment variable validation

4. Usage Example:
   ```python
   from app.core.firebase_admin import verify_token
   
   # Verify a Firebase ID token
   try:
       decoded_token = verify_token(id_token)
       user_id = decoded_token.get('uid')
   except ValueError as e:
       # Handle invalid token
   ```

5. Error Handling:
   - Initialization failures
   - Invalid token formats
   - Expired tokens
   - Malformed credentials
   - Network issues

6. Logging:
   - Debug level for initialization
   - Info level for successful operations
   - Error level for failures
   - Sensitive data redaction
   - Stack traces for debugging

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
   FIREBASE_PROJECT_ID=<project_id>
   FIREBASE_PRIVATE_KEY_ID=<private_key_id>
   FIREBASE_PRIVATE_KEY=<private_key>
   FIREBASE_CLIENT_EMAIL=<client_email>
   FIREBASE_CLIENT_ID=<client_id>
   FIREBASE_CLIENT_X509_CERT_URL=<cert_url>
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

### Transcription Pipeline Testing
1. Test Script Implementation:
   ```python
   # Location: backend/test_complete_pipeline.py
   # Tests the complete transcription pipeline including:
   - Firebase authentication
   - Audio recording
   - Transcription service
   - Search functionality
   ```

2. SSL Certificate Setup (macOS):
   ```bash
   # Install Python SSL certificates
   /Applications/Python\ 3.13/Install\ Certificates.command
   ```

3. Pipeline Components:
   - Firebase Admin SDK initialization
   - Custom token generation and verification
   - Audio recording with sounddevice
   - WAV file creation and handling
   - Transcription API integration
   - Search endpoint testing

4. Error Handling:
   - SSL certificate verification
   - API connection issues
   - Authentication failures
   - File handling errors
   - Response validation

5. Testing Process:
   ```bash
   # Start the server
   PYTHONPATH=/path/to/backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   
   # Run the test script
   python test_complete_pipeline.py
   ```

6. Next Steps:
   - Frontend UI integration testing
   - Real-time audio streaming
   - Progress indicators
   - Error handling UI
   - Response visualization

## Audio Recording and Processing Pipeline

### Implementation Details
- Audio recording implemented using MediaRecorder API
- WebM format used for initial recording
- Conversion pipeline:
  1. WebM blob → ArrayBuffer
  2. Audio decoding with Web Audio API
  3. WAV conversion for API compatibility
- Successful transcription integration with backend API

### Current Issues
#### Outline Generation Error
- Error occurs in the following sequence:
  1. Audio recording and conversion successful
  2. Transcription API call successful
  3. Vector store segment creation successful
  4. Outline generation fails with "No valid segments found"

#### Debug Information
- Vector store operations:
  - Collection "story_segments" exists and accessible
  - Segment creation successful (confirmed by logs)
  - Segment retrieval failing
- Error trace:
  ```
  WARNING: Segment with ID not found
  ERROR: Error generating outline: No valid segments found
  ```

#### Technical Investigation Points
1. Vector Store Segment Persistence
   - Verify segment metadata storage
   - Check segment ID generation and mapping
   - Validate vector dimensions match collection configuration

2. Segment Retrieval
   - Confirm segment ID format consistency
   - Verify user context in segment queries
   - Check segment filtering logic

3. Outline Generation
   - Review segment validation criteria
   - Verify minimum segment requirements
   - Check error handling in outline service

### Frontend Component Architecture

#### AudioRecorder Component
The AudioRecorder component handles audio recording, transcription, and outline generation:

1. Props Interface:
   ```typescript
   interface AudioRecorderProps {
     onRecordingComplete: (audioBlob: Blob) => void;
   }
   ```

2. State Management:
   - Recording state and timer
   - Processing and error states
   - Transcript and outline data
   - Segment IDs for transcript management

3. Key Functions:
   - `startRecording()`: Initializes audio recording with WebM format
   - `stopRecording()`: Stops recording and triggers processing
   - `convertToWav()`: Converts WebM audio to WAV format
   - `processRecording()`: Handles transcription and outline generation
   - `handleTranscriptUpdate()`: Manages transcript edits
   - `handleSaveChanges()`: Persists transcript changes

4. Error Handling:
   - Recording permission errors
   - Audio processing errors
   - Transcription service errors
   - Save operation errors

#### TranscriptDisplay Component
The TranscriptDisplay component is implemented as a simple, read-only view of the transcript:
```typescript
interface TranscriptDisplayProps {
  transcript: string;
}

// Displays raw transcript text in a pre-formatted block
// No editing capabilities in MVP phase
export default function TranscriptDisplay({ transcript }: TranscriptDisplayProps)
```

Key Features:
- Raw transcript display with proper whitespace preservation
- Pre-formatted text block with proper font styling
- No editing capabilities (temporarily disabled for MVP)
- Clean, focused presentation of transcript content

#### OutlineDisplay Component
The OutlineDisplay component presents a clean, hierarchical view of the generated outline:
```typescript
interface OutlinePoint {
  text: string;
  segment_ids: string[];  // Reserved for future linking feature
}

interface OutlineSection {
  heading: string;
  points: OutlinePoint[];
}

interface Outline {
  title: string;
  sections: OutlineSection[];
}
```

Key Features:
- Clean hierarchical display of outline sections and points
- No interactive elements in MVP phase
- Maintains semantic structure for future feature additions
- Segment IDs preserved in data structure for future linking capability

### UI Design Decisions
1. MVP Focus:
   - Simplified UI to focus on core functionality
   - Removed editing capabilities to reduce complexity
   - Disabled interactive features (View Source, section collapse) for initial release
   
2. Future Enhancements (Post-MVP):
   - Transcript editing capabilities
   - Interactive outline with source linking
   - Collapsible sections for better navigation
   - Enhanced visualization of transcript-outline relationships

## Outline Generation System

### Architecture
The outline generation system consists of several interconnected components:

1. **OutlineService**: Orchestrates the outline generation process
   - Validates segment IDs against the vector store
   - Formats context for the Gemini API
   - Validates outline structure against JSON schema
   - Implements comprehensive error handling and logging

2. **VectorStore**: Manages segment storage and retrieval
   - Stores text segments with their embeddings
   - Provides efficient retrieval by segment ID
   - Implements batch retrieval for multiple segments
   - Includes proper error handling and logging

3. **EmbeddingService**: Generates embeddings for text segments
   - Uses sentence-transformers with all-MiniLM-L6-v2 model
   - Handles both single and batch text embeddings
   - Returns consistent embedding dimensions
   - Includes proper error handling and logging

4. **GeminiService**: Interfaces with the Gemini API
   - Implements retry mechanism with exponential backoff
   - Validates JSON responses against schema
   - Includes comprehensive error handling
   - Provides detailed logging of operations

### Data Flow
1. User provides segment IDs and optional prompt
2. OutlineService validates segment IDs against VectorStore
3. VectorStore retrieves text segments
4. OutlineService formats context for Gemini API
5. GeminiService generates outline with retries if needed
6. OutlineService validates outline structure
7. Validated outline is returned to user

### Error Handling
The system implements comprehensive error handling at multiple levels:

1. **Segment ID Validation**:
   - Checks existence of each segment ID
   - Logs valid and invalid IDs
   - Returns only valid IDs for processing

2. **Outline Structure Validation**:
   - Uses JSON schema validation
   - Checks required fields and data types
   - Logs validation errors with details

3. **Gemini API Interaction**:
   - Implements retry mechanism with exponential backoff
   - Handles JSON parsing errors
   - Logs raw responses for debugging
   - Returns structured error information

4. **Vector Store Operations**:
   - Handles connection errors
   - Logs retrieval failures
   - Provides fallback mechanisms

### Logging Strategy
The system implements detailed logging throughout the pipeline:

1. **Initialization Logs**:
   - Service startup information
   - Configuration details
   - Connection status

2. **Operation Logs**:
   - Number of segments being processed
   - Segment IDs being used
   - Custom prompts if provided

3. **Error Logs**:
   - Detailed error messages with context
   - Raw response data when parsing fails
   - Validation failures with specific details

4. **Success Logs**:
   - Confirmation of successful operations
   - Summary of processed data
   - Validation results

### JSON Schema
The outline structure is validated against the following schema:

```json
{
  "type": "object",
  "required": ["title", "sections"],
  "properties": {
    "title": {"type": "string"},
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["heading", "points"],
        "properties": {
          "heading": {"type": "string"},
          "points": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["text", "segment_ids"],
              "properties": {
                "text": {"type": "string"},
                "segment_ids": {
                  "type": "array",
                  "items": {"type": "string"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Outline Generation Workflow

1. **Frontend Request Flow**:
   - Audio recording is processed and converted to WAV format
   - Audio is sent to transcription endpoint
   - Segment IDs from transcription are used for outline generation
   - Outline request uses query parameters: `segment_ids` and `prompt`

2. **Backend Processing**:
   - Validates segment IDs against vector store
   - Retrieves text segments using Qdrant
   - Generates outline using Gemini service
   - Returns structured outline with title, sections, and points

3. **Error Handling**:
   - Frontend implements type checking for optional callbacks
   - Backend validates segment IDs and outline structure
   - Comprehensive logging at each step of the process

4. **Integration Points**:
   - Qdrant vector store for segment storage and retrieval
   - Gemini service for outline generation
   - Firebase authentication for user verification
   - WebSocket for real-time updates (optional)

### Development Branch Structure
Current active development is taking place on the following branches:

1. `main`
   - Stable, production-ready code
   - Contains all core infrastructure
   - Recently updated with simplified UI components
   - All authentication and vector store functionality verified

2. `feature/basic-ai-outline` (current)
   - Task 1.6: Basic AI Outline Generation PoC
   - Building on verified vector store functionality
   - Focus on Gemini API integration
   - Target completion: Basic outline generation with RAG

### Vector Store Verification
Recent logs confirm proper functionality of the vector store system:

1. Initialization:
   ```log
   INFO:app.services.vector_store:Successfully initialized Qdrant client
   INFO:app.services.vector_store:Collection story_segments already exists
   ```

2. Embedding Generation:
   ```log
   DEBUG:app.services.embedding_service:Generating embeddings for 1 texts
   DEBUG:app.services.embedding_service:Generated embeddings with shape: (1, 384)
   ```

3. Segment Operations:
   ```log
   INFO:app.services.vector_store:Successfully upserted 1 segments
   DEBUG:app.services.outline_service:Segment <uuid> is valid
   INFO:app.services.vector_store:Retrieved 1 segments by ID
   ```

This verification confirms the vector store is ready for integration with the Gemini-based outline generation system.

### Mock Service Implementation
The mock service implementation provides a testing environment for the outline generation system:

1. MockVectorStore:
   ```python
   class MockVectorStore:
       def __init__(self, test_segment_data, test_segment_ids):
           self.test_segment_data = copy.deepcopy(test_segment_data)
           self.test_segment_ids = test_segment_ids.copy()
           self.segments = {}
           
       def get_segment_by_id(self, segment_id: str) -> Dict[str, Any]:
           # Type checking and validation
           if not isinstance(segment_id, str):
               raise TypeError("Segment ID must be a string")
           if not segment_id:
               raise ValueError("Segment ID cannot be empty")
           return copy.deepcopy(self.segments.get(segment_id))
           
       def get_segments_by_ids(self, segment_ids: List[str]) -> List[Dict[str, Any]]:
           # Input validation and type checking
           if not isinstance(segment_ids, list):
               raise TypeError("Segment IDs must be provided as a list")
           return [copy.deepcopy(self.segments[sid]) for sid in segment_ids if sid in self.segments]
   ```

2. MockOutlineService:
   ```python
   class MockOutlineService:
       def _validate_segment_ids(self, segment_ids: List[str]) -> List[Dict[str, Any]]:
           # Comprehensive validation
           if not isinstance(segment_ids, list):
               raise TypeError("Segment IDs must be provided as a list")
           if not segment_ids:
               raise ValueError("No segment IDs provided")
           
           # UUID format validation
           for sid in segment_ids:
               if not isinstance(sid, str):
                   raise TypeError(f"Invalid segment ID type: {type(sid)}")
               try:
                   uuid.UUID(sid)
               except ValueError:
                   raise ValueError(f"Invalid segment ID format: {sid}")
           
           # Segment retrieval and validation
           valid_segments = self._vector_store.get_segments_by_ids(segment_ids)
           if not valid_segments:
               raise ValueError(f"No valid segments found for IDs: {segment_ids}")
           return valid_segments
   ```

3. Key Features:
   - Deep copy protection for test data
   - Comprehensive input validation
   - UUID format checking for segment IDs
   - Type checking for all parameters
   - Source segment tracking in responses
   - Centralized validation logic
   - Detailed error messages

4. Usage Example:
   ```python
   @pytest.fixture
   def mock_outline_service(test_outline_data, test_analysis_data, test_segment_data, test_segment_ids):
       return MockOutlineService(
           test_outline_data,
           test_analysis_data,
           test_segment_data,
           test_segment_ids
       )
   ```

5. Error Handling:
   - Type validation errors
   - Empty input validation
   - UUID format validation
   - Segment existence validation
   - Data integrity protection

6. Data Protection:
   - Deep copy of all test data
   - Independent copies of segment IDs
   - Protected test data from mutation
   - Secure segment retrieval

7. Response Structure:
   ```python
   {
       "sections": [
           {
               "points": [
                   {
                       "segment_ids": ["uuid1", "uuid2"],
                       "source_segments": ["segment1 text", "segment2 text"]
                   }
               ]
           }
       ]
   }
   ```

## API Request Formats

### Outline Generation

The outline generation endpoint now uses a JSON request body instead of query parameters, following REST best practices:

```json
{
  "segment_ids": ["id1", "id2", "id3"],
  "prompt": "Optional prompt to guide outline generation"
}
```

#### Request Details:
- **Endpoint**: `POST /api/outline/generate`
- **Content-Type**: `application/json`
- **Authentication**: Bearer token required
- **Request Body**:
  - `segment_ids`: Array of segment IDs to include in the outline
  - `prompt`: Optional string to guide the outline generation process

#### Response Format:
```json
{
  "title": "Main title of the outline",
  "sections": [
    {
      "heading": "Section heading",
      "points": [
        {
          "text": "Point description",
          "segment_ids": ["id1", "id2"]
        }
      ]
    }
  ]
}
```

This change improves:
1. Data structure suitability for complex parameters
2. Request size limitations (no URL length constraints)
3. Security (sensitive data not exposed in URL)
4. Future extensibility of the API
