from app.db.session import async_session
from app.models.usage import RequestLog
from app.models.guardrail_log import GuardrailLog
from app.core.guardrails.base import GuardrailResult

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


async def log_guardrail_results(
    results: list[GuardrailResult],
    guardrail_names: list[str],
    request_id: str | None = None,
    side: str | None = None,
):
    if not results:
        return
    async with async_session() as session:
        for result, name in zip(results, guardrail_names):
            entry = GuardrailLog(
                guardrail_name=name,
                side=side,
                action_taken=result.action,
                reason=result.reason,
                matched_pattern=result.matched_pattern,
                score=str(result.metadata.get("score", "")) if result.metadata else None,
                request_id=request_id or "",
                extra_data=result.metadata if result.metadata else None,
            )
            session.add(entry)
        await session.commit()
