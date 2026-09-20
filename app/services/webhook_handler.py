"""Webhook handler service for Helpdesk integrations."""
from typing import Any, Dict, Optional


async def process_webhook(source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process incoming webhook from Helpdesk.
    
    Normalizes payload from different providers (Zendesk, Intercom, Freshdesk)
    into internal ticket format and creates ticket.
    """
    # Normalize based on source
    if source == "zendesk":
        ticket_data = _normalize_zendesk(payload)
    elif source == "intercom":
        ticket_data = _normalize_intercom(payload)
    elif source == "freshdesk":
        ticket_data = _normalize_freshdesk(payload)
    else:
        ticket_data = _normalize_generic(payload)

    # In production: create ticket in DB, trigger classification/generation
    # For now, return normalized ticket

    return {
        "status": "accepted",
        "source": source,
        "ticket": ticket_data,
    }


def _normalize_zendesk(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Zendesk webhook payload."""
    ticket = payload.get("ticket", {})
    return {
        "external_id": str(ticket.get("id")),
        "subject": ticket.get("subject", ""),
        "body": ticket.get("description", ""),
        "customer_email": ticket.get("requester", {}).get("email"),
        "customer_name": ticket.get("requester", {}).get("name"),
        "tags": ticket.get("tags", []),
        "priority": ticket.get("priority", "normal"),
        "status": ticket.get("status", "new"),
    }


def _normalize_intercom(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Intercom webhook payload."""
    data = payload.get("data", {})
    item = data.get("item", {})
    return {
        "external_id": str(item.get("id")),
        "subject": item.get("subject", data.get("topic", "")),
        "body": item.get("body", ""),
        "customer_email": item.get("author", {}).get("email"),
        "customer_name": item.get("author", {}).get("name"),
        "tags": item.get("tags", []),
        "priority": "normal",
        "status": "open",
    }


def _normalize_freshdesk(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Freshdesk webhook payload."""
    ticket = payload.get("ticket", {})
    return {
        "external_id": str(ticket.get("id")),
        "subject": ticket.get("subject", ""),
        "body": ticket.get("description", ""),
        "customer_email": ticket.get("email"),
        "customer_name": ticket.get("requester", {}).get("name"),
        "tags": ticket.get("tags", []),
        "priority": ticket.get("priority", 1),
        "status": ticket.get("status", 2),
    }


def _normalize_generic(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize generic webhook payload."""
    return {
        "external_id": str(payload.get("id", "")),
        "subject": payload.get("subject", payload.get("title", "")),
        "body": payload.get("body", payload.get("description", payload.get("message", ""))),
        "customer_email": payload.get("email", payload.get("customer_email")),
        "customer_name": payload.get("name", payload.get("customer_name")),
        "tags": payload.get("tags", []),
        "priority": "normal",
        "status": "open",
    }


async def send_webhook_response(
    source: str,
    ticket_id: str,
    response: str,
    webhook_url: Optional[str] = None,
) -> bool:
    """Send response back to Helpdesk via webhook."""
    # In production: POST to webhook URL with response
    # For now, return success
    return True