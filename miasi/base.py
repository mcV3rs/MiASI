from dynaconf import FlaskDynaconf
from flask import Flask


def create_app(**config):
    app = Flask(__name__, static_url_path='/static')
    FlaskDynaconf(app, **config)  # Konfiguracja z pliku settings.toml
    app.config.load_extensions(
        "EXTENSIONS"
    )
    app.config.update(config)
    return app


def create_app_wsgi():  # pragma: no cover
    app = create_app()
    return app
