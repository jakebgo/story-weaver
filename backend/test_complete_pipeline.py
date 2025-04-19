import os
import asyncio
import logging
import aiohttp
import numpy as np
import wave
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
import json
import requests
import sounddevice as sd
from scipy.io import wavfile
from gtts import gTTS
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from environment variables."""
    try:
        # Create service account dict from environment variables
        service_account = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
        }
        
        logger.debug("Initializing Firebase Admin SDK with service account...")
        logger.debug(f"Project ID: {service_account['project_id']}")
        logger.debug(f"Client Email: {service_account['client_email']}")
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)
        logger.info("Successfully initialized Firebase Admin SDK")
        return True
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}", exc_info=True)
        return False

def get_test_token():
    """Get a test Firebase ID token for testing purposes."""
    try:
        # Create a custom token for a test user
        test_uid = "test_user_123"
        custom_token = auth.create_custom_token(test_uid)
        logger.debug(f"Created custom token: {custom_token.decode()}")
        
        # Exchange custom token for ID token using Firebase Auth REST API
        api_key = os.getenv("FIREBASE_WEB_API_KEY")
        if not api_key:
            raise ValueError("FIREBASE_WEB_API_KEY environment variable is not set")
            
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
        data = {
            "token": custom_token.decode(),
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        id_token = response.json()["idToken"]
        logger.debug("Successfully exchanged custom token for ID token")
        return id_token
        
    except Exception as e:
        logger.error(f"Error creating test token: {str(e)}")
        raise

async def create_test_audio(file_path: str):
    """Record audio from microphone and save as WAV file."""
    try:
        # Recording parameters
        duration = 5  # seconds
        sample_rate = 44100  # Hz
        channels = 1  # mono
        
        print("Recording will start in 3 seconds...")
        await asyncio.sleep(3)
        print("🎤 Recording... Speak now! (5 seconds)")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype=np.int16
        )
        sd.wait()  # Wait until recording is finished
        
        print("✅ Recording finished!")
        
        # Save as WAV file
        wavfile.write(file_path, sample_rate, recording)
        logger.debug(f"Created test audio file at {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error recording audio: {str(e)}")
        raise

async def test_search_functionality(session: aiohttp.ClientSession, base_url: str, query: str, token: str, limit: int = 5):
    """Test the search endpoint."""
    search_url = f"{base_url}/api/transcription/search"
    params = {"query": query, "limit": limit}
    headers = {"Authorization": f"Bearer {token}"}
    
    async with session.get(search_url, params=params, headers=headers) as response:
        response_json = await response.json()
        logger.debug(f"Search response: {response_json}")
        return response_json

async def test_complete_pipeline():
    """Test the complete transcription and search pipeline."""
    base_url = "http://localhost:8000"
    test_audio_path = "test_audio.wav"
    
    try:
        # Initialize Firebase
        if not initialize_firebase():
            raise Exception("Failed to initialize Firebase")
            
        # Get test token
        test_token = get_test_token()
        logger.debug("Got test token")
        
        # Create test audio file
        await create_test_audio(test_audio_path)
        
        async with aiohttp.ClientSession() as session:
            # Test transcription endpoint
            transcribe_url = f"{base_url}/api/transcription/transcribe"
            
            # Read the audio file
            with open(test_audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Prepare the form data
            form_data = aiohttp.FormData()
            form_data.add_field('audio_file',
                              audio_data,
                              filename='test_audio.wav',
                              content_type='audio/wav')
            
            # Add authorization header
            headers = {"Authorization": f"Bearer {test_token}"}
            
            # Send the request
            async with session.post(transcribe_url, data=form_data, headers=headers) as response:
                response_json = await response.json()
                logger.debug(f"Transcription response: {response_json}")
                
                if response.status != 200:
                    logger.error(f"Transcription failed with status {response.status}")
                    logger.error(f"Response: {response_json}")
                    return
            
            # Test search functionality
            search_result = await test_search_functionality(session, base_url, "test query", test_token)
            logger.debug(f"Search result: {search_result}")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        raise
    finally:
        # Cleanup
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
            logger.debug(f"Cleaned up test audio file: {test_audio_path}")

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline()) 