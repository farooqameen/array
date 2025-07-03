import pytest
import json
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from prototype.backend_server.app import app
from tests.prototype_test.backend_server_test.conftest import (
    fx_simple_request_with_auth,
    fx_simple_request_without_auth,
    fx_mock_sse_generator,
    fx_client, 
)
import asyncio

def test_health_endpoint(fx_client):
    response = fx_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"health": "OK!"}

@pytest.mark.asyncio(loop_scope="session")
@patch("prototype.backend_server.app.RunnableWithMessageHistory")
@patch("prototype.backend_server.app.g_solution")
@patch("prototype.backend_server.app.stream_generator_esr")
async def test_stream_endpoint(
    mock_stream_generator_esr, 
    mock_runnable_with_message_history, 
    mock_g_solution,
    fx_simple_request_with_auth, 
    fx_mock_sse_generator,
):
    mock_stream_generator_esr.side_effect = fx_mock_sse_generator
    # Define the headers and body for the request
    headers, body = fx_simple_request_with_auth
    
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        async with async_client.stream("POST", "/stream", json=body, headers=headers) as response:
            assert response.status_code == 200, "Expected status code 200 but got {response.status_code}"

            event_count = 0
            async for event in response.aiter_lines():
                if event.startswith('data:'):
                    event_count += 1
                    data = event.replace('data:', '', 1).strip().replace("'", '"')
                    assert data, "Empty data received from stream"

                    token = json.loads(data)

                    assert 'context' in token or 'answer' in token or 'title' in token, "Unexpected token in stream data"

            assert event_count > 0, "No events were received in the stream"

@pytest.mark.asyncio(loop_scope="session")
@patch("prototype.backend_server.app.RunnableWithMessageHistory")
@patch("prototype.backend_server.app.g_solution")
@patch("prototype.backend_server.app.stream_generator_esr")
async def test_stream_endpoint_without_title(
    mock_stream_generator_esr, 
    mock_runnable_with_message_history, 
    mock_g_solution,
    fx_simple_request_with_auth, 
    fx_mock_sse_generator,
):
    mock_stream_generator_esr.side_effect = fx_mock_sse_generator
    # Define the headers and body for the request
    headers, body = fx_simple_request_with_auth
    del body["input"]["generate_title"]
    
    # current_loop = asyncio.get_running_loop()
    
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        async with async_client.stream("POST", "/stream", json=body, headers=headers) as response:
            assert response.status_code == 200, "Expected status code 200 but got {response.status_code}"

            event_count = 0
            async for event in response.aiter_lines():
                if event.startswith('data:'):
                    event_count += 1
                    data = event.replace('data:', '', 1).strip().replace("'", '"')
                    assert data, "Empty data received from stream"

                    token = json.loads(data)

                    assert 'context' in token or 'answer' in token, "Unexpected token in stream data"
                    assert 'title' not in token, "Unexpected 'title' key found in token"

            assert event_count > 0, "No events were received in the stream"

@pytest.mark.asyncio
async def test_stream_endpoint_unauthorized(fx_simple_request_without_auth):
    headers, body = fx_simple_request_without_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.post("/stream", json=body, headers=headers)

        assert response.status_code == 403, "Expected status code 403 but got {response.status_code}"
        assert response.json()["detail"] == "Unauthorized", "Unexpected error detail for unauthorized access"


@pytest.mark.asyncio
async def test_stream_endpoint_empty_body(fx_simple_request_with_auth):
    headers = fx_simple_request_with_auth[0]
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        response = await async_client.post("/stream", json={}, headers=headers)

        assert response.status_code == 422, "Expected status code 422 but got {response.status_code}"