def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.get_json()["db"] == "ok"


def test_health_unknown_api_path_returns_json(client):
    response = client.get("/api/v1/unknown")
    assert response.status_code == 404
    assert response.is_json
