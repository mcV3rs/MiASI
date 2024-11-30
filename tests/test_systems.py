import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from miasi.ext.database import db
from miasi.models import System, Form, User, SystemForm


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


def test_system1_forms(client, setup_system):
    """Test the forms associated with a system."""
    with client.application.app_context():
        # Retrieve the system within the context
        system = System.query.get(1)
        response = client.get(f"/system/{system.id}")
        assert response.status_code == 200
        assert b"Kalkulator BMI" in response.data

def test_system2_forms(client, setup_system):
    """Test the forms associated with a system."""
    with client.application.app_context():
        # Retrieve the system within the context
        system = System.query.get(3)
        response = client.get(f"/system/{system.id}")
        assert response.status_code == 200
        assert b"Kalkulator AMR" in response.data


def test_system_in_database(client, setup_system):
    """Test if the system exists in the database."""
    with client.application.app_context():
        system = System.query.get(setup_system["systems"][0].id)
        assert system is not None
        assert system.name == "BMI_Calculator"


def test_system1_form_submission(client, setup_system):
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

def test_system2_form_submission(client, setup_system):
    """Test form submission and equation calculation."""
    with client.application.app_context():
        system_id = setup_system["systems"][1].id
        data = {"height": "1.75", "weight": "70", "age": "25", "sex": "1"}
        response = client.post(f"/api/v1/system/{system_id}/form/submit", json=data)
        result = response.json["results"]

        assert response.status_code == 201

        assert "message" in response.json
        assert "Equations calculated successfully, but no advice available" in response.json["message"]

        assert "results" in response.json
        assert 'equation_name' in result[0]
        assert 'Basal Metabolic Rate - Male' in result[0]['equation_name']

        assert 'result' in result[0]
        assert result[0]['result'] == pytest.approx(1755, rel=1e-2)


def test_system3_form_submission(client, setup_system):
    """Test form submission and equation calculation."""
    with client.application.app_context():
        system_id = setup_system["systems"][2].id
        data = {"height": "1.75", "weight": "70", "age": "25", "sex": "1", "activity_level": "1.8"}

        response = client.post(f"/api/v1/system/{system_id}/form/submit", json=data)
        result = response.json["results"]

        assert response.status_code == 201

        assert "message" in response.json
        assert "Equations calculated successfully, but no advice available" in response.json["message"]

        assert "results" in response.json
        assert 'equation_name' in result[0]
        assert 'Active Metabolic Rate - Male' in result[0]['equation_name']

        assert 'result' in result[0]
        assert result[0]['result'] == pytest.approx(3159, rel=1e-2)


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


def test_hash_password():
    """Test funkcji hash_password()"""
    plain_password = "my_secure_password"
    hashed_password = User.hash_password(plain_password)

    assert hashed_password is not None
    assert hashed_password != plain_password
    assert check_password_hash(hashed_password, plain_password)


def test_create_system_form_with_objects(app, setup_system):
    """Test tworzenia SystemForm za pomocą obiektów System i Form."""
    system = setup_system["systems"][3]
    form = setup_system["forms"][0]

    # Tworzenie SystemForm za pomocą obiektów
    system_form = SystemForm(system=system, form=form)

    # Dodanie do sesji i commit
    with app.app_context():
        db.session.add(system_form)
        db.session.commit()

        # Pobranie obiektu z bazy
        retrieved_system_form = SystemForm.query.filter_by(id_system=system.id, id_form=form.id).first()

        assert retrieved_system_form is not None
        assert retrieved_system_form.id_system == system.id
        assert retrieved_system_form.id_form == form.id


def test_create_system_form_with_ids(app, setup_system):
    """Test tworzenia SystemForm za pomocą ID systemu i formularza."""
    system = setup_system["systems"][0]
    form = setup_system["forms"][0]
    system_form = SystemForm(id_system=system.id, id_form=form.id)

    assert system_form.id_system == system.id
    assert system_form.id_form == form.id
    assert system_form.system is None
    assert system_form.form is None


def test_create_system_form_with_missing_parameters():
    with pytest.raises(ValueError) as excinfo:
        SystemForm()
    assert "Either system and form objects or id_system and id_form must be provided" in str(excinfo.value)
