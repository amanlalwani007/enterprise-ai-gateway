from fastapi import FastAPI
from app.api.v1 import chat

app = FastAPI(title="Enterprise AI Gateway")

app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Enterprise AI Gateway is running"}
