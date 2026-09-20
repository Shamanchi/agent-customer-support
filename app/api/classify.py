"""Classification API endpoint."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.exceptions import ValidationError
from app.core.metrics import classification_confidence, tickets_classified_total
from app.services.classifier import classify_ticket

router = APIRouter(prefix="/classify", tags=["classify"])


class ClassifyRequest(BaseModel):
    """Classification request."""
    text: str = Field(..., min_length=1, max_length=10000)
    language: Optional[str] = Field(default=None, max_length=10)


class ClassifyResponse(BaseModel):
    """Classification response."""
    category: Literal["technical", "billing", "general", "spam", "other"]
    confidence: float = Field(ge=0.0, le=1.0)
    subcategory: Optional[str] = None
    suggested_priority: Literal["low", "medium", "high", "urgent"]


@router.post("", response_model=ClassifyResponse)
async def classify_endpoint(request: ClassifyRequest):
    """Classify a support ticket text."""
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="Text cannot be empty")

    result = await classify_ticket(request.text, request.language)

    # Metrics
    classification_confidence.observe(result["confidence"])
    tickets_classified_total.labels(
        category=result["category"],
        confidence_bucket=_confidence_bucket(result["confidence"]),
    ).inc()

    return ClassifyResponse(**result)


def _confidence_bucket(confidence: float) -> str:
    """Convert confidence to bucket label."""
    if confidence >= 0.9:
        return "high"
    elif confidence >= 0.7:
        return "medium"
    elif confidence >= 0.5:
        return "low"
    return "very_low"