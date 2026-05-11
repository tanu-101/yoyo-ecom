from __future__ import annotations


def test_health_check(api_client):
    response = api_client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_public_api_health_check(api_client):
    response = api_client.get("/api/v1/public/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
