import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.asyncio
async def test_admin_create_key_missing_auth(client):
    response = await client.post("/v1/admin/keys?email=test@test.com")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_create_key_wrong_auth(client, mock_db_session):
    response = await client.post(
        "/v1/admin/keys?email=test@test.com",
        headers={"Authorization": "Bearer wrong-key"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_create_key_success(client, mock_db_session):
    mock_db_session.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = None
    settings.ADMIN_API_KEY = "test-admin-key"
    response = await client.post(
        "/v1/admin/keys?email=newuser@test.com",
        headers={"Authorization": "Bearer test-admin-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["api_key"].startswith("eag_")

@pytest.mark.asyncio
async def test_admin_list_keys_success(client, mock_db_session):
    settings.ADMIN_API_KEY = "test-admin-key"
    response = await client.get(
        "/v1/admin/keys",
        headers={"Authorization": "Bearer test-admin-key"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_admin_logs_export_json(client, mock_db_session):
    settings.ADMIN_API_KEY = "test-admin-key"
    response = await client.get(
        "/v1/admin/logs/export?format=json",
        headers={"Authorization": "Bearer test-admin-key"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

@pytest.mark.asyncio
async def test_admin_logs_export_csv(client, mock_db_session):
    settings.ADMIN_API_KEY = "test-admin-key"
    response = await client.get(
        "/v1/admin/logs/export?format=csv",
        headers={"Authorization": "Bearer test-admin-key"}
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
