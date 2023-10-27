import pytest  # type: ignore
from web.backend.app.common.test.app_connection import AppTestClient, init_test_config


@pytest.fixture
def client():
    test_config = init_test_config()
    with AppTestClient(config=test_config) as client:
        yield client


def test_success(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
