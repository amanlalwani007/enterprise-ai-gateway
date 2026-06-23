# 🚀 Enterprise AI Gateway

The **Enterprise AI Gateway** is an open-source, high-performance control plane for corporate AI usage. Built on top of **LiteLLM** and **FastAPI**, it allows organizations to centralize their AI access, restrict usage through granular credit limits, and dramatically reduce costs using **Semantic Caching**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.109+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-v14-black.svg)

## ✨ Key Features

*   **⚡ High-Concurrency Proxy:** Handles thousands of concurrent LLM streams using Python's `asyncio` and FastAPI.
*   **💰 Budgeting & Credit Limits:** Allocate USD/Token budgets to Tenants, Teams, and individual Users. Support for Hard and Soft limits.
*   **🧠 Semantic Caching:** Uses `pgvector` to identify and reuse responses for semantically identical queries, saving up to 70% in API costs.
*   **🛡️ PII Masking:** Automatically detects and redacts sensitive data (SSNs, Emails, CCs) before it reaches the LLM provider.
*   **🔌 Multi-Provider Support:** Integrated with LiteLLM to support 100+ providers including OpenAI, Anthropic, Gemini, Azure, and local models (Ollama).
*   **📊 Enterprise Dashboard:** A modern Next.js dashboard for monitoring spend, cache hit rates, and team health.

## 🛠️ Tech Stack

*   **Backend:** FastAPI (Python), LiteLLM, SQLAlchemy (Async), Uvicorn.
*   **Frontend:** Next.js 14, Tailwind CSS, Lucide React, Recharts.
*   **Database:** PostgreSQL with `pgvector` & `pgvectorscale`.
*   **Caching:** Redis (Async).
*   **DevOps:** Docker, Docker Compose.

## 🚀 Quick Start

### 1. Prerequisites
*   Docker & Docker Compose installed.
*   API keys for your LLM providers (e.g., OpenAI, Anthropic).

### 2. Setup
Clone the repository and create your environment file:
```bash
cp .env.example .env
```
Edit `.env` and add your `OPENAI_API_KEY` or other provider keys.

### 3. Run with Docker
```bash
docker-compose up --build
```

The services will be available at:
*   **Dashboard:** [http://localhost:3000](http://localhost:3000)
*   **API Gateway:** [http://localhost:8000](http://localhost:8000)
*   **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 API Usage
The gateway is **OpenAI-compatible**. Simply point your existing OpenAI client to the gateway URL.

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

## 🏗️ Architecture
1.  **Request** hits the FastAPI Gateway.
2.  **Auth & Rate Limit** checks are performed against Redis.
3.  **PII Masking** redacts sensitive data.
4.  **Semantic Cache** check performed in Postgres (`pgvector`).
5.  **Proxy** call made via LiteLLM if cache miss.
6.  **Response** streamed back and cached asynchronously.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
