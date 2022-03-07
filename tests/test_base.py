from fastapi.testclient import TestClient

from app import app

# TODO: Add .env environment variable export
test_client = TestClient(app)


def test_server_running():
    response = test_client.get("/")
    assert response.json() == {"detail": "Not Found"}
