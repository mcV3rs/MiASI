from miasi.models import System, Form, Equation, SystemForm, User


def test_create_db(cli_runner):
    """Test creating the database."""
    result = cli_runner.invoke(args=["create-db"])
    assert result.exit_code == 0, result.output
    assert "Database created" in result.output

def test_drop_db(cli_runner):
    """Test dropping the database."""
    result = cli_runner.invoke(args=["drop-db"])
    assert result.exit_code == 0
    assert "Database dropped" in result.output

def test_populate_db(cli_runner, app):
    """Test populating the database with sample data."""
    cli_runner.invoke(args=["create-db"])  # Upewnij się, że baza istnieje
    result = cli_runner.invoke(args=["populate-db"])
    assert result.exit_code == 0

    # Sprawdź, czy dane zostały dodane do bazy
    with app.app_context():
        assert System.query.count() > 0
        assert Form.query.count() > 0
        assert Equation.query.count() > 0
        assert SystemForm.query.count() > 0

def test_reset_db(cli_runner, app):
    """Test resetting the database."""
    result = cli_runner.invoke(args=["reset-db"])
    assert result.exit_code == 0
    assert "Database reset and ready to use" in result.output

    # Sprawdź, czy baza została zresetowana i wypełniona
    with app.app_context():
        assert System.query.count() > 0
        assert Form.query.count() > 0
        assert Equation.query.count() > 0
        assert SystemForm.query.count() > 0
        assert User.query.count() > 0

def test_add_user(cli_runner, app):
    """Test adding a user through CLI."""
    result = cli_runner.invoke(args=["add-user", "-u", "test_user", "-p", "test_password"])
    assert result.exit_code == 0

    # Sprawdź, czy użytkownik został dodany
    from miasi.ext.auth import User
    with app.app_context():
        user = User.query.filter_by(username="test_user").first()
        assert user is not None
