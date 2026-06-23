from app.db.session import async_session
from app.models.usage import RequestLog

async def log_request_to_db(
    user_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    request_data: dict,
    response_data: dict,
    cost: float = 0.0
):
    async with async_session() as session:
        log = RequestLog(
            user_id=user_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            request_data=request_data,
            response_data=response_data
        )
        session.add(log)
        await session.commit()
