"""Unit tests for webhook handler service."""
import pytest


class TestWebhookHandler:
    """Tests for webhook processing."""

    @pytest.mark.asyncio
    async def test_process_zendesk_webhook(self):
        from app.services.webhook_handler import process_webhook
        payload = {
            "ticket": {
                "id": 12345,
                "subject": "Test issue",
                "description": "Description here",
                "requester": {"email": "test@example.com", "name": "John Doe"},
                "tags": ["urgent", "bug"],
                "priority": "high",
                "status": "open",
            }
        }
        result = await process_webhook("zendesk", payload)
        assert result["status"] == "accepted"
        assert result["source"] == "zendesk"
        ticket = result["ticket"]
        assert ticket["external_id"] == "12345"
        assert ticket["subject"] == "Test issue"
        assert ticket["customer_email"] == "test@example.com"
        assert ticket["priority"] == "high"

    @pytest.mark.asyncio
    async def test_process_intercom_webhook(self):
        from app.services.webhook_handler import process_webhook
        payload = {
            "data": {
                "item": {
                    "id": "conv_123",
                    "subject": "Intercom issue",
                    "body": "Body text",
                    "author": {"email": "jane@example.com", "name": "Jane"},
                    "tags": [{"name": "support"}],
                },
                "topic": "conversation.user.created",
            }
        }
        result = await process_webhook("intercom", payload)
        assert result["status"] == "accepted"
        assert result["source"] == "intercom"
        ticket = result["ticket"]
        assert ticket["external_id"] == "conv_123"
        assert ticket["customer_email"] == "jane@example.com"

    @pytest.mark.asyncio
    async def test_process_freshdesk_webhook(self):
        from app.services.webhook_handler import process_webhook
        payload = {
            "ticket": {
                "id": 999,
                "subject": "Freshdesk issue",
                "description": "Details",
                "email": "fresh@example.com",
                "requester": {"name": "Fresh User"},
                "tags": ["freshdesk"],
                "priority": 2,
                "status": 2,
            }
        }
        result = await process_webhook("freshdesk", payload)
        assert result["status"] == "accepted"
        assert result["source"] == "freshdesk"
        ticket = result["ticket"]
        assert ticket["external_id"] == "999"

    @pytest.mark.asyncio
    async def test_process_generic_webhook(self):
        from app.services.webhook_handler import process_webhook
        payload = {"id": "gen-1", "subject": "Generic", "message": "Hello", "email": "gen@test.com"}
        result = await process_webhook("generic", payload)
        assert result["status"] == "accepted"
        assert result["source"] == "generic"
        assert result["ticket"]["external_id"] == "gen-1"

    @pytest.mark.asyncio
    async def test_normalize_zendesk_minimal(self):
        from app.services.webhook_handler import _normalize_zendesk
        payload = {"ticket": {"id": 1}}
        result = _normalize_zendesk(payload)
        assert result["external_id"] == "1"
        assert result["subject"] == ""
        assert result["customer_email"] is None

    @pytest.mark.asyncio
    async def test_verify_signature(self):
        from app.services.webhook_handler import verify_signature
        import hmac
        import hashlib
        secret = "test-secret"
        payload = b'{"test": "data"}'
        sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        assert await verify_signature(payload, sig, secret) is True
        assert await verify_signature(payload, "wrong", secret) is False