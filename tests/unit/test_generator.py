"""Unit tests for generator service."""
import pytest


class TestGenerator:
    """Tests for response generation."""

    @pytest.mark.asyncio
    async def test_generate_response_technical(self):
        from app.services.generator import generate_response
        result = await generate_response(
            ticket_id="test-123",
            context="The app crashes on login",
            language="en",
        )
        assert "response" in result
        assert result["model"] == "template-fallback"
        assert result["confidence"] > 0.5
        assert isinstance(result["tokens_used"], int)
        assert isinstance(result["citations"], list)

    @pytest.mark.asyncio
    async def test_generate_response_billing(self):
        from app.services.generator import generate_response
        result = await generate_response(
            ticket_id="test-456",
            context="Wrong charge on my invoice",
            language="en",
        )
        assert "response" in result
        assert result["confidence"] > 0.5

    @pytest.mark.asyncio
    async def test_generate_response_russian(self):
        from app.services.generator import generate_response
        result = await generate_response(
            ticket_id="test-789",
            context="Приложение падает при входе",
            language="ru",
        )
        assert "response" in result
        # Should contain Russian text
        assert any(c in result["response"] for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

    @pytest.mark.asyncio
    async def test_generate_response_with_context(self):
        from app.services.generator import generate_response
        result = await generate_response(
            ticket_id="test-ctx",
            context="User reports login failure",
            language="en",
        )
        assert "Regarding your message" in result["response"]

    def test_select_template(self):
        from app.services.generator import _select_template
        assert "technical" in _select_template("technical", "en").lower()
        assert "billing" in _select_template("billing", "en").lower()
        assert "general" in _select_template("general", "en").lower()
        # Russian
        assert any(c in _select_template("technical", "ru") for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

    def test_cache_key(self):
        from app.services.generator import _generate_cache_key
        key1 = _generate_cache_key("ticket-1", "context", "en")
        key2 = _generate_cache_key("ticket-1", "context", "en")
        key3 = _generate_cache_key("ticket-2", "context", "en")
        assert key1 == key2
        assert key1 != key3
        assert len(key1) == 16