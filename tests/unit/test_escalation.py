"""Unit tests for escalation service."""
import pytest


class TestEscalation:
    """Tests for ticket escalation."""

    @pytest.mark.asyncio
    async def test_escalate_ticket(self):
        from app.services.escalation import escalate_ticket
        result = await escalate_ticket(
            ticket_id="test-123",
            reason="low_confidence",
            details="Customer needs human help",
            priority="high",
        )
        assert result["ticket_id"] == "test-123"
        assert result["reason"] == "low_confidence"
        assert result["priority"] == "high"
        assert result["status"] == "pending"
        assert "escalation_id" in result
        assert "created_at" in result

    @pytest.mark.asyncio
    async def test_escalate_ticket_minimal(self):
        from app.services.escalation import escalate_ticket
        result = await escalate_ticket(ticket_id="test-min")
        assert result["ticket_id"] == "test-min"
        assert result["reason"] == "low_confidence"  # default
        assert result["priority"] == "medium"  # default
        assert result["assigned_to"] is None

    @pytest.mark.asyncio
    async def test_escalate_all_reasons(self):
        from app.services.escalation import escalate_ticket
        reasons = ["low_confidence", "complex_issue", "customer_request", "policy_violation", "other"]
        for reason in reasons:
            result = await escalate_ticket(ticket_id=f"test-{reason}", reason=reason)
            assert result["reason"] == reason

    @pytest.mark.asyncio
    async def test_get_escalation(self):
        from app.services.escalation import get_escalation
        result = await get_escalation("esc-123")
        assert result["escalation_id"] == "esc-123"
        assert "status" in result

    @pytest.mark.asyncio
    async def test_acknowledge_escalation(self):
        from app.services.escalation import acknowledge_escalation
        result = await acknowledge_escalation("esc-123", "operator-1")
        assert result["escalation_id"] == "esc-123"
        assert result["status"] == "acknowledged"
        assert result["acknowledged_by"] == "operator-1"
        assert "acknowledged_at" in result

    @pytest.mark.asyncio
    async def test_resolve_escalation(self):
        from app.services.escalation import resolve_escalation
        result = await resolve_escalation("esc-123", "Issue resolved by operator")
        assert result["escalation_id"] == "esc-123"
        assert result["status"] == "resolved"
        assert result["resolution"] == "Issue resolved by operator"
        assert "resolved_at" in result