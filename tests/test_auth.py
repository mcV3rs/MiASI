import pytest
from miasi.ext.auth import verify_login, create_user
from miasi.models import User


def test_verify_login_valid_user(app, setup_user):
    """Test successful login for an existing user."""
    valid_credentials = {"username": "test_user", "password": "test_password"}
    assert verify_login(valid_credentials) is True


def test_verify_login_invalid_password(app, setup_user):
    """Test login with invalid password."""
    invalid_password = {"username": "test_user", "password": "wrong_password"}
    assert verify_login(invalid_password) is False


def test_verify_login_nonexistent_user(app):
    """Test login with a nonexistent user."""
    nonexistent_user = {"username": "nonexistent_user", "password": "test_password"}
    assert verify_login(nonexistent_user) is False


def test_verify_login_missing_fields(app):
    """Test login with missing username or password."""
    missing_username = {"password": "test_password"}
    missing_password = {"username": "test_user"}
    assert verify_login(missing_username) is False
    assert verify_login(missing_password) is False


def test_create_user_success(app):
    """Test creating a new user."""
    with app.app_context():
        username = "new_user"
        password = "new_password"
        user = create_user(username, password)
        assert user.username == username
        assert user.password != password  # Password should be hashed
        assert User.query.filter_by(username=username).first() is not None


def test_create_user_existing_user(app, setup_user):
    """Test creating a user that already exists."""
    with app.app_context():
        with pytest.raises(RuntimeError) as excinfo:
            create_user("test_user", "new_password")
        assert "test_user already exists" in str(excinfo.value)
