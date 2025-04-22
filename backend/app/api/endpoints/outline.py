from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from ...services.outline_service import OutlineService
from ...core.auth_middleware import verify_token_middleware
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
outline_service = OutlineService()

@router.post("/generate")
async def generate_outline(
    segment_ids: str = Query(..., description="Comma-separated list of segment IDs"),
    prompt: Optional[str] = None,
    user: Dict = Depends(verify_token_middleware)
) -> Dict[str, Any]:
    """
    Generate a story outline from the provided segment IDs.
    
    Args:
        segment_ids: Comma-separated list of segment IDs to include in the outline
        prompt: Optional prompt to guide the outline generation
        user: Authenticated user information
        
    Returns:
        Generated outline as a dictionary
    """
    try:
        # Convert comma-separated string to list
        segment_id_list = [id.strip() for id in segment_ids.split(",")]
        logger.info(f"Generating outline for {len(segment_id_list)} segments")
        outline = await outline_service.generate_outline(segment_id_list, prompt)
        return outline
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating outline: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate outline")

@router.post("/analyze")
async def analyze_transcript(
    segment_ids: List[str],
    user: Dict = Depends(verify_token_middleware)
) -> Dict[str, Any]:
    """
    Analyze the transcript segments to identify topics, key moments, and key terms.
    
    Args:
        segment_ids: List of segment IDs to analyze
        user: Authenticated user information
        
    Returns:
        Dict containing the analysis results
    """
    try:
        logger.info(f"Analyzing {len(segment_ids)} segments")
        analysis = await outline_service.analyze_transcript(segment_ids)
        return analysis
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze transcript") 