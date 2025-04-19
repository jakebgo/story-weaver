import os
import requests
from typing import Optional, Dict, Any
import tempfile
import aiofiles
from .secret_manager import get_secret

class TranscriptionService:
    def __init__(self):
        """Initialize the transcription service with API key from Secret Manager."""
        try:
            # Get Gladia API key from Secret Manager
            secrets = get_secret("gladia-api-key")
            self.api_key = secrets.get("api_key")
            if not self.api_key:
                raise ValueError("Gladia API key not found in Secret Manager")
            
            # Set up API endpoint
            self.api_url = "https://api.gladia.io/audio/text/audio-transcription/"
            self.headers = {
                "x-gladia-key": self.api_key
            }
        except Exception as e:
            raise Exception(f"Failed to initialize transcription service: {str(e)}")

    async def save_audio_file(self, audio_data: bytes) -> str:
        """
        Save audio data to a temporary file.
        
        Args:
            audio_data: Raw audio data bytes
            
        Returns:
            Path to the saved temporary file
        """
        try:
            # Create a temporary file with .wav extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            
            # Write the audio data to the file
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(audio_data)
            
            return temp_path
        except Exception as e:
            raise Exception(f"Failed to save audio file: {str(e)}")

    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file using Gladia API.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            # Prepare the files for upload
            files = {
                'audio': ('audio.wav', open(audio_path, 'rb'), 'audio/wav')
            }
            
            # Set up parameters
            params = {
                'language_detection': 'true',
                'speaker_detection': 'true',
                'diarization': 'true',
                'punctuate': 'true',
                'format_text': 'true'
            }
            
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                files=files,
                params=params
            )
            
            # Clean up the temporary file
            os.unlink(audio_path)
            
            # Check response
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            # Parse the response
            result = response.json()
            
            # Return the transcription results
            return {
                "text": result.get("prediction", ""),
                "speakers": result.get("speakers", []),
                "words": [
                    {
                        "text": word.get("word", ""),
                        "start": word.get("start", 0),
                        "end": word.get("end", 0),
                        "speaker": word.get("speaker", ""),
                        "confidence": word.get("confidence", 0)
                    }
                    for word in result.get("words", [])
                ],
                "language": result.get("language", ""),
                "audio_duration": result.get("duration", 0),
                "status": "completed"
            }
            
        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            raise Exception(f"Transcription failed: {str(e)}")

# Create a singleton instance
transcription_service = TranscriptionService() 