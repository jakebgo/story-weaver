from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Security
from fastapi.responses import JSONResponse
from ..core.auth_middleware import verify_token_middleware
from ..services.transcription_service import (
    transcription_service,
    TranscriptionError,
    AudioValidationError,
    RateLimitError
)
from typing import Dict, Any
import logging
import traceback
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    user = Security(verify_token_middleware)
) -> Dict[str, Any]:
    """
    Transcribe an audio file with speaker detection and timestamps.
    
    Args:
        audio_file: The audio file to transcribe (WAV format recommended)
        user: The authenticated user (from middleware)
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if transcription was successful
        - transcript: Full transcript text
        - language: Detected language code
        - duration: Audio duration in seconds
        - speakers: List of detected speakers
        - segments: List of transcript segments with:
            - text: Segment text
            - start: Start time in seconds
            - end: End time in seconds
            - speaker: Speaker identifier
            
    Raises:
        HTTPException:
            - 400: Invalid audio file
            - 413: Audio file too large
            - 429: Rate limit exceeded
            - 500: Transcription service error
    """
    start_time = time.time()
    audio_path = None
    try:
        user_id = user.uid  # Get the user ID from the authenticated user
            
        logger.info(f"Received transcription request from user {user_id}")
        logger.debug(f"Audio file details - filename: {audio_file.filename}, content_type: {audio_file.content_type}")
        
        # More lenient content type check
        if audio_file.content_type and not (
            audio_file.content_type.startswith('audio/') or 
            'wav' in audio_file.content_type.lower() or
            audio_file.filename.lower().endswith('.wav')
        ):
            logger.error(f"Invalid content type: {audio_file.content_type}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only audio files are accepted."
            )
            
        # Read the audio file
        logger.debug("Reading audio file data...")
        audio_data = await audio_file.read()
        logger.debug(f"Read {len(audio_data)} bytes of audio data")
        
        # Save and transcribe the audio
        logger.debug("Saving audio file...")
        try:
            audio_path = await transcription_service.save_audio_file(audio_data)
            logger.debug(f"Audio saved to {audio_path}")
        except AudioValidationError as e:
            logger.error(f"Audio validation error: {str(e)}")
            if "too large" in str(e):
                raise HTTPException(status_code=413, detail=str(e))
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error saving audio file: {str(e)}")
        
        logger.debug("Starting transcription...")
        try:
            result = await transcription_service.transcribe_audio(audio_path)
            logger.debug(f"Transcription result: {result}")
        except RateLimitError as e:
            logger.error(f"Rate limit error: {str(e)}")
            raise HTTPException(status_code=429, detail=str(e))
        except TranscriptionError as e:
            logger.error(f"Transcription error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")
        
        processing_time = time.time() - start_time
        logger.info(f"Transcription completed for user {user_id} in {processing_time:.2f} seconds")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during transcription: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during transcription: {str(e)}"
        )
    finally:
        # Clean up the temporary audio file
        if audio_path:
            await transcription_service.cleanup_audio_file(audio_path) 