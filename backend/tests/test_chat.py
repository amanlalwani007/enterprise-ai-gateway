import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import json

@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.asyncio
async def test_chat_completions_missing_api_key(client):
    response = await client.post("/v1/chat/completions", json={"model": "gpt-4", "messages": []})
    assert response.status_code == 401
    assert "API Key" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chat_completions_invalid_api_key(client):
    response = await client.post(
        "/v1/chat/completions",
        json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
        headers={"Authorization": "Bearer invalid-key"}
    )
    assert response.status_code in (401, 402, 429, 500)

@pytest.mark.asyncio
async def test_chat_completions_rate_limit_exceeded(client, mock_redis):
    mock_redis.incr.return_value = 100
    response = await client.post(
        "/v1/chat/completions",
        json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
        headers={"Authorization": "Bearer test-key"}
    )
    assert response.status_code == 429
    assert "Rate limit" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chat_completions_budget_exceeded(client, mock_redis):
    mock_redis.get.return_value = "0"
    response = await client.post(
        "/v1/chat/completions",
        json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
        headers={"Authorization": "Bearer test-key"}
    )
    assert response.status_code == 402
    assert "Budget" in response.json()["detail"]

@pytest.mark.asyncio
async def test_chat_completions_success_non_streaming(
    client, mock_redis, mock_litellm, mock_semantic_cache, mock_save_cache, mock_log_db
):
    response = await client.post(
        "/v1/chat/completions",
        json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
        headers={"Authorization": "Bearer test-key"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_chat_completions_success_streaming(
    client, mock_redis, mock_semantic_cache, mock_save_cache, mock_log_db
):
    from unittest.mock import AsyncMock, MagicMock
    async def mock_stream():
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "Hello"
        chunk.choices[0].finish_reason = None
        chunk.usage = None
        chunk.model_dump_json.return_value = '{"choices":[{"delta":{"content":"Hello"}}]}'
        yield chunk
        final = MagicMock()
        final.choices = [MagicMock()]
        final.choices[0].delta.content = None
        final.choices[0].finish_reason = "stop"
        final.usage = MagicMock()
        final.usage.prompt_tokens = 10
        final.usage.completion_tokens = 20
        final.model_dump_json.return_value = '{"choices":[{"delta":{"content":null},"finish_reason":"stop"}]}'
        yield final

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.api.v1.chat.litellm.acompletion", AsyncMock(return_value=mock_stream()))
        response = await client.post(
            "/v1/chat/completions",
            json={"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}], "stream": True},
            headers={"Authorization": "Bearer test-key"}
        )
        assert response.status_code == 200
