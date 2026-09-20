"""Unit tests for classifier service."""
import pytest


class TestClassifier:
    """Tests for ticket classification."""

    @pytest.mark.parametrize("text,expected_category", [
        ("The app crashes when I click login", "technical"),
        ("Getting error 500 on API call", "technical"),
        ("My invoice is wrong, wrong charge", "billing"),
        ("Need refund for last month", "billing"),
        ("How do I reset password?", "general"),
        ("What are your business hours?", "general"),
        ("Buy now! Click here for free money!", "spam"),
    ])
    def test_rule_based_classify(self, text, expected_category):
        from app.services.classifier import _rule_based_classify
        result = _rule_based_classify(text)
        assert result["category"] == expected_category
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_classify_ticket_technical(self):
        from app.services.classifier import classify_ticket
        result = await classify_ticket("The app crashes on login", "en")
        assert result["category"] == "technical"
        assert result["confidence"] > 0.5
        assert result["suggested_priority"] in ("medium", "high", "urgent")

    @pytest.mark.asyncio
    async def test_classify_ticket_billing(self):
        from app.services.classifier import classify_ticket
        result = await classify_ticket("Wrong charge on my invoice", "en")
        assert result["category"] == "billing"
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_classify_ticket_empty(self):
        from app.services.classifier import classify_ticket
        result = await classify_ticket("", "en")
        assert result["category"] == "general"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_classify_ticket_whitespace(self):
        from app.services.classifier import classify_ticket
        result = await classify_ticket("   \n\t  ", "en")
        assert result["category"] == "general"
        assert result["confidence"] == 0.0

    def test_confidence_bucket(self):
        from app.services.classifier import _confidence_bucket
        assert _confidence_bucket(0.95) == "high"
        assert _confidence_bucket(0.8) == "medium"
        assert _confidence_bucket(0.6) == "low"
        assert _confidence_bucket(0.3) == "very_low"