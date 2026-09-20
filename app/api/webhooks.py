"""Webhooks API endpoints for Helpdesk integrations."""
import hmac
import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel

from app.core.exceptions import ValidationError
from app.services.webhook_handler import process_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class ZendeskWebhook(BaseModel):
    """Zendesk webhook payload."""
    ticket: dict
    event: str


class IntercomWebhook(BaseModel):
    """Intercom webhook payload."""
    data: dict
    topic: str


class FreshdeskWebhook(BaseModel):
    """Freshdesk webhook payload."""
    ticket: dict
    event: str


@router.post("/zendesk")
async def zendesk_webhook(
    request: Request,
    payload: ZendeskWebhook,
    x_zendesk_signature: Optional[str] = Header(None, alias="X-Zendesk-Signature"),
):
    """Handle Zendesk webhook."""
    # Verify signature if configured
    # await verify_zendesk_signature(request, x_zendesk_signature)
    return await process_webhook("zendesk", payload.model_dump())


@router.post("/intercom")
async def intercom_webhook(
    request: Request,
    payload: IntercomWebhook,
    x_hub_signature: Optional[str] = Header(None, alias="X-Hub-Signature"),
):
    """Handle Intercom webhook."""
    # Verify signature if configured
    # await verify_intercom_signature(request, x_hub_signature)
    return await process_webhook("intercom", payload.model_dump())


@router.post("/freshdesk")
async def freshdesk_webhook(
    request: Request,
    payload: FreshdeskWebhook,
    x_freshdesk_signature: Optional[str] = Header(None, alias="X-Freshdesk-Signature"),
):
    """Handle Freshdesk webhook."""
    # Verify signature if configured
    # await verify_freshdesk_signature(request, x_freshdesk_signature)
    return await process_webhook("freshdesk", payload.model_dump())


@router.post("/generic")
async def generic_webhook(request: Request):
    """Generic webhook endpoint."""
    payload = await request.json()
    return await process_webhook("generic", payload)


async def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC signature."""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)