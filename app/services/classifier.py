"""Ticket classification service."""
from typing import Literal, Optional
import re


# Keywords for rule-based classification (fallback when LLM unavailable)
TECHNICAL_KEYWORDS = [
    "error", "bug", "crash", "exception", "stack trace", "not working",
    "broken", "fail", "timeout", "connection", "api", "integration",
    "login", "password", "auth", "permission", "access denied",
    "performance", "slow", "lag", "latency", "memory", "cpu",
]

BILLING_KEYWORDS = [
    "bill", "invoice", "charge", "payment", "refund", "subscription",
    "plan", "pricing", "cost", "price", "upgrade", "downgrade",
    "cancel", "trial", "coupon", "discount", "receipt",
]

GENERAL_KEYWORDS = [
    "question", "how to", "help", "info", "information", "guide",
    "documentation", "feature", "request", "suggestion", "feedback",
    "contact", "support", "hello", "hi", "thanks", "thank you",
]

SPAM_KEYWORDS = [
    "buy now", "click here", "free money", "lottery", "winner",
    "congratulations", "urgent", "act now", "limited time",
]


def _keyword_score(text: str, keywords: list[str]) -> int:
    """Count keyword matches in text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _rule_based_classify(text: str) -> dict:
    """Rule-based classification as fallback."""
    scores = {
        "technical": _keyword_score(text, TECHNICAL_KEYWORDS),
        "billing": _keyword_score(text, BILLING_KEYWORDS),
        "general": _keyword_score(text, GENERAL_KEYWORDS),
        "spam": _keyword_score(text, SPAM_KEYWORDS),
    }

    # If no keywords matched, default to general
    if all(v == 0 for v in scores.values()):
        return {"category": "general", "confidence": 0.5, "subcategory": None}

    # Get top category
    category = max(scores, key=scores.get)
    max_score = scores[category]
    total = sum(scores.values())

    # Confidence based on score ratio
    confidence = min(0.9, max_score / max(total, 1) + 0.3)

    # Subcategory based on specific keywords
    subcategory = None
    if category == "technical":
        if any(kw in text.lower() for kw in ["login", "password", "auth"]):
            subcategory = "authentication"
        elif any(kw in text.lower() for kw in ["api", "integration"]):
            subcategory = "integration"
    elif category == "billing":
        if any(kw in text.lower() for kw in ["refund", "cancel"]):
            subcategory = "refund_cancellation"

    return {
        "category": category,
        "confidence": round(confidence, 2),
        "subcategory": subcategory,
    }


def _priority_from_category(category: str, confidence: float) -> Literal["low", "medium", "high", "urgent"]:
    """Determine priority from category and confidence."""
    if confidence < 0.5:
        return "low"
    if category in ("technical", "billing"):
        return "high"
    if category == "spam":
        return "low"
    return "medium"


async def classify_ticket(text: str, language: Optional[str] = None) -> dict:
    """
    Classify a support ticket text.
    
    Uses rule-based classification as primary (works offline),
    can be extended with LLM-based classification.
    """
    if not text or not text.strip():
        return {
            "category": "general",
            "confidence": 0.0,
            "subcategory": None,
            "suggested_priority": "low",
        }

    # Use rule-based classification (works offline, no API keys needed)
    result = _rule_based_classify(text)

    # Add priority
    result["suggested_priority"] = _priority_from_category(result["category"], result["confidence"])

    # Add language info
    result["language"] = language

    return result


# TODO: Add LLM-based classification when API keys available
# async def _llm_classify(text: str, language: Optional[str]) -> dict:
#     ...