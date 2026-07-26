def test_health_and_openapi(client):
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["database"] == "connected"

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert "/api/v1/auth/login" in openapi.json()["paths"]
