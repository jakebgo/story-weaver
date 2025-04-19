import os
import asyncio
import aiohttp
import json
import logging
from dotenv import load_dotenv
from get_test_token import get_test_token

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS.mmm format."""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"

async def test_transcription():
    """Test the transcription endpoint with a sample audio file."""
    
    # Get Firebase ID token
    token = get_test_token()
    if not token:
        logger.error("Failed to get Firebase ID token")
        return
        
    # API endpoint
    url = "http://localhost:8001/api/transcription/transcribe"
    
    # Headers with authentication
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test audio file path (you'll need to provide a sample audio file)
    audio_path = "test_audio.wav"
    
    if not os.path.exists(audio_path):
        logger.error(f"Error: Test audio file not found at {audio_path}")
        logger.error("Please provide a WAV file for testing")
        return
    else:
        logger.info(f"Found test audio file at {audio_path}")
        logger.info(f"File size: {os.path.getsize(audio_path)} bytes")
        
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('audio_file',
                         open(audio_path, 'rb'),
                         filename='test_audio.wav',
                         content_type='audio/wav')
            
            logger.info("Sending request to transcription endpoint...")
            logger.debug(f"Request headers: {headers}")
            logger.debug("Request data: FormData with audio_file field")
            
            async with session.post(url, headers=headers, data=data) as response:
                logger.info(f"Response status: {response.status}")
                response_text = await response.text()
                logger.info(f"Response body: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    print("\nTranscription successful!")
                    print("\nLanguage:", result["language"])
                    print("Duration:", format_time(result["duration"]))
                    print("\nFull transcript:", result["transcript"])
                    
                    if result["speakers"]:
                        print("\nDetected speakers:", ", ".join(result["speakers"]))
                    else:
                        print("\nNo speaker diarization available")
                    
                    print("\nSegments:")
                    for segment in result["segments"]:
                        print(f"\n[{format_time(segment['start'])} - {format_time(segment['end'])}] ", end="")
                        print(f"Speaker: {segment['speaker']} ", end="")
                        print(f"(Confidence: {segment['confidence']:.2%})")
                        print(f"Text: {segment['text']}")
                        
                        print("Words:")
                        for word in segment["words"]:
                            print(f"  {word['word']} ", end="")
                            print(f"[{format_time(word['time_begin'])} - {format_time(word['time_end'])}] ", end="")
                            print(f"(Confidence: {word['confidence']:.2%})")
                else:
                    print(f"\nError: {response.status}")
                    print(response_text)
                    
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_transcription()) 