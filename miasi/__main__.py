import click
from flask.cli import FlaskGroup

from . import create_app_wsgi


@click.group(cls=FlaskGroup, create_app=create_app_wsgi) # pragma: no cover
def main():
    """Zarządzanie aplikacją."""


if __name__ == "__main__":  # pragma: no cover
    main()
