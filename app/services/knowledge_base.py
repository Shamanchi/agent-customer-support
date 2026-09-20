"""Knowledge base service for Agent Customer Support."""
from typing import List, Optional
import re


# In-memory knowledge base (replace with vector DB in production)
KNOWLEDGE_BASE = {
    "technical": [
        {
            "id": "kb-tech-001",
            "title": "How to restart the application",
            "content": "Close the application completely and reopen it. On Windows: Task Manager > End Task. On Mac: Cmd+Q then reopen.",
            "tags": ["restart", "crash", "frozen"],
            "language": "en",
        },
        {
            "id": "kb-tech-002",
            "title": "Clearing cache and cookies",
            "content": "Browser: Settings > Privacy > Clear browsing data. App: Settings > Storage > Clear Cache.",
            "tags": ["cache", "cookies", "slow", "performance"],
            "language": "en",
        },
        {
            "id": "kb-tech-003",
            "title": "API connection timeout",
            "content": "Check network connectivity. Verify API endpoint URL. Check firewall/proxy settings. Increase timeout in config.",
            "tags": ["api", "timeout", "connection", "integration"],
            "language": "en",
        },
    ],
    "billing": [
        {
            "id": "kb-bill-001",
            "title": "How to update payment method",
            "content": "Go to Account > Billing > Payment Methods. Click 'Add New' or 'Update'. Enter new card/bank details.",
            "tags": ["payment", "card", "update", "method"],
            "language": "en",
        },
        {
            "id": "kb-bill-002",
            "title": "Requesting a refund",
            "content": "Refunds available within 30 days of purchase. Contact support with order ID. Processed in 5-10 business days.",
            "tags": ["refund", "return", "money back"],
            "language": "en",
        },
    ],
    "general": [
        {
            "id": "kb-gen-001",
            "title": "Contacting support",
            "content": "Email: support@example.com. Chat: widget on website. Phone: +1-800-XXX-XXXX (business hours).",
            "tags": ["contact", "support", "help"],
            "language": "en",
        },
        {
            "id": "kb-gen-002",
            "title": "Supported languages",
            "content": "We support English, Russian, Spanish, German, and French. Set your preferred language in account settings.",
            "tags": ["language", "localization", "translate"],
            "language": "en",
        },
    ],
}


def search_knowledge_base(
    query: str,
    category: Optional[str] = None,
    language: str = "en",
    limit: int = 5,
) -> List[dict]:
    """
    Search knowledge base for relevant articles.
    
    Simple keyword matching (replace with vector search in production).
    """
    query_lower = query.lower()
    query_words = set(re.findall(r"\w+", query_lower))

    results = []

    # Search in specific category or all
    categories = [category] if category else KNOWLEDGE_BASE.keys()

    for cat in categories:
        for article in KNOWLEDGE_BASE.get(cat, []):
            if article["language"] != language:
                continue

            # Simple scoring: count matching words in title + content + tags
            text = f"{article['title']} {article['content']} {' '.join(article['tags'])}".lower()
            text_words = set(re.findall(r"\w+", text))
            score = len(query_words & text_words)

            if score > 0:
                results.append({
                    "id": article["id"],
                    "title": article["title"],
                    "content": article["content"],
                    "category": cat,
                    "score": score,
                    "tags": article["tags"],
                })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


async def get_article(article_id: str) -> Optional[dict]:
    """Get article by ID."""
    for cat in KNOWLEDGE_BASE.values():
        for article in cat:
            if article["id"] == article_id:
                return article
    return None


async def add_article(
    category: str,
    title: str,
    content: str,
    tags: list[str],
    language: str = "en",
) -> dict:
    """Add new article to knowledge base."""
    # In production: save to DB/vector DB
    article_id = f"kb-{category}-{len(KNOWLEDGE_BASE.get(category, [])) + 1:03d}"
    article = {
        "id": article_id,
        "title": title,
        "content": content,
        "tags": tags,
        "language": language,
    }
    if category not in KNOWLEDGE_BASE:
        KNOWLEDGE_BASE[category] = []
    KNOWLEDGE_BASE[category].append(article)
    return article