from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Header
from fastapi.responses import StreamingResponse
from app.db.utils import log_request_to_db
from app.core.redis_utils import check_budget_cache, update_budget_cache, check_rate_limit
from app.core.cache_utils import find_semantic_cache, save_to_semantic_cache
from app.core.security import mask_pii
from app.core.routing import router as model_router
import hashlib
import litellm
import os
import json

router = APIRouter()

@router.post("/completions")
async def chat_completions(
    request: Request, 
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    # 1. Simple Auth Check
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    
    api_key = authorization.split(" ")[1]
    
    # 2. Rate Limit Check (Redis)
    is_allowed = await check_rate_limit(api_key)
    if not is_allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # 3. Budget Check (Redis)
    has_budget, remaining = await check_budget_cache(api_key)
    if not has_budget:
        raise HTTPException(status_code=402, detail="Budget exceeded")

    data = await request.json()
    
    # 4. PII Masking
    for message in data.get("messages", []):
        if message.get("content"):
            message["content"] = mask_pii(message["content"])

    prompt = data.get("messages", [])[-1].get("content", "")
    
    # 5. Semantic Cache Check
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

    # 6. Model routing
    model_name = data.get("model", "gpt-4")
    route = model_router.resolve(model_name)
    if route.get("provider"):
        data["model"] = route["model"]
        litellm.api_base = route.get("api_base")
    del model_name

    # 7. Proxy to LiteLLM
    try:
        response = await litellm.acompletion(
            **data,
            stream=data.get("stream", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    user_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
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
            
            background_tasks.add_task(update_budget_cache, api_key, 1)
            
            background_tasks.add_task(log_request_to_db, user_id=user_hash, model=data.get("model"), 
                                    prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, 
                                    total_tokens=prompt_tokens + completion_tokens,
                                    request_data=data, response_data={"full_text": full_response})
            
            background_tasks.add_task(save_to_semantic_cache, prompt=prompt, response=full_response, model=data.get("model"))
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    
    # 7. Non-streaming cleanup
    full_response = response.choices[0].message.content
    background_tasks.add_task(save_to_semantic_cache, prompt=prompt, response=full_response, model=data.get("model"))
    
    await update_budget_cache(api_key, 1)
    background_tasks.add_task(log_request_to_db, user_id=user_hash, model=data.get("model"),
                            prompt_tokens=response.usage.prompt_tokens if response.usage else 0, 
                            completion_tokens=response.usage.completion_tokens if response.usage else 0,
                            total_tokens=response.usage.total_tokens if response.usage else 0,
                            request_data=data, response_data=response.model_dump())
    
    return response
