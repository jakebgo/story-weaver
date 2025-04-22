from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ...services.outline_service import OutlineService
from ...core.auth_middleware import verify_token_middleware
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
outline_service = OutlineService()

class OutlineRequest(BaseModel):
    """Request model for outline generation."""
    segment_ids: List[str]
    prompt: Optional[str] = None

class AnalysisRequest(BaseModel):
    """Request model for transcript analysis."""
    segment_ids: List[str]

@router.post("/generate")
async def generate_outline(
    request: OutlineRequest,
    user: Dict = Depends(verify_token_middleware)
) -> Dict[str, Any]:
    """
    Generate a story outline from the provided segment IDs.
    
    Args:
        request: OutlineRequest containing segment IDs and optional prompt
        user: Authenticated user information
        
    Returns:
        Generated outline as a dictionary
    """
    try:
        logger.info(f"Generating outline for {len(request.segment_ids)} segments")
        logger.debug(f"Segment IDs: {request.segment_ids}")
        
        outline = await outline_service.generate_outline(
            segment_ids=request.segment_ids,
            prompt=request.prompt
        )
        return outline
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating outline: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate outline")

@router.post("/analyze")
async def analyze_transcript(
    request: AnalysisRequest,
    user: Dict = Depends(verify_token_middleware)
) -> Dict[str, Any]:
    """
    Analyze the transcript segments to identify topics, key moments, and key terms.
    
    Args:
        request: AnalysisRequest containing segment IDs to analyze
        user: Authenticated user information
        
    Returns:
        Dict containing the analysis results
    """
    try:
        logger.info(f"Analyzing {len(request.segment_ids)} segments")
        logger.debug(f"Segment IDs: {request.segment_ids}")
        
        analysis = await outline_service.analyze_transcript(request.segment_ids)
        return analysis
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze transcript")

@router.get("/segment/{segment_id}")
async def get_segment(
    segment_id: str,
    user: Dict = Depends(verify_token_middleware)
) -> Dict[str, Any]:
    """
    Retrieve a specific segment by ID.
    
    Args:
        segment_id: The ID of the segment to retrieve
        user: Authenticated user information
        
    Returns:
        Dict containing the segment data
    """
    try:
        logger.info(f"Retrieving segment: {segment_id}")
        
        segment = outline_service.vector_store.get_segment_by_id(segment_id)
        if not segment:
            logger.error(f"Segment not found: {segment_id}")
            raise HTTPException(status_code=404, detail="Segment not found")
            
        return segment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving segment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve segment") 