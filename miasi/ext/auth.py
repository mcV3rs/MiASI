from flask_simplelogin import SimpleLogin
from werkzeug.security import check_password_hash, generate_password_hash

from miasi.ext.database import db
from miasi.models import User


def verify_login(user):
    """Sprawdzenie, czy użytkownik istnieje i czy hasło jest poprawne"""
    username = user.get("username")
    password = user.get("password")

    if not username or not password:
        return False

    existing_user = User.query.filter_by(username=username).first()

    if not existing_user:
        return False

    if check_password_hash(existing_user.password, password):
        return True

    return False


def create_user(username, password):
    """Tworzenie nowego użytkownika"""
    if User.query.filter_by(username=username).first():
        raise RuntimeError(f"{username} already exists")

    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return user


def init_app(app):
    SimpleLogin(app, login_checker=verify_login)
