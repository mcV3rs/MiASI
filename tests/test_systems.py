import pytest
from miasi.ext.database import db
from miasi.models import System, Form

def test_database_isolation(app):
    """Ensure the database is isolated for tests."""
    with app.app_context():
        # Sprawdź, czy baza jest pusta po inicjalizacji
        assert System.query.count() == 0
        assert Form.query.count() == 0


def test_system_list(client, setup_system):
    """Test the list of available systems."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Kalkulator BMI" in response.data


def test_system_forms(client, setup_system):
    """Test the forms associated with a system."""
    with client.application.app_context():
        # Retrieve the system within the context
        system = System.query.get(1)
        response = client.get(f"/system/{system.id}")
        assert response.status_code == 200
        assert b"Kalkulator BMI" in response.data


def test_system_in_database(client, setup_system):
    """Test if the system exists in the database."""
    with client.application.app_context():
        system = System.query.get(setup_system["systems"][0].id)
        assert system is not None
        assert system.name == "BMI_Calculator"


def test_system_form_submission(client, setup_system):
    """Test form submission and equation calculation."""
    with client.application.app_context():
        system_id = setup_system["systems"][0].id
        data = {"height": "1.75", "weight": "70"}
        response = client.post(f"/api/v1/system/{system_id}/form/submit", json=data)
        result = response.json["results"]

        assert response.status_code == 201

        assert "message" in response.json
        assert "Equations calculated successfully with advice" in response.json["message"]

        assert "advice" in response.json
        assert "Twoja waga jest w normie" in response.json["advice"]

        assert "results" in response.json
        assert 'equation_name' in result[0]
        assert 'Body Mass Index' in result[0]['equation_name']

        assert 'result' in result[0]
        assert result[0]['result'] == pytest.approx(22.86, rel=1e-2)


def test_add_system(app):
    """Test adding a new system to the database."""
    with app.app_context():
        new_system = System(name="New_System", name_human_readable="New System",
                            description="System for testing additions.")
        db.session.add(new_system)
        db.session.commit()

        retrieved_system = System.query.filter_by(name="New_System").first()
        assert retrieved_system is not None
        assert retrieved_system.name_human_readable == "New System"


def test_update_system(app, setup_system):
    """Test updating an existing system in the database."""
    with app.app_context():
        # Get the last system from the setup
        system = System.query.get(setup_system["systems"][-1].id)
        assert system is not None

        system.name_human_readable = "Updated System"
        db.session.commit()

        updated_system = System.query.get(system.id)
        assert updated_system.name_human_readable == "Updated System"


def test_delete_system(app, setup_system):
    """Test deleting a system from the database."""
    with app.app_context():
        # Add system to the database
        system = System(name="Delete_System", name_human_readable="Delete System",
                        description="System for testing deletions.")
        db.session.add(system)
        db.session.commit()

        assert system is not None

        db.session.delete(system)
        db.session.commit()

        deleted_system = System.query.get(system.id)
        assert deleted_system is None
