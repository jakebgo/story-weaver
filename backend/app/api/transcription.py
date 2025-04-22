from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from app.core.auth_middleware import get_current_user
from app.services.transcription_service import TranscriptionService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.text_processor import TextProcessor
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    transcription_service: TranscriptionService = Depends(),
    embedding_service: EmbeddingService = Depends(),
    vector_store: VectorStore = Depends(),
    text_processor: TextProcessor = Depends()
):
    try:
        # Get the user ID from the authenticated user
        user_id = user.get('user_id')  # Changed from user.uid to user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        # Read the audio file content
        audio_content = await audio_file.read()
        
        # Transcribe the audio
        transcription = await transcription_service.transcribe(audio_content)
        
        # Process the transcription into segments
        segments = text_processor.process_text(transcription)
        
        # Generate embeddings for all segments at once
        embeddings = embedding_service.embed_texts(segments)
        
        # Generate unique IDs for each segment
        segment_ids = [str(uuid.uuid4()) for _ in segments]
        
        # Prepare metadata for each segment
        metadata = [
            {
                "user_id": user_id,
                "source": audio_file.filename,
                "segment_index": i,
                "total_segments": len(segments)
            }
            for i in range(len(segments))
        ]
        
        # Store all segments in vector DB
        vector_store.upsert_segments(
            segment_ids=segment_ids,
            vectors=embeddings,
            texts=segments,
            metadata=metadata
        )
        
        return {
            "transcription": transcription,
            "segment_ids": segment_ids
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in transcribe_audio endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/search")
async def search_segments(
    query: str,
    limit: int = 10,
    user: dict = Depends(get_current_user),
    embedding_service: EmbeddingService = Depends(),
    vector_store: VectorStore = Depends()
):
    try:
        # Get the user ID from the authenticated user
        user_id = user.get('user_id')  # Changed from user.uid to user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        # Generate embedding for the search query
        query_embedding = embedding_service.embed_texts(query)
        
        # Search the vector store
        results = vector_store.search_similar(
            query_vector=query_embedding,
            limit=limit
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Unexpected error in search_segments endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/save-transcript")
async def save_transcript(
    segment_id: str,
    updated_text: str,
    user: dict = Depends(get_current_user),
    vector_store: VectorStore = Depends(),
    embedding_service: EmbeddingService = Depends()
):
    try:
        # Get the user ID from the authenticated user
        user_id = user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
            
        # Get the existing segment
        segment = vector_store.get_segment_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
            
        # Verify the segment belongs to the user
        if segment.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this segment")
            
        # Generate new embedding for the updated text
        new_embedding = embedding_service.embed_texts(updated_text)
        
        # Update the segment in the vector store
        vector_store.upsert_segments(
            segment_ids=[segment_id],
            vectors=new_embedding,
            texts=[updated_text],
            metadata=[{
                **segment,
                "text": updated_text,
                "updated_at": datetime.now().isoformat()
            }]
        )
        
        return {"status": "success", "message": "Transcript updated successfully"}
        
    except Exception as e:
        logger.error(f"Unexpected error in save_transcript endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") 