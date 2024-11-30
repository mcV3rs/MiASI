import os
import sqlite3
import tempfile

import pytest
from werkzeug.security import generate_password_hash

from miasi import create_app
from miasi.ext.database import db
from miasi.models import System, Form, Equation, Knowledge, SystemForm, User


@pytest.fixture(scope="module")
def app():
    """Fixture to create a test instance of the application."""
    if os.path.exists("instance/testing.db"):
        os.remove("instance/testing.db")

    app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
    db_path = os.path.join(app.instance_path, "testing.db")

    with app.app_context():
        db.create_all()  # Tworzenie schematu bazy danych
        yield app

        # Usuwanie sesji i pliku bazy danych po zakończeniu testów
        db.session.remove()
        db.drop_all()
        if os.path.exists(db_path):
            os.remove(db_path)


@pytest.fixture(scope="module")
def isolated_app():
    """Fixture to create a test instance of the application."""
    isolated_app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
    isolated_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    isolated_app.config["TESTING"] = True

    with isolated_app.app_context():
        db.create_all()
        yield isolated_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    """Fixture to create a test client."""
    return app.test_client()

@pytest.fixture
def isolated_client(isolated_app):
    """Fixture to create a test client."""
    return isolated_app.test_client()


@pytest.fixture(scope="module")
def setup_system(app):
    """Fixture to create a sample system."""
    with app.app_context():
        systems = [
            System(name="BMI_Calculator", name_human_readable="Kalkulator BMI",
                   description="System, który umożliwi Ci sprawdzenie swojego BMI"),
            System(name="BMR_Calculator", name_human_readable="Kalkulator BMR",
                   description="Kalkulator, który pozwoli Ci obliczyć zapotrzebowanie kaloryczne (BMR)"),
            System(name="AMR_Calculator", name_human_readable="Kalkulator AMR",
                   description="Kalkulator, który pozwoli Ci obliczyć zapotrzebowanie kaloryczne (AMR)"),
            System(name="Test_No_Equations", name_human_readable="Testowy system bez równań", description="Test"),
            System(name="Test_Many_Advices", name_human_readable="Testowy system z wieloma poradami", description="Test", system_type=True)
        ]

        forms = [
            Form(name="height", name_human_readable="Wzrost", input_type="number",
                 description="Wzrost w metrach"),
            Form(name="weight", name_human_readable="Waga", input_type="number",
                 description="Waga w kilogramach"),
            Form(name="age", name_human_readable="Wiek", input_type="number",
                 description="Wiek w pełnych latach"),
            Form(name="sex", name_human_readable="Płeć", input_type="sex",
                 description="Wybierz swoją płeć"),
            Form(name="activity_level", name_human_readable="Poziom aktywności", input_type="select",
                 select_options="1; 1.2; 1.4; 1.6; 1.8",
                 select_values="Siedzący; Mało aktywny; Umiarkowanie aktywny; Aktywny; Bardzo aktywny",
                 description="Wybierz swój poziom aktywności")
        ]

        equations = [
            Equation(id_system=1, name="BMI", name_human_readable="Body Mass Index",
                     formula="weight / (height ** 2)"),
            Equation(id_system=2, name="BMR_Male", name_human_readable="Basal Metabolic Rate - Male",
                     formula="66 + (13.7 * weight) + (500 * height) - (5.8 * age)", sex=1),
            Equation(id_system=2, name="BMR_Female", name_human_readable="Basal Metabolic Rate - Female",
                     formula="655 + (9.6 * weight) + (180 * height) - (4.7 * age)", sex=0),
            Equation(id_system=3, name="AMR", name_human_readable="Active Metabolic Rate - Female",
                     formula="round((655 + (9.6 * weight) + (180 * height) - (4.7 * age) ) * activity_level)", sex=0),
            Equation(id_system=3, name="AMR", name_human_readable="Active Metabolic Rate - Male",
                        formula="round((66 + (13.7 * weight) + (500 * height) - (5.8 * age) ) *  activity_level)", sex=1)
        ]

        knowledge = [
            Knowledge(id_system=1, condition="0 <= BMI < 18.5",
                      advice="Twoja waga jest zbyt niska. Rozważ konsultację z dietetykiem."),
            Knowledge(id_system=1, condition="18.5 <= BMI < 25",
                      advice="Twoja waga jest w normie. Utrzymuj zdrowy styl życia!"),
            Knowledge(id_system=1, condition="25 <= BMI < 30",
                      advice="Masz nadwagę. Rozważ zwiększenie aktywności fizycznej i konsultację z dietetykiem."),
            Knowledge(id_system=1, condition="BMI >= 30",
                      advice="Masz otyłość. Skonsultuj się z lekarzem i dietetykiem."),
            Knowledge(id_system=5, condition="height == 0", advice="Rada 1"),
            Knowledge(id_system=5, condition="weight == 0", advice="Rada 2"),
        ]

        system_forms = [
            SystemForm(id_system=1, id_form=1),
            SystemForm(id_system=1, id_form=2),
            SystemForm(id_system=2, id_form=1),
            SystemForm(id_system=2, id_form=2),
            SystemForm(id_system=2, id_form=3),
            SystemForm(id_system=2, id_form=4),
            SystemForm(id_system=3, id_form=1),
            SystemForm(id_system=3, id_form=2),
            SystemForm(id_system=3, id_form=3),
            SystemForm(id_system=3, id_form=4),
            SystemForm(id_system=3, id_form=5),
            SystemForm(id_system=5, id_form=1),
            SystemForm(id_system=5, id_form=2),
        ]

        db.session.bulk_save_objects(systems)
        db.session.bulk_save_objects(forms)
        db.session.bulk_save_objects(equations)
        db.session.bulk_save_objects(knowledge)
        db.session.bulk_save_objects(system_forms)

        db.session.commit()

        return {
            "systems": System.query.all(),
            "forms": Form.query.all(),
            "equations": Equation.query.all(),
            "knowledge": Knowledge.query.all(),
            "system_forms": SystemForm.query.all()
        }

@pytest.fixture(scope="module")
def cli_runner(app):
    """Fixture dostarczająca `cli_runner` do testowania komend CLI."""
    return app.test_cli_runner()

@pytest.fixture(scope="module")
def setup_test_database(app):
    """Fixture to create a temporary database file in instance/."""
    file_path = os.path.join(app.instance_path, "development.db")

    # Upewnij się, że katalog instance/ istnieje
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Tworzenie pliku testowego
    with open(file_path, "w") as f:
        f.write("Test database content")

    yield file_path


@pytest.fixture
def upload_test_file(app):
    """Fixture to create a temporary .db file for testing upload."""
    db_file = os.path.join(app.instance_path, "test_database.db")
    os.makedirs(app.instance_path, exist_ok=True)

    with open(db_file, "w") as f:
        f.write("Test database content")

    yield db_file

    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture
def setup_empty_database(app):
    """Fixture to create a valid SQLite database file."""
    db_path = os.path.join(app.instance_path, "test_database.db")
    os.makedirs(app.instance_path, exist_ok=True)

    # Tworzenie poprawnej bazy danych SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
    cursor.execute("INSERT INTO test_table (name) VALUES ('Test Entry');")
    conn.commit()
    conn.close()

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def setup_user(app):
    """Fixture to create a test user in the database."""
    with app.app_context():
        user = User(username="test_user", password=generate_password_hash("test_password"))
        db.session.add(user)
        db.session.commit()

        yield user

        db.session.delete(user)
        db.session.commit()