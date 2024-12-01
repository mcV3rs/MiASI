import os

def test_form_inputs_view(client, login_as_admin):
    """Test accessing the Form Inputs view."""
    response = client.get("/admin/form/")
    assert response.status_code == 200
    assert b"Form Inputs" in response.data


def test_systems_view(client, login_as_admin):
    """Test accessing the Systems view."""
    response = client.get("/admin/system/")
    assert response.status_code == 200
    assert b"Systems" in response.data


def test_equations_view(client, login_as_admin):
    """Test accessing the Equations view."""
    response = client.get("/admin/equation/")
    assert response.status_code == 200
    assert b"Equations" in response.data


def test_knowledge_base_view(client, login_as_admin):
    """Test accessing the Knowledge Base view."""
    response = client.get("/admin/knowledge/")
    assert response.status_code == 200
    assert b"Knowledge Base" in response.data


def test_export_view(client, login_as_admin, setup_system):
    """Test accessing the Export Database view."""
    response = client.get("/admin/download-database/")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert "attachment" in response.headers["Content-Disposition"]
    assert response.headers["Content-Disposition"].endswith(".db")


def test_no_file_uploaded(client, login_as_admin, setup_system):
    """Test uploading with no file in the request."""
    response = client.post("/admin/import-database/", data={}, follow_redirects=True)

    # Print the response text for debugging
    print("Response text:", response.get_data(as_text=True))

    assert response.status_code == 200  # Redirect to the same page
    assert b"No file part in the request." in response.data


def test_empty_file_selection(client, login_as_admin):
    """Test uploading with no file selected."""
    response = client.post("/admin/import-database/", data={"file": ""}, follow_redirects=True)

    print("Response status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response text:", response.get_data(as_text=True))  # Debugowanie treści odpowiedzi

    assert response.status_code == 200
    assert b"No file part in the request." in response.data


def test_invalid_file_format(client, login_as_admin):
    """Test uploading a file with an invalid extension."""
    invalid_file_path = "invalid_file.txt"

    with open(invalid_file_path, "wb") as f:
        f.write(b"Invalid content")  # Zapisz binarne dane

    with open(invalid_file_path, "rb") as invalid_file:  # Otwórz w trybie binarnym
        data = {"file": (invalid_file, "invalid_file.txt")}
        response = client.post("/admin/import-database/", data=data, content_type="multipart/form-data", follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid file format. Please upload a .db file." in response.data

    os.remove(invalid_file_path)  # Usuń plik po teście


def test_valid_db_upload(client, login_as_admin, setup_empty_database):
    """Test uploading a valid .db file."""
    with open(setup_empty_database, "rb") as db_file:
        data = {"file": (db_file, "test_database.db")}
        response = client.post("/admin/import-database/", data=data, content_type="multipart/form-data", follow_redirects=True)

    assert response.status_code == 200
    assert b"Database imported successfully" in response.data
