# Story Weaver

A web application that helps writers' rooms by automatically transcribing recorded discussions and using AI to generate structured story outlines with links back to the relevant transcript context.

## Project Structure

- `frontend/`: React frontend using Vite
- `backend/`: Python backend using FastAPI

## Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- Firebase account
- Firebase project with Authentication enabled

## Setup

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file based on `.env.example` and fill in your Firebase configuration.

4. Start the development server:
   ```
   npm run dev
   ```

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and fill in your Firebase Admin SDK credentials.

5. Start the development server:
   ```
   python run.py
   ```

## Firebase Setup

1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/)
2. Enable Email/Password authentication
3. Get the Firebase configuration for the frontend
4. Generate a service account key for the backend:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file and use its values in the backend `.env` file

## Development

- Frontend runs on http://localhost:5173
- Backend runs on http://localhost:8000
- API documentation available at http://localhost:8000/docs 