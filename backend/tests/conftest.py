import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture(autouse=True)
def apply_config():
    with patch("app.core.config.settings") as mock:
        mock.BUDGET_ENABLED = True
        mock.DEFAULT_BUDGET = 1000.0
        mock.DEFAULT_COST_PER_REQUEST = 0.001
        mock.RATE_LIMIT_ENABLED = True
        mock.RATE_LIMIT_REQUESTS = 60
        mock.RATE_LIMIT_WINDOW_SECONDS = 60
        mock.CACHE_ENABLED = True
        mock.CACHE_SIMILARITY_THRESHOLD = 0.95
        mock.PII_MASKING_ENABLED = True
        mock.GUARDRAILS_ENABLED = False
        mock.GUARDRAILS_CONFIG_PATH = ""
        mock.ADMIN_API_KEY = "test-admin-key"
        mock.EMBEDDING_MODEL = "text-embedding-3-small"
        mock.MODEL_ROUTES = None
        mock.DB_ECHO_SQL = False
        yield mock

@pytest.fixture
def mock_redis():
    with patch("app.core.redis_utils.redis_client") as mock:
        mock.get = AsyncMock(return_value="1000")
        mock.incr = AsyncMock(return_value=1)
        mock.expire = AsyncMock(return_value=True)
        mock.decrbyfloat = AsyncMock(return_value=True)
        mock.ping = AsyncMock(return_value=True)
        yield mock

@pytest.fixture
def mock_auth_user():
    with patch("app.api.v1.chat.async_session") as mock:
        session = AsyncMock()
        user = MagicMock()
        user.is_active = True
        session.execute.return_value.scalar_one_or_none.return_value = user
        session.__aenter__.return_value = session
        mock.return_value = session
        yield mock

@pytest.fixture
def mock_db_session():
    with patch("app.db.session.async_session") as mock:
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.close = AsyncMock()
        session.__aenter__.return_value = session
        mock.return_value = session
        yield mock

@pytest.fixture
def mock_litellm():
    with patch("app.api.v1.chat.litellm.acompletion") as mock:
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "Mock response"
        response.choices[0].delta.content = "Mock response"
        response.usage.prompt_tokens = 10
        response.usage.completion_tokens = 20
        response.usage.total_tokens = 30
        response.model_dump.return_value = {"choices": [{"message": {"content": "Mock response"}}]}
        mock.return_value = response
        yield mock

@pytest.fixture
def mock_semantic_cache():
    with patch("app.api.v1.chat.find_semantic_cache", new_callable=AsyncMock) as mock:
        mock.return_value = None
        yield mock

@pytest.fixture
def mock_save_cache():
    with patch("app.api.v1.chat.save_to_semantic_cache", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_log_db():
    with patch("app.api.v1.chat.log_request_to_db", new_callable=AsyncMock) as mock:
        yield mock
