def test_create_db(cli_runner, setup_db):
    """Test komendy `create_db`."""
    result = cli_runner.invoke(args=["create-db"])
    assert result.exit_code == 0
    assert "Database created" in result.output

def test_drop_db(cli_runner, setup_db):
    """Test komendy `drop_db`."""
    result = cli_runner.invoke(args=["drop-db"])
    assert result.exit_code == 0
    assert "Database dropped" in result.output

def test_populate_db(cli_runner, setup_db):
    """Test komendy `populate_db`."""
    result = cli_runner.invoke(args=["populate-db"])
    assert result.exit_code == 0
    assert "Database populated" in result.output

def test_reset_db(cli_runner, setup_db):
    """Test komendy `reset_db`."""
    result = cli_runner.invoke(args=["reset-db"])
    assert result.exit_code == 0
    assert "Database reset and ready to use" in result.output

def test_add_user(cli_runner, setup_db):
    """Test komendy `add_user`."""
    username = "test_user"
    password = "test_pass"
    result = cli_runner.invoke(args=["add-user", "-u", username, "-p", password])
    assert result.exit_code == 0
    # Sprawdzenie, czy użytkownik został poprawnie dodany
    from miasi.ext.auth import User
    with db.session.begin():
        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.username == username
