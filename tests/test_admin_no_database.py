import os


def test_no_database_export_view(client, login_as_admin):
    """
    Test accessing the Export Database view when no database file is present.
    """
    # Usuń bazę danych przed wykonaniem testu
    db_uri = client.application.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
    db_path = os.path.join(client.application.instance_path, db_uri)

    if os.path.exists(db_path):
        os.remove(db_path)  # Usuń plik bazy danych, aby symulować jego brak

    # Wywołanie widoku eksportu bazy danych
    response = client.get("/admin/download-database/")

    # Sprawdzenie odpowiedzi
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Database file not found.' in response.data