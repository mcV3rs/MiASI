def test_no_database_export_view(isolated_client):
    """Test accessing the Export Database view, when no database is present."""
    response = isolated_client.get("/admin/download-database/")
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Database file not found.' in response.data