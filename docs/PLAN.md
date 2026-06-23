# Enterprise AI Gateway SaaS Implementation Plan (High-Concurrency Python)

## 1. Objective
Build an open-source Enterprise AI Gateway SaaS using **FastAPI**. This architecture prioritizes high concurrency and low latency by utilizing Python's `asyncio` for all I/O operations (database, caching, and LLM proxying).

## 2. Tech Stack (High-Concurrency Focus)
*   **Web Framework:** **FastAPI** (Asynchronous, built on Starlette and Pydantic).
*   **LLM Logic:** **LiteLLM SDK** (Integrated directly into FastAPI routes).
*   **Server:** **Uvicorn** (Lightning-fast ASGI server) with **Gunicorn** for process management.
*   **Database:** PostgreSQL with **`asyncpg`** and **`pgvectorscale`** (specialized extension for high-performance vector search).
*   **ORM/Query Builder:** **SQLAlchemy (Async)**.
*   **Caching & Budgets:** **Redis** (using `redis-py` async client) for millisecond-latency budget and rate-limit checks.
*   **Authentication:** **FastAPI Users** or **Authlib** (supporting OAuth2 and future SAML/SSO).
*   **Dashboard UI:** **Next.js** (talking to the FastAPI Backend).

## 3. Deployment & Infrastructure Strategy

### Local Development (The "One-Command" Setup)
*   **Tool:** `docker-compose`.
*   **Goal:** Allow contributors to run the entire stack (FastAPI, Next.js, Postgres + pgvector, Redis) with a single `docker-compose up` command.
*   **Environment:** Use a `.env.example` file to manage LLM API keys and database credentials.

### Production: AWS EC2 (Simple Deployment)
*   **Strategy:** Dockerized deployment using `docker-compose` or a single-node setup.
*   **Reverse Proxy:** **Nginx** or **Caddy** for SSL termination (HTTPS) and load balancing.
*   **Persistence:** Use **AWS EBS** for Postgres data persistence.

### Production: AWS EKS / Kubernetes (Enterprise Scaling)
*   **Strategy:** Container orchestration for high availability.
*   **Artifacts:**
    *   **Helm Chart:** Provide a standard Helm chart for deploying the API, Worker, and UI.
    *   **StatefulSets:** For Postgres and Redis (or recommend managed services like **AWS RDS** and **AWS ElastiCache** for production).
    *   **Horizontal Pod Autoscaler (HPA):** Automatically scale the FastAPI Gateway pods based on CPU/Request load.
    *   **Ingress:** Use **AWS Load Balancer Controller** to handle external traffic.

## 4. High-Concurrency Architecture
1.  **Async Entry Point:** Every request enters an `async def` route in FastAPI. This ensures the worker is never "blocked" while waiting for an LLM response.
2.  **Distributed State (Redis):** To scale horizontally across multiple servers/containers, we store active token budgets and rate limits in Redis.
3.  **Non-Blocking Logic:**
    *   **Auth Check:** JWT validation + Redis lookup.
    *   **Budget Check:** Async Redis `GET`/`DECR` (decrements credits atomically).
    *   **Semantic Cache:** Async `pgvector` search in Postgres.
4.  **Streaming Proxy:** FastAPI natively supports `StreamingResponse`. We will use LiteLLM's async streaming to pipe tokens from the provider (OpenAI/Anthropic) directly to the user with zero buffering.

## 4. Phased Implementation Plan

### Phase 1: High-Speed Async Proxy
*   **Goal:** Build a FastAPI proxy that handles streaming and basic usage logging.
*   **Tasks:**
    *   Initialize FastAPI project with Uvicorn.
    *   Integrate `litellm.completion` (async) into a `/v1/chat/completions` route.
    *   Implement async PostgreSQL connection pool using `asyncpg`.
    *   Log token usage to Postgres asynchronously *after* the request is completed (using `BackgroundTasks`).

### Phase 2: Distributed Budgeting & Rate Limiting
*   **Goal:** Implement the "Enterprise" control logic using Redis.
*   **Tasks:**
    *   Set up Redis with an async connection pool.
    *   Implement a "pre-check" middleware: Verify API key and check if budget in Redis is > 0.
    *   Implement "Hard Limits" (reject request) and "Soft Limits" (allow but flag).
    *   Build the credit allocation logic (allocate to Teams/Users).

### Phase 3: Async Semantic Caching
*   **Goal:** Use `pgvector` to save costs on repeated queries.
*   **Tasks:**
    *   Integrate an async embedding client (e.g., OpenAI or a local model).
    *   Perform a vector similarity search in Postgres before hitting the LLM.
    *   Return cached results using `StreamingResponse` for consistent UX.

### Phase 4: Enterprise UI & PII Masking
*   **Goal:** Add the Dashboard and security layer.
*   **Tasks:**
    *   Build the Next.js Dashboard for managing organizations and viewing spend analytics.
    *   Add an async PII masking layer using regex or a specialized service.
    *   Implement Audit Logs (exportable CSV/JSON).

## 5. Next Steps
1.  Confirm that **FastAPI + Asyncpg + Redis** satisfies the concurrency requirements.
2.  Begin Project Scaffolding: Set up the FastAPI directory structure and Docker Compose (Postgres, Redis, App).
