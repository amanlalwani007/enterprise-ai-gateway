# Enterprise AI Gateway

> **Open-source, high-performance API gateway for corporate AI usage.** Centralize access to 100+ LLM providers, enforce budgets, slash costs with query-aware semantic caching, and protect sensitive data — all in one Docker command.

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a86b.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000.svg?logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg?logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-Caching-DC382D.svg?logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker)](https://docker.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## Features

| Capability | Description |
|---|---|
| **⚡ High-Concurrency Proxy** | Handles thousands of concurrent LLM streams via FastAPI + asyncio with streaming and non-streaming support |
| **🧠 Query-Aware Semantic Caching** | Classifies queries (factual, code, creative, analytical, conversational) and applies per-type similarity thresholds, TTLs, and keyword fallback — saves up to 70% on API costs |
| **🔌 Model Router** | Glob-pattern routing (`gpt-4*`, `claude-*`) to any provider, model name overrides, fallback routes, and per-route budget limits |
| **💰 Budgeting & Credit Limits** | USD/Token budgets per API key with Redis-based budget checks and background spend tracking |
| **🛡️ PII Masking** | Auto-detects and redacts emails, SSNs, credit cards, and phone numbers before they reach the LLM provider |
| **🔐 Rate Limiting** | Sliding-window rate limiter via Redis — configurable requests per window, disabled by default |
| **🔑 Admin API** | Full REST admin interface for API key creation, rotation, revocation, audit log export (CSV/JSON), and cache statistics |
| **📊 Enterprise Dashboard** | Next.js admin panel with spend analytics, cache hit rates, PII masking metrics, and team health overview |
| **🏥 Health Checks** | Database and Redis health monitoring endpoint (`/health`) |

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Async), LiteLLM, SQLAlchemy (Async), Uvicorn |
| **Frontend** | Next.js 14 (Standalone), Tailwind CSS, Lucide React |
| **Database** | PostgreSQL + `pgvector` (HNSW index, GIN index for keywords) |
| **Cache** | Redis (Async) — rate limiting, budget, semantic cache thresholds |
| **Infra** | Docker, Docker Compose |
| **Testing** | pytest, pytest-asyncio, httpx |

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- API key(s) for your LLM provider(s)

### Setup

```bash
# Clone
git clone https://github.com/amanlalwani007/enterprise-ai-gateway.git
cd enterprise-ai-gateway

# Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (or other provider keys)

# Launch everything
docker-compose up --build
```

### Services

| Service | URL |
|---|---|
| **Dashboard** | http://localhost:3000 |
| **API Gateway** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **PostgreSQL (pgvector)** | localhost:5432 |
| **Redis** | localhost:6379 |

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `ADMIN_API_KEY` | `admin-secret-change-me` | Admin API key (must be changed) |
| `BUDGET_ENABLED` | `true` | Enable budget enforcement |
| `DEFAULT_BUDGET` | `1000.0` | Default per-key budget (USD) |
| `DEFAULT_COST_PER_REQUEST` | `0.001` | Default cost per request (USD) |
| `RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | `60` | Max requests per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window duration |
| `CACHE_ENABLED` | `true` | Enable semantic caching |
| `CACHE_SIMILARITY_THRESHOLD` | `0.95` | Default similarity threshold |
| `PII_MASKING_ENABLED` | `true` | Enable PII redaction |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model for caching |
| `MODEL_ROUTES` | — | JSON model routing config (optional) |

## API Usage

### Chat (OpenAI-compatible)

Point your existing OpenAI client at the gateway:

```python
import openai

client = openai.OpenAI(
    api_key="your-gateway-key",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain quantum computing."}]
)
```

### Admin API

All admin endpoints require `Authorization: Bearer <ADMIN_API_KEY>`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/admin/keys?email=...` | Create API key |
| `GET` | `/v1/admin/keys` | List all API keys |
| `DELETE` | `/v1/admin/keys/{user_id}` | Revoke API key |
| `POST` | `/v1/admin/keys/{user_id}/rotate` | Rotate API key |
| `GET` | `/v1/admin/logs/export?format=csv` | Export audit logs |
| `GET` | `/v1/admin/cache/stats` | Cache statistics |

### Health Check

```bash
curl http://localhost:8000/health
```

Returns database and Redis status with a top-level `healthy` or `degraded`.

## Architecture

```
Request → FastAPI Gateway
            ├── Health Check (/health)
            ├── Auth & Rate Limit (Redis)
            ├── PII Masking (email, SSN, credit card, phone)
            ├── Model Router (glob-pattern → provider)
            ├── Query-Aware Semantic Cache (pgvector)
            │     ├── Classify query (factual/code/creative/analytical/conversational)
            │     ├── Per-type similarity threshold + TTL
            │     └── Hit  → Return cached response
            │     └── Miss → Proxy via LiteLLM → Save to cache (background)
            ├── Budget Tracking (background)
            └── Request Logging (background)
```

## Project Structure

```
enterprise-ai-gateway/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── chat.py           # Chat completion proxy (streaming + non-streaming)
│   │   │   └── admin.py          # Admin routes (keys, logs, cache stats)
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic settings from env vars
│   │   │   ├── security.py       # API key verification
│   │   │   ├── redis_utils.py    # Redis async client
│   │   │   ├── cache_utils.py    # Semantic cache (pgvector)
│   │   │   ├── query_classifier.py  # Query type classification + strategy
│   │   │   ├── routing.py        # Glob-pattern model router
│   │   │   └── health.py         # DB + Redis health checks
│   │   ├── db/
│   │   │   ├── session.py        # Async SQLAlchemy session
│   │   │   ├── init_db.py        # Schema init + HNSW/GIN indexes
│   │   │   └── utils.py          # DB utilities
│   │   ├── models/
│   │   │   ├── enterprise.py     # Tenant, Team, User ORM models
│   │   │   ├── cache.py          # SemanticCache ORM model
│   │   │   └── usage.py          # RequestLog ORM model
│   │   └── main.py               # FastAPI app entrypoint (v0.2.0)
│   ├── tests/
│   │   ├── conftest.py           # Pytest fixtures (9 async fixtures)
│   │   ├── test_admin.py         # Admin route tests
│   │   ├── test_cache.py         # Cache logic unit tests
│   │   ├── test_chat.py          # Chat route tests
│   │   ├── test_health.py        # Health endpoint tests
│   │   └── test_routing.py       # Model routing tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js App Router pages
│   │   └── components/           # DashboardLayout, stat cards, tables
│   ├── Dockerfile
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── tsconfig.json
│   └── package.json
├── docker-compose.yml
├── .env.example
├── CONTRIBUTING.md
└── LICENSE
```

## Testing

Tests use `pytest` with async support. Run from the `backend/` directory:

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## Model Routing

The built-in router maps glob patterns to providers. Customize via `MODEL_ROUTES` env var or fall back to defaults:

```json
[
  {"pattern": "gpt-4*", "provider": "openai"},
  {"pattern": "claude-*", "provider": "anthropic"},
  {"pattern": "gemini-*", "provider": "gemini"},
  {"pattern": "*", "provider": "openai", "fallback": "ollama/llama3"}
]
```

## Semantic Cache Strategies

The query classifier categorizes prompts and applies tuned strategies:

| Query Type | Similarity Threshold | TTL | Keyword Fallback |
|---|---|---|---|
| **Factual** | 0.94 | 7 days | Yes |
| **Code** | 0.97 | 7 days | Yes |
| **Analytical** | 0.91 | 1 day | Yes |
| **Creative** | 0.85 | 1 hour | No |
| **Conversational** | 0.80 | 30 min | No |

## API Key Format

Generated keys use the format `eag_` followed by 48 hex characters. Keys are SHA-256 hashed before storage — the raw key is shown once at creation.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Distributed under the [MIT License](LICENSE).
