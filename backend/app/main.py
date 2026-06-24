from fastapi import FastAPI
from app.api.v1 import chat, admin, observability
from app.core.health import get_health_status
from app.core.tracing import setup_tracing

app = FastAPI(title="Enterprise AI Gateway", version="0.2.0")

app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
app.include_router(admin.router, prefix="/v1/admin", tags=["admin"])
app.include_router(observability.router, prefix="/v1/admin", tags=["observability"])

setup_tracing()

@app.get("/")
async def root():
    return {"message": "Enterprise AI Gateway is running"}

@app.get("/health")
async def health():
    return await get_health_status()
