from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Header
from fastapi.responses import StreamingResponse
from app.db.utils import log_request_to_db
from app.core.redis_utils import check_budget_cache, update_budget_cache, check_rate_limit
from app.core.cache_utils import find_semantic_cache, save_to_semantic_cache
from app.core.security import mask_pii
from app.core.routing import router as model_router
from app.core.config import settings
from app.db.session import async_session
from app.models.enterprise import User
from sqlalchemy import select
import hashlib
import litellm
import json

router = APIRouter()

@router.post("/completions")
async def chat_completions(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")

    raw_api_key = authorization.split(" ")[1]
    api_key_hash = hashlib.sha256(raw_api_key.encode()).hexdigest()

    async with async_session() as session:
        result = await session.execute(select(User).where(User.api_key == api_key_hash, User.is_active == True))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or revoked API Key")

    api_key = raw_api_key

    # Optional rate limiting
    if settings.RATE_LIMIT_ENABLED:
        is_allowed = await check_rate_limit(api_key)
        if not is_allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Optional budget check
    if settings.BUDGET_ENABLED:
        has_budget, _ = await check_budget_cache(api_key)
        if not has_budget:
            raise HTTPException(status_code=402, detail="Budget exceeded")

    data = await request.json()

    # Optional PII masking
    if settings.PII_MASKING_ENABLED:
        for message in data.get("messages", []):
            if message.get("content"):
                message["content"] = mask_pii(message["content"])

    messages = data.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="At least one message is required")
    prompt = messages[-1].get("content", "")

    # Optional semantic cache check
    if settings.CACHE_ENABLED:
        cached_response = await find_semantic_cache(prompt)
        if cached_response:
            if data.get("stream"):
                async def stream_cached():
                    chunk = {
                        "choices": [{"delta": {"content": cached_response}, "index": 0, "finish_reason": "stop"}]
                    }
                    yield f"data: {json.dumps(chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                return StreamingResponse(stream_cached(), media_type="text/event-stream")
            return {"choices": [{"message": {"content": cached_response}, "index": 0, "finish_reason": "stop"}]}

    # Model routing
    model_name = data.get("model", "gpt-4")
    route = model_router.resolve(model_name)
    if route.get("provider") and route.get("model"):
        data["model"] = route["model"]

    # Proxy to LiteLLM
    try:
        response = await litellm.acompletion(
            **data,
            stream=data.get("stream", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    user_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    cost = settings.DEFAULT_COST_PER_REQUEST

    if data.get("stream"):
        async def stream_generator():
            full_response = ""
            prompt_tokens = 0
            completion_tokens = 0
            async for chunk in response:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                if chunk.usage:
                    prompt_tokens = chunk.usage.prompt_tokens or 0
                    completion_tokens = chunk.usage.completion_tokens or 0
                yield f"data: {chunk.model_dump_json()}\n\n"

            background_tasks.add_task(update_budget_cache, api_key, cost)

            background_tasks.add_task(log_request_to_db, user_id=user_hash, model=data.get("model"),
                                    prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                                    total_tokens=prompt_tokens + completion_tokens, cost=cost,
                                    request_data=data, response_data={"full_text": full_response})

            if settings.CACHE_ENABLED:
                background_tasks.add_task(save_to_semantic_cache, prompt=prompt, response=full_response, model=data.get("model"))

            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    # Non-streaming
    full_response = response.choices[0].message.content

    background_tasks.add_task(update_budget_cache, api_key, cost)

    if settings.CACHE_ENABLED:
        background_tasks.add_task(save_to_semantic_cache, prompt=prompt, response=full_response, model=data.get("model"))

    background_tasks.add_task(log_request_to_db, user_id=user_hash, model=data.get("model"),
                            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                            completion_tokens=response.usage.completion_tokens if response.usage else 0,
                            total_tokens=response.usage.total_tokens if response.usage else 0, cost=cost,
                            request_data=data, response_data=response.model_dump())

    return response
