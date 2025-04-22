from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..services.outline_service import outline_service
from ..auth import get_current_user
from ..auth.auth_bearer import JWTBearer

router = APIRouter()

class OutlineRequest(BaseModel):
    segment_ids: List[str]
    prompt: Optional[str] = None

class AnalysisRequest(BaseModel):
    segment_ids: List[str]

@router.post("/generate")
async def generate_outline(
    request: OutlineRequest,
    current_user = Depends(get_current_user)
):
    try:
        outline = await outline_service.generate_outline(request.segment_ids)
        return outline
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate outline")

@router.post("/analyze-transcript", dependencies=[Depends(JWTBearer())])
async def analyze_transcript(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze transcript segments to identify topics, key moments, and key terms.
    """
    try:
        analysis = await outline_service.analyze_transcript(
            segment_ids=request.segment_ids
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/segment/{segment_id}", dependencies=[Depends(JWTBearer())])
async def get_segment(segment_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific segment by ID.
    """
    try:
        segment = outline_service.vector_store.get_segment_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        return segment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 