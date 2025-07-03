import pytest
from unittest.mock import AsyncMock
from sse_starlette.sse import ServerSentEvent
from fastapi.testclient import TestClient
from prototype.backend_server.app import app

@pytest.fixture
def auth_key(monkeypatch) -> str:
    """Fixture to set the API_AUTH_KEY environment variable."""
    key = "testkey"
    monkeypatch.setenv(name='API_AUTH_KEY', value=key)
    return key

@pytest.fixture
def fx_simple_request_with_auth(auth_key: str) -> tuple[dict[str, str], dict[str, dict]]:
    """Fixture for a simple request with correct authentication."""
    headers = {"APIAuth": auth_key}
    body = {
        "input": {
            "question": "What is the rule about?",
            "session_id": "session_0",
            "user_id": "user_0",
            "generate_title": True
        }
    }
    return headers, body

@pytest.fixture
def fx_simple_request_without_auth() ->  tuple[dict[str, str], dict[str, dict]]:
    """Fixture for a simple request with incorrect authentication."""
    headers = {"APIAuth": "invalid_key"}
    body = {
        "input": {
            "question": "What is the rule about?",
            "session_id": "session_0",
            "user_id": "user_0",
            "generate_title": True
        }
    }
    return headers, body

@pytest.fixture
def fx_mock_sse_generator():
    """Fixture for a mock SSE async generator."""
    async def mock_astream(**kwargs):
        yield ServerSentEvent(data={"context": "This is a test context."})
        yield ServerSentEvent(data={"answer": "This is a test answer."})
        if (kwargs["generate_title"]):
            yield ServerSentEvent(data={"title": "This is a test title."})

    return mock_astream

@pytest.fixture
def fx_client() -> TestClient:
    """Fixture for the FastAPI test client."""
    return TestClient(app)