"""Unit tests for knowledge base service."""
import pytest


class TestKnowledgeBase:
    """Tests for knowledge base service."""

    def test_search_technical(self):
        from app.services.knowledge_base import search_knowledge_base
        results = search_knowledge_base("app crashes on login", category="technical", limit=3)
        assert len(results) > 0
        assert all(r["category"] == "technical" for r in results)
        assert results[0]["score"] >= results[-1]["score"]

    def test_search_billing(self):
        from app.services.knowledge_base import search_knowledge_base
        results = search_knowledge_base("wrong charge on invoice", category="billing", limit=3)
        assert len(results) > 0
        assert all(r["category"] == "billing" for r in results)

    def test_search_general(self):
        from app.services.knowledge_base import search_knowledge_base
        results = search_knowledge_base("how to contact support", category="general", limit=3)
        assert len(results) > 0
        assert all(r["category"] == "general" for r in results)

    def test_search_all_categories(self):
        from app.services.knowledge_base import search_knowledge_base
        results = search_knowledge_base("help", limit=10)
        assert len(results) > 0
        categories = {r["category"] for r in results}
        assert len(categories) >= 2

    def test_search_language_filter(self):
        from app.services.knowledge_base import search_knowledge_base
        # English (default)
        results_en = search_knowledge_base("restart", language="en", limit=5)
        assert all(r["language"] == "en" for r in results_en)

    def test_search_no_results(self):
        from app.services.knowledge_base import search_knowledge_base
        results = search_knowledge_base("xyzzyx nonexistent query", limit=5)
        assert results == []

    def test_search_sorted_by_score(self):
        from app.services.knowledge_base import search_knowledge_base
        results = search_knowledge_base("restart cache", category="technical", limit=5)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_get_article(self):
        from app.services.knowledge_base import get_article
        article = await get_article("kb-tech-001")
        assert article is not None
        assert article["id"] == "kb-tech-001"
        assert "title" in article

    @pytest.mark.asyncio
    async def test_get_nonexistent_article(self):
        from app.services.knowledge_base import get_article
        article = await get_article("nonexistent-id")
        assert article is None

    @pytest.mark.asyncio
    async def test_add_article(self):
        from app.services.knowledge_base import add_article, get_article
        article = await add_article(
            category="technical",
            title="Test Article",
            content="Test content",
            tags=["test", "new"],
        )
        assert article["title"] == "Test Article"
        assert article["category"] == "technical"  # not returned but in KB
        fetched = await get_article(article["id"])
        assert fetched is not None
        assert fetched["title"] == "Test Article"