def test_get_all_systems(client):
    response = client.get("/systems")
    assert response.status_code == 200
    assert response.json == []
