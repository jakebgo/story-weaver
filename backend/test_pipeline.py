import os
import asyncio
import aiohttp
import wave
import numpy as np
from dotenv import load_dotenv
import logging
from pathlib import Path
from get_test_token import get_test_token
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_test_audio(duration: float = 3.0, sample_rate: int = 44100) -> str:
    """
    Create a test WAV file with a simple sine wave.
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Path to the created WAV file
    """
    # Generate a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    
    # Convert to 16-bit PCM
    audio_data = (tone * 32767).astype(np.int16)
    
    # Create WAV file
    output_path = "test_audio.wav"
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    logger.info(f"Created test audio file: {output_path}")
    return output_path

async def test_pipeline():
    """Test the complete transcription and embedding pipeline."""
    audio_path = None
    try:
        # Get test token
        test_token = os.environ.get('TEST_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzNDU2Nzg5MCIsInVzZXJuYW1lIjoidGVzdF91c2VyIn0.SIGNATURE')
        logger.info(f"Using test token: {test_token}")
        
        # Create test audio file
        audio_path = create_test_audio()
        logger.info(f"Test audio file created successfully at {os.path.abspath(audio_path)}")
        
        # Send the audio file to the transcription API
        url = "http://localhost:8000/api/transcription/transcribe"
        
        # Create form data with the audio file
        data = aiohttp.FormData()
        data.add_field(
            'file',
            open(audio_path, 'rb'),
            filename='test_audio.wav',
            content_type='audio/wav'
        )
        
        # Add auth header with test token
        headers = {
            "Authorization": f"Bearer {test_token}"
        }
        
        # Send request
        async with aiohttp.ClientSession() as session:
            logger.info(f"Sending request to {url}")
            logger.debug(f"Request headers: {headers}")
            
            async with session.post(url, data=data, headers=headers) as response:
                logger.info(f"Response status: {response.status}")
                logger.debug(f"Response headers: {response.headers}")
                
                response_text = await response.text()
                logger.debug(f"Raw response: {response_text}")
                
                try:
                    response_json = await response.json()
                    logger.info(f"Response JSON: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    logger.error("Failed to parse response as JSON")
                    logger.info(f"Response text: {response_text}")

                if response.status == 200:
                    logger.info("Request successful")
                    
                    # Verify vector store integration
                    if "segment_ids" in response_json:
                        logger.info(f"Successfully stored {len(response_json['segment_ids'])} segments in vector store")
                    else:
                        logger.warning("No segment IDs found in response")
                else:
                    logger.error(f"Request failed with status {response.status}")
        
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)
    finally:
        # Clean up test audio file
        if audio_path and os.path.exists(audio_path):
            logger.info(f"Test audio file is at: {audio_path}")
            os.remove(audio_path)
            logger.info(f"Cleaned up test audio file: {audio_path}")

if __name__ == "__main__":
    asyncio.run(test_pipeline()) 