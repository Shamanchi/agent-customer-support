"""Escalation API endpoint."""
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.exceptions import NotFoundError
from app.core.metrics import tickets_escalated_total
from app.services.escalation import escalate_ticket

router = APIRouter(prefix="/escalate", tags=["escalate"])


class EscalateRequest(BaseModel):
    """Escalation request."""
    ticket_id: str = Field(..., min_length=1)
    reason: Literal["low_confidence", "complex_issue", "customer_request", "policy_violation", "other"]
    details: Optional[str] = Field(default=None, max_length=2000)
    assigned_to: Optional[str] = Field(default=None, max_length=100)
    priority: Literal["low", "medium", "high", "urgent"] = "medium"


class EscalateResponse(BaseModel):
    """Escalation response."""
    ticket_id: str
    escalation_id: str
    status: str
    assigned_to: Optional[str]
    priority: str
    created_at: str


@router.post("", response_model=EscalateResponse)
async def escalate_endpoint(request: EscalateRequest):
    """Escalate a ticket to a human operator."""
    result = await escalate_ticket(
        ticket_id=request.ticket_id,
        reason=request.reason,
        details=request.details,
        assigned_to=request.assigned_to,
        priority=request.priority,
    )

    # Metrics
    tickets_escalated_total.labels(reason=request.reason).inc()

    return EscalateResponse(**result)