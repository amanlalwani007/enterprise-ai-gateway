# Enterprise AI Gateway

> **Open-source, high-performance API gateway for corporate AI usage.** Centralize access to 100+ LLM providers, enforce budgets, slash costs with semantic caching, and protect sensitive data — all in one Docker command.

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
| **⚡ High-Concurrency Proxy** | Handles thousands of concurrent LLM streams via FastAPI + asyncio |
| **💰 Budgeting & Credit Limits** | USD/Token budgets per Tenant, Team, and User with Hard/Soft limits (Redis-based) |
| **🧠 Semantic Caching** | Reuses responses for semantically identical queries via `pgvector` — saves up to 70% on API costs |
| **🛡️ PII Masking** | Auto-detects and redacts SSNs, Emails, Credit Cards before they reach the LLM provider |
| **🔌 Multi-Provider Support** | Powers 100+ providers via LiteLLM: OpenAI, Anthropic, Gemini, Azure, Ollama, and more |
| **📊 Enterprise Dashboard** | Next.js admin panel for spend analytics, cache hit rates, and team health |
| **🔐 Rate Limiting** | Sliding-window rate limiter in Redis per API key |

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Async), LiteLLM, SQLAlchemy (Async), Uvicorn |
| **Frontend** | Next.js 14, Tailwind CSS, Lucide React, Recharts |
| **Database** | PostgreSQL + `pgvector` / `pgvectorscale` |
| **Cache** | Redis (Async) |
| **Infra** | Docker, Docker Compose |

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

## API Usage

The gateway is **OpenAI-compatible**. Point your existing OpenAI client at it:

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

## Architecture

```
Request → FastAPI Gateway
            ├── Auth & Rate Limit (Redis)
            ├── PII Masking
            ├── Semantic Cache Check (pgvector)
            │     └── Hit  → Return cached response
            │     └── Miss → Proxy via LiteLLM → Cache response
            └── Response streamed to client
```

## Project Structure

```
enterprise-ai-gateway/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes (chat, etc.)
│   │   ├── core/            # Config, security, caching, redis
│   │   ├── db/              # Database session, init, utils
│   │   ├── models/          # SQLAlchemy models
│   │   └── main.py          # FastAPI app entrypoint
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   └── components/      # Dashboard layout, widgets
│   ├── Dockerfile
│   └── package.json
├── docs/PLAN.md             # Implementation plan
├── docker-compose.yml
├── .env.example
└── LICENSE
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Distributed under the [MIT License](LICENSE).
