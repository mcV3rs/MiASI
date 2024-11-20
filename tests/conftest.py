import sys
import pytest

from miasi import create_app
from miasi.ext.database import db


@pytest.fixture()
def app():
    app = create_app(FORCE_ENV_FOR_DYNACONF="testing")
    with app.app_context():
        yield app

@pytest.fixture
def cli_runner(app):
    """Fixture dostarczająca `cli_runner` do testowania komend CLI."""
    return app.test_cli_runner()

@pytest.fixture
def setup_db(app):
    """Fixture inicjalizująca i czyszcząca bazę danych przed i po testach."""
    with app.app_context():
        db.create_all()
        yield
        db.drop_all()

# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield
