"""Tickets API endpoints."""
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.core.exceptions import NotFoundError, ValidationError
from app.core.metrics import tickets_created_total
from app.db.session import get_db_session

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketCreate(BaseModel):
    """Ticket creation request."""
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=10000)
    language: Optional[str] = Field(default=None, max_length=10)
    customer_id: Optional[str] = Field(default=None, max_length=100)
    metadata: Optional[dict] = None


class TicketResponse(BaseModel):
    """Ticket response."""
    id: str
    subject: str
    body: str
    language: Optional[str]
    customer_id: Optional[str]
    status: str
    created_at: str
    metadata: Optional[dict]


class TicketListResponse(BaseModel):
    """Paginated ticket list."""
    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int


# In-memory storage for demo (replace with DB in production)
_tickets_store: dict[str, dict] = {}


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    request: Request,
    session=Depends(get_db_session),
):
    """Create a new support ticket."""
    ticket_id = str(uuid4())
    now = "2026-09-20T00:00:00Z"  # Use datetime.utcnow().isoformat() in production

    ticket_data = {
        "id": ticket_id,
        "subject": ticket.subject,
        "body": ticket.body,
        "language": ticket.language,
        "customer_id": ticket.customer_id,
        "status": "open",
        "created_at": now,
        "metadata": ticket.metadata or {},
    }

    _tickets_store[ticket_id] = ticket_data

    # Metrics
    tickets_created_total.labels(
        source=request.headers.get("x-source", "api"),
        language=ticket.language or "unknown",
    ).inc()

    return TicketResponse(**ticket_data)


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
):
    """List tickets with pagination."""
    tickets = list(_tickets_store.values())

    if status_filter:
        tickets = [t for t in tickets if t["status"] == status_filter]

    total = len(tickets)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = tickets[start:end]

    return TicketListResponse(
        tickets=[TicketResponse(**t) for t in paginated],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str):
    """Get ticket by ID."""
    if ticket_id not in _tickets_store:
        raise NotFoundError(f"Ticket {ticket_id} not found")

    return TicketResponse(**_tickets_store[ticket_id])


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, updates: dict):
    """Update ticket (e.g., status change)."""
    if ticket_id not in _tickets_store:
        raise NotFoundError(f"Ticket {ticket_id} not found")

    _tickets_store[ticket_id].update(updates)
    return TicketResponse(**_tickets_store[ticket_id])


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: str):
    """Delete ticket."""
    if ticket_id not in _tickets_store:
        raise NotFoundError(f"Ticket {ticket_id} not found")

    del _tickets_store[ticket_id]