"""Response generation API endpoint."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.exceptions import NotFoundError, ValidationError
from app.core.metrics import generation_latency_seconds, tickets_generated_total
from app.services.generator import generate_response

router = APIRouter(prefix="/generate", tags=["generate"])


class GenerateRequest(BaseModel):
    """Generation request."""
    ticket_id: str = Field(..., min_length=1)
    context: Optional[str] = Field(default=None, max_length=5000)
    language: Optional[str] = Field(default=None, max_length=10)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4000)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)


class GenerateResponse(BaseModel):
    """Generation response."""
    response: str
    model: str
    tokens_used: int
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[str] = []


@router.post("", response_model=GenerateResponse)
async def generate_endpoint(request: GenerateRequest):
    """Generate a response for a ticket."""
    import time
    start = time.perf_counter()

    result = await generate_response(
        ticket_id=request.ticket_id,
        context=request.context,
        language=request.language,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    latency = time.perf_counter() - start

    # Metrics
    generation_latency_seconds.observe(latency)
    tickets_generated_total.labels(
        model=result["model"],
        status="success",
    ).inc()

    return GenerateResponse(**result)