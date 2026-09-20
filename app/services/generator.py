"""Response generation service."""
from typing import Optional
import time
import hashlib


# Template responses for different categories (fallback when LLM unavailable)
TEMPLATES = {
    "technical": {
        "en": "Thank you for reporting this technical issue. Our team is investigating. "
              "In the meantime, please try: 1) Restarting the application, 2) Clearing cache, "
              "3) Checking for updates. We'll update you within 24 hours.",
        "ru": "Спасибо за сообщение о технической проблеме. Наша команда исследует её. "
              "Пока что попробуйте: 1) Перезапустить приложение, 2) Очистить кэш, "
              "3) Проверить обновления. Мы обновим вас в течение 24 часов.",
    },
    "billing": {
        "en": "Thank you for your billing inquiry. We've received your request and "
              "our billing team will review it within 1-2 business days. "
              "You'll receive an email with updates.",
        "ru": "Спасибо за запрос по биллингу. Мы получили ваш запрос и наша команда "
              "биллинга рассмотрит его в течение 1-2 рабочих дней. Вы получите email с обновлениями.",
    },
    "general": {
        "en": "Thank you for contacting us. We've received your message and will respond "
              "within 24 hours. For immediate help, check our knowledge base at help.example.com.",
        "ru": "Спасибо за обращение. Мы получили ваше сообщение и ответим в течение 24 часов. "
              "Для быстрой помощи обратитесь к базе знаний help.example.com.",
    },
    "spam": {
        "en": "Thank you for your message. If this is a legitimate inquiry, please rephrase "
              "and resend. Automated messages are filtered.",
        "ru": "Спасибо за сообщение. Если это легальный запрос, перефразируйте и отправьте снова. "
              "Автоматические сообщения фильтруются.",
    },
    "other": {
        "en": "Thank you for contacting support. We'll review your message and respond shortly.",
        "ru": "Спасибо за обращение в поддержку. Мы рассмотрим ваше сообщение и ответим в ближайшее время.",
    },
}


def _select_template(category: str, language: str) -> str:
    """Select appropriate template for category and language."""
    lang = language.lower() if language else "en"
    if lang not in ("en", "ru"):
        lang = "en"

    cat_templates = TEMPLATES.get(category, TEMPLATES["general"])
    return cat_templates.get(lang, cat_templates["en"])


def _generate_cache_key(ticket_id: str, context: Optional[str], language: Optional[str]) -> str:
    """Generate cache key for response caching."""
    content = f"{ticket_id}:{context or ''}:{language or ''}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


async def generate_response(
    ticket_id: str,
    context: Optional[str] = None,
    language: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> dict:
    """
    Generate a response for a ticket.
    
    Uses template-based generation as fallback (works offline).
    Can be extended with LLM-based generation when API keys available.
    """
    # In production, fetch ticket from DB to get category
    # For now, simulate category detection from context
    category = "general"
    if context:
        context_lower = context.lower()
        if any(kw in context_lower for kw in ["error", "bug", "crash", "technical", "api", "login"]):
            category = "technical"
        elif any(kw in context_lower for kw in ["bill", "invoice", "payment", "refund", "charge"]):
            category = "billing"
        elif any(kw in context_lower for kw in ["spam", "buy now", "click here"]):
            category = "spam"

    # Select template
    response_text = _select_template(category, language or "en")

    # Add context acknowledgment if provided
    if context:
        response_text = f"Regarding your message: \"{context[:200]}...\"\n\n{response_text}"

    # Simulated model info
    model = "template-fallback"
    tokens_used = len(response_text.split())

    # Confidence based on category match
    confidence = 0.85 if category != "general" else 0.6

    return {
        "response": response_text,
        "model": model,
        "tokens_used": tokens_used,
        "confidence": confidence,
        "citations": [],
    }


# TODO: Add LLM-based generation when API keys available
# async def _llm_generate(...):
#     ...