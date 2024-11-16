import click

from miasi.ext.auth import create_user
from miasi.ext.database import db
from miasi.models import Product, Systems, Forms, Equations, EquationFields


def create_db():
    """Creates database"""
    db.create_all()


def drop_db():
    """Cleans database"""
    db.drop_all()


def populate_db():
    """Populate db with sample data"""
    # Sample data for Product table
    products = [
        Product(id=1, name="Ciabatta", price="10", description="Italian Bread"),
        Product(id=2, name="Baguete", price="15", description="French Bread"),
        Product(id=3, name="Pretzel", price="20", description="German Bread"),
    ]

    # Sample data for Systems table
    systems = [
        Systems(id=1, name="BMI_Calculator", name_human_readable="Kalkulator BMI", description="System, który umożliwi Ci sprawdzenie swojego BMI"),
    ]

    # Sample data for Forms table
    forms = [
        Forms(id=1, id_systems=1, name="height", name_human_readable="Wzrost", input_type="number", description="Wzrost w metrach", order=1, validation_rule="^[0-9]+(\.[0-9]+)?$"),
        Forms(id=2, id_systems=1, name="weight", name_human_readable="Waga", input_type="number", description="Waga w kilogramach", order=2, validation_rule="^[0-9]+(\.[0-9]+)?$")
    ]

    # Sample data for Equations table
    equations = [
        Equations(id=1, id_systems=1, name="BMI", name_human_readable="Body Mass Index", formula="weight / (height ** 2)", description="Obliczanie BMI")
    ]

    # Sample data for EquationFields table
    equation_fields = [
        EquationFields(id=1, id_equations=1, id_forms=1, variable_name="height", description="Wzrost w metrach"),
        EquationFields(id=2, id_equations=1, id_forms=2, variable_name="weight", description="Waga w kilogramach")
    ]

    # Add all sample data to the session
    db.session.bulk_save_objects(products)
    db.session.bulk_save_objects(systems)
    db.session.bulk_save_objects(forms)
    db.session.bulk_save_objects(equations)
    db.session.bulk_save_objects(equation_fields)

    # Commit the session
    db.session.commit()

    return {
        "products": Product.query.all(),
        "systems": Systems.query.all(),
        "forms": Forms.query.all(),
        "equations": Equations.query.all(),
        "equation_fields": EquationFields.query.all()
    }


def init_app(app):
    # add multiple commands in a bulk
    for command in [create_db, drop_db, populate_db]:
        app.cli.add_command(app.cli.command()(command))

    # add a single command
    @app.cli.command()
    @click.option("--username", "-u")
    @click.option("--password", "-p")
    def add_user(username, password):
        """Adds a new user to the database"""
        return create_user(username, password)
