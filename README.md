# Agent Customer Support

[![CI](https://github.com/Shamanchi/agent-customer-support/actions/workflows/ci.yml/badge.svg)](https://github.com/Shamanchi/agent-customer-support/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://hub.docker.com/r/shamanchi/agent-customer-support)
[![License: Shamanchi](https://img.shields.io/badge/License-Shamanchi-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

**ИИ-агент для автоматизации поддержки клиентов** — классификация тикетов, генерация ответов, эскалация к человеку, интеграция с CRM/Helpdesk.

> **Источник темы**: `Hands-On-AI-Engineering / P-109 (ai_customer_support_agent)` → портфолио `agent-customer-support`

---

## 🎯 Задача

Автоматизировать первичную поддержку клиентов:
- **Классификация** входящих обращений по темам (техническая, биллинг, общие вопросы)
- **Генерация ответов** на основе базы знаний и истории диалогов
- **Эскалация** сложных кейсов к живым операторам с контекстом
- **Мультиязычность** (en, ru, es, de, fr)
- **Интеграция** с популярными Helpdesk (Zendesk, Intercom, Freshdesk) через вебхуки

---

## 🏗 Архитектура

```mermaid
flowchart TD
    A[Входящий тикет] --> B[Классификатор намерений]
    B --> C{Уверенность > порог?}
    C -- Да --> D[Генератор ответа (RAG + LLM)]
    C -- Нет --> E[Эскалация к оператору]
    D --> F[Проверка качества / Guardrails]
    F --> G{Прошло?}
    G -- Да --> H[Автоответ клиенту]
    G -- Нет --> E
    E --> I[Оператор + контекст]
    H --> J[Логирование / Аналитика]
    I --> J
```

**Слои:**
- `api/` — FastAPI endpoints: `/tickets`, `/classify`, `/generate`, `/escalate`, `/webhooks`
- `services/` — `classifier`, `generator`, `escalation`, `webhook_handler`, `knowledge_base`
- `core/` — `config` (pydantic-settings), `logging`, `exceptions`, `metrics` (Prometheus)

---

## 🚀 Quickstart

```bash
# Клонировать
git clone https://github.com/Shamanchi/agent-customer-support.git
cd agent-customer-support

# Настроить окружение
cp .env.example .env
# Отредактировать .env (добавить OPENAI_API_KEY и пр.)

# Локально (Poetry / pip)
pip install -r requirements.txt
uvicorn app.main:app --reload

# Или Docker
docker compose up --build
```

API будет доступен на `http://localhost:8000`:
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`
- Metrics: `http://localhost:8000/metrics`

---

## 📦 API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/tickets` | Создать тикет (входной вебхук) |
| `POST` | `/api/v1/classify` | Классифицировать текст обращения |
| `POST` | `/api/v1/generate` | Сгенерировать ответ для тикета |
| `POST` | `/api/v1/escalate` | Эскалировать к оператору |
| `POST` | `/api/v1/webhooks/{provider}` | Вебхуки от Helpdesk (Zendesk/Intercom) |
| `GET` | `/api/v1/health` | Health-check |
| `GET` | `/metrics` | Prometheus metrics |

---

## ⚙️ Конфигурация (`.env`)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OPENAI_API_KEY` | Ключ OpenAI (для генерации) | — |
| `OPENAI_BASE_URL` | Базовый URL OpenAI | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Модель генерации | `gpt-4o-mini` |
| `ANTHROPIC_API_KEY` | Ключ Anthropic (fallback) | — |
| `ANTHROPIC_MODEL` | Модель Anthropic | `claude-3-5-sonnet-20241022` |
| `DATABASE_URL` | URL БД (SQLite/PostgreSQL) | `sqlite:///./data.db` |
| `REDIS_URL` | Redis для кэша/очереди | `redis://localhost:6379/0` |
| `APP_ENV` | Окружение | `development` |
| `DEBUG` | Режим отладки | `True` |
| `DEFAULT_LANGUAGE` | Язык по умолчанию | `en` |
| `SUPPORTED_LANGUAGES` | Поддерживаемые языки | `en,ru,es,de,fr` |
| `MAX_CONVERSATION_HISTORY` | Макс. длина истории | `10` |
| `RESPONSE_TIMEOUT` | Таймаут ответа (сек) | `30` |
| `RATE_LIMIT_PER_MINUTE` | Лимит запросов/мин | `60` |

Полный список см. в `.env.example`.

---

## 🧪 Тесты

```bash
# Unit-тесты (без сети)
pytest tests/unit -v

# Интеграционные (требуют БД/Redis)
pytest tests/integration -v -m integration

# Все тесты с покрытием
pytest --cov=app --cov-report=term-missing
```

---

## 🐳 Docker

```bash
# Сборка
docker build -t agent-customer-support .

# Запуск (app + DB + Redis)
docker compose up --build -d

# Логи
docker compose logs -f app
```

`docker-compose.yml` поднимает:
- `app` — FastAPI приложение
- `db` — PostgreSQL 16
- `redis` — Redis 7

---

## 📁 Структура проекта

```
agent-customer-support/
├── .github/workflows/ci.yml      # CI: ruff + mypy + pytest
├── app/
│   ├── api/                      # FastAPI routers
│   │   ├── tickets.py
│   │   ├── classify.py
│   │   ├── generate.py
│   │   ├── escalate.py
│   │   └── webhooks.py
│   ├── services/                 # Бизнес-логика
│   │   ├── classifier.py
│   │   ├── generator.py
│   │   ├── escalation.py
│   │   ├── webhook_handler.py
│   │   └── knowledge_base.py
│   ├── core/                     # Конфиг, логи, метрики
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── exceptions.py
│   │   └── metrics.py
│   └── main.py                   # FastAPI factory + lifespan
├── tests/
│   ├── unit/                     # Unit-тесты (mock LLM/DB)
│   └── integration/              # Интеграционные (real DB/Redis)
├── .env.example                  # Шаблон переменных окружения
├── .gitignore
├── requirements.txt              # Зависимости (pinned)
├── pyproject.toml                # Метаданные + tool config
├── Dockerfile                    # Multi-stage, non-root
├── docker-compose.yml            # App + Postgres + Redis
├── alembic/                      # Миграции БД
├── LICENSE
└── NOTICE.md
```

---

## 📊 Наблюдаемость

- **Prometheus metrics** на `/metrics` (request latency, ticket count, classification accuracy, escalation rate)
- **Structured logging** (JSON) — корреляция по `request_id`
- **Health checks** — `/api/v1/health` (liveness/readiness)

---

## 📄 Лицензия

Лицензия Shamanchi 1.0 (source-available) — см. [LICENSE](LICENSE).
---

## 📞 Контакты

- Telegram: @PavelYrevichh
- Email: Lietman46@mail.ru
- GitHub: Shamanchi
- FL.ru: https://www.fl.ru/users/Shamanchi