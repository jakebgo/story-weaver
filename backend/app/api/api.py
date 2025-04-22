from fastapi import APIRouter
from .transcription import router as transcription_router
from .endpoints.outline import router as outline_router

api_router = APIRouter()

# Include the transcription router
api_router.include_router(
    transcription_router,
    prefix="/transcription",
    tags=["transcription"]
)

# Include the outline router
api_router.include_router(
    outline_router,
    prefix="/outline",
    tags=["outline"]
) 