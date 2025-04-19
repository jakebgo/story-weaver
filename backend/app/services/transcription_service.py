import os
import tempfile
import aiohttp
import aiofiles
import logging
import time
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from fastapi import HTTPException
import wave
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class TranscriptionError(Exception):
    """Base exception for transcription errors"""
    pass

class AudioValidationError(TranscriptionError):
    """Exception for audio validation errors"""
    pass

class RateLimitError(TranscriptionError):
    """Exception for API rate limit errors"""
    pass

class TranscriptionService:
    def __init__(self):
        self.api_key = os.getenv("GLADIA_API_KEY")
        if not self.api_key:
            logger.error("GLADIA_API_KEY environment variable is not set")
            raise ValueError("GLADIA_API_KEY environment variable is not set")
        
        logger.debug(f"Initialized TranscriptionService with API key: {self.api_key[:8]}...")
        
        self.api_url = "https://api.gladia.io/audio/text/audio-transcription/"
        
        # Configure API parameters
        self.api_params = {
            "language_behaviour": "automatic single language",
            "model_size": "large",
            "diarization": "true",  # String values for form data
            "timestamps": "true",   # String values for form data
            "max_duration": "300",  # String values for form data
            "language": "en"
        }
        logger.debug(f"API parameters configured: {self.api_params}")
        
        # Polling configuration
        self.max_polling_attempts = 30  # 5 minutes with 10-second intervals
        self.polling_interval = 10  # seconds
        
    async def validate_audio(self, audio_data: bytes) -> None:
        """
        Validate the audio file data.
        
        Args:
            audio_data: The audio file data
            
        Raises:
            AudioValidationError: If the audio data is invalid
        """
        logger.debug("Starting audio validation...")
        if not audio_data:
            logger.error("No audio data provided")
            raise AudioValidationError("No audio data provided")
            
        if len(audio_data) > 10 * 1024 * 1024:  # 10MB limit
            logger.error(f"Audio file too large: {len(audio_data)} bytes")
            raise AudioValidationError("Audio file too large (max 10MB)")
            
        if len(audio_data) < 1024:  # 1KB minimum
            logger.error(f"Audio file too small: {len(audio_data)} bytes")
            raise AudioValidationError("Audio file too small (min 1KB)")
            
        # Validate WAV format
        try:
            with io.BytesIO(audio_data) as audio_io:
                with wave.open(audio_io, 'rb') as wav_file:
                    # Check basic WAV properties
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    frame_rate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()
                    duration = n_frames / float(frame_rate)
                    
                    logger.debug(f"WAV properties - Channels: {channels}, Sample width: {sample_width}, "
                               f"Frame rate: {frame_rate}, Duration: {duration:.2f}s")
                    
                    # Validate properties
                    if channels not in [1, 2]:
                        raise AudioValidationError("Audio must be mono or stereo")
                    if sample_width not in [1, 2, 3, 4]:
                        raise AudioValidationError("Invalid sample width")
                    if frame_rate < 8000 or frame_rate > 48000:
                        raise AudioValidationError("Frame rate must be between 8kHz and 48kHz")
                    if duration > 300:  # 5 minutes
                        raise AudioValidationError("Audio duration must be less than 5 minutes")
                    
        except wave.Error:
            logger.error("Invalid WAV format")
            raise AudioValidationError("Invalid WAV format")
        except Exception as e:
            logger.error(f"Error validating WAV file: {str(e)}")
            raise AudioValidationError(f"Error validating WAV file: {str(e)}")
            
        logger.debug(f"Audio validation passed. Size: {len(audio_data)} bytes")
        
    async def save_audio_file(self, audio_data: bytes) -> str:
        """
        Save the audio file temporarily.
        
        Args:
            audio_data: The audio file data
            
        Returns:
            Path to the saved audio file
            
        Raises:
            AudioValidationError: If the audio data is invalid
        """
        try:
            logger.debug("Starting to save audio file...")
            await self.validate_audio(audio_data)
            
            # Create a temporary file with .wav extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            logger.debug(f"Created temporary file: {temp_path}")
            
            # Write the audio data to the temporary file
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(audio_data)
                
            logger.info(f"Audio file saved temporarily at {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to save audio file: {str(e)}", exc_info=True)
            raise AudioValidationError(f"Failed to save audio file: {str(e)}")
            
    async def _handle_api_error(self, response: aiohttp.ClientResponse) -> None:
        """
        Handle API error responses.
        
        Args:
            response: The API response
            
        Raises:
            RateLimitError: If rate limit is exceeded
            TranscriptionError: For other API errors
        """
        error_text = await response.text()
        logger.error(f"Gladia API error: {error_text}")
        
        if response.status == 429:
            raise RateLimitError("API rate limit exceeded. Please try again later.")
        elif response.status == 400:
            raise TranscriptionError(f"Invalid request: {error_text}")
        elif response.status == 401:
            raise TranscriptionError("Invalid API key")
        elif response.status == 403:
            raise TranscriptionError("API key does not have permission to access this resource")
        else:
            raise TranscriptionError(f"Gladia API error: {error_text}")
            
    async def _poll_transcription_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll for transcription status.
        
        Args:
            task_id: The task ID to poll
            
        Returns:
            The transcription result when complete
            
        Raises:
            TranscriptionError: If polling fails or times out
        """
        headers = {"x-gladia-key": self.api_key}
        status_url = f"{self.api_url}/status/{task_id}"
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(self.max_polling_attempts):
                try:
                    logger.debug(f"Polling attempt {attempt + 1}/{self.max_polling_attempts}")
                    async with session.get(status_url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("status")
                            
                            if status == "completed":
                                logger.info("Transcription completed successfully")
                                return result
                            elif status == "failed":
                                error_msg = result.get("error", "Unknown error")
                                logger.error(f"Transcription failed: {error_msg}")
                                raise TranscriptionError(f"Transcription failed: {error_msg}")
                            elif status == "processing":
                                logger.debug("Transcription still processing...")
                                await asyncio.sleep(self.polling_interval)
                            else:
                                logger.warning(f"Unknown status: {status}")
                                await asyncio.sleep(self.polling_interval)
                        else:
                            await self._handle_api_error(response)
                            
                except aiohttp.ClientError as e:
                    logger.error(f"Network error during polling: {str(e)}", exc_info=True)
                    raise TranscriptionError(f"Network error during polling: {str(e)}")
                    
        raise TranscriptionError("Transcription polling timed out")
        
    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe the audio file using Gladia API.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription results with speaker labels and timestamps
            
        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            # Prepare the request
            headers = {
                "x-gladia-key": self.api_key
            }
            
            logger.debug(f"Preparing to transcribe audio file: {audio_path}")
            logger.debug(f"File exists: {os.path.exists(audio_path)}")
            logger.debug(f"File size: {os.path.getsize(audio_path)} bytes")
            
            # Open the audio file
            async with aiofiles.open(audio_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
                
                # Create form data
                data = aiohttp.FormData()
                data.add_field('audio', audio_data, filename='audio.wav', content_type='audio/wav')
                for key, value in self.api_params.items():
                    data.add_field(key, value)
                
                logger.debug("Sending request to Gladia API...")
                logger.debug(f"API URL: {self.api_url}")
                logger.debug(f"Headers: {headers}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_url, headers=headers, data=data) as response:
                        logger.debug(f"Received response with status: {response.status}")
                        
                        if response.status != 200:
                            await self._handle_api_error(response)
                            
                        result = await response.json()
                        logger.debug(f"Raw API response: {result}")
                        
                        # Check if the API returned a task ID for asynchronous processing
                        task_id = result.get("task_id")
                        if task_id:
                            logger.info(f"Received task ID: {task_id}. Starting polling...")
                            result = await self._poll_transcription_status(task_id)
                            
                        return result
                        
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}", exc_info=True)
            raise TranscriptionError(f"Error during transcription: {str(e)}")
            
    async def cleanup_audio_file(self, audio_path: str) -> None:
        """
        Clean up the temporary audio file.
        
        Args:
            audio_path: Path to the audio file to clean up
        """
        try:
            if os.path.exists(audio_path):
                os.unlink(audio_path)
                logger.debug(f"Cleaned up temporary audio file: {audio_path}")
        except Exception as e:
            logger.error(f"Error cleaning up audio file: {str(e)}", exc_info=True)

# Create a singleton instance
transcription_service = TranscriptionService() 