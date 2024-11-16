import click

from miasi.ext.auth import create_user
from miasi.ext.database import db
from miasi.models import Product, System, Form, Equation, EquationFields, Knowledge


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

    # Sample data for System table
    systems = [
        System(id=1, name="BMI_Calculator", name_human_readable="Kalkulator BMI",
               description="System, który umożliwi Ci sprawdzenie swojego BMI"),
    ]

    # Sample data for Form table
    forms = [
        Form(id=1, id_system=1, name="height", name_human_readable="Wzrost", input_type="number", description="Wzrost w metrach",
             order=1, validation_rule="^[0-9]+(\.[0-9]+)?$"),
        Form(id=2, id_system=1, name="weight", name_human_readable="Waga", input_type="number", description="Waga w kilogramach",
             order=2, validation_rule="^[0-9]+(\.[0-9]+)?$")
    ]

    # Sample data for Equation table
    equations = [
        Equation(id=1, id_system=1, name="BMI", name_human_readable="Body Mass Index", formula="weight / (height ** 2)",
                 description="Obliczanie BMI")
    ]

    # Sample data for EquationFields table
    equation_fields = [
        EquationFields(id=1, id_equation=1, id_form=1, variable_name="height", description="Wzrost w metrach"),
        EquationFields(id=2, id_equation=1, id_form=2, variable_name="weight", description="Waga w kilogramach")
    ]

    # Sample data for Knowledge table
    knowledge = [
        Knowledge(id=1, id_system=1, id_equation=1, condition="value < 18.5",
                  advice="Twoja waga jest zbyt niska. Rozważ konsultację z dietetykiem."),
        Knowledge(id=2, id_system=1, id_equation=1, condition="value >= 18.5 and value < 25",
                  advice="Twoja waga jest w normie. Utrzymuj zdrowy styl życia!"),
        Knowledge(id=3, id_system=1, id_equation=1, condition="value >= 25 and value < 30",
                  advice="Masz nadwagę. Rozważ zwiększenie aktywności fizycznej i konsultację z dietetykiem."),
        Knowledge(id=4, id_system=1, id_equation=1, condition="value >= 30",
                  advice="Masz otyłość. Skonsultuj się z lekarzem i dietetykiem."),
    ]

    # Add all sample data to the session
    db.session.bulk_save_objects(products)
    db.session.bulk_save_objects(systems)
    db.session.bulk_save_objects(forms)
    db.session.bulk_save_objects(equations)
    db.session.bulk_save_objects(equation_fields)
    db.session.bulk_save_objects(knowledge)

    # Commit changes to the database
    db.session.commit()

    return {
        "products": Product.query.all(),
        "systems": System.query.all(),
        "forms": Form.query.all(),
        "equations": Equation.query.all(),
        "equation_fields": EquationFields.query.all(),
        "knowledge": Knowledge.query.all()
    }

def reset_db():
    """Resets database"""
    drop_db()
    create_db()
    populate_db()
    create_user("admin", "1234")


def init_app(app):
    # add multiple commands in a bulk
    for command in [create_db, drop_db, populate_db, reset_db]:
        app.cli.add_command(app.cli.command()(command))

    # add a single command
    @app.cli.command()
    @click.option("--username", "-u")
    @click.option("--password", "-p")
    def add_user(username, password):
        """Adds a new user to the database"""
        return create_user(username, password)

