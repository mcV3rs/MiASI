import click

from miasi.ext.auth import create_user
from miasi.ext.database import db
from miasi.models import System, Form, Equation, Knowledge, SystemForm


def create_db():
    """Komenda tworząca bazę danych"""
    db.create_all()
    print("Database created")


def drop_db():
    """Komenda usuwająca bazę danych"""
    db.drop_all()
    print("Database dropped")


def populate_db():
    """Komenda wypełniająca bazę danych przykładowymi danymi"""

    systems = [
        System(name="BMI_Calculator", name_human_readable="Kalkulator BMI",
               description="System, który umożliwi Ci sprawdzenie swojego BMI"),
        System(name="BMR_Calculator", name_human_readable="Kalkulator BMR",
               description="Kalkulator, który pozwoli Ci obliczyć zapotrzebowanie kaloryczne (BMR)")
    ]

    forms = [
        Form(name="height", name_human_readable="Wzrost", input_type="number",
             description="Wzrost w metrach"),
        Form(name="weight", name_human_readable="Waga", input_type="number",
             description="Waga w kilogramach"),
        Form(name="age", name_human_readable="Wiek", input_type="number",
             description="Wiek w pełnych latach"),
        Form(name="sex", name_human_readable="Płeć", input_type="sex",
             description="Wybierz swoją płeć")
    ]

    equations = [
        Equation(id_system=1, name="BMI", name_human_readable="Body Mass Index",
                 formula="weight / (height ** 2)"),
        Equation(id_system=2, name="BMR_Male", name_human_readable="Basal Metabolic Rate - Male",
                 formula="66 + (13.7 * weight) + (500 * height) - (5.8 * age)", sex=1),
        Equation(id_system=2, name="BMR_Female", name_human_readable="Basal Metabolic Rate - Female",
                 formula="655 + (9.6 * weight) + (180 * height) - (4.7 * age)", sex=0)
    ]

    knowledge = [
        Knowledge(id_system=1, condition="BMI < 18.5",
                  advice="Twoja waga jest zbyt niska. Rozważ konsultację z dietetykiem."),
        Knowledge(id_system=1, condition="18.5 <= BMI < 25",
                  advice="Twoja waga jest w normie. Utrzymuj zdrowy styl życia!"),
        Knowledge(id_system=1, condition="25 <= BMI < 30",
                  advice="Masz nadwagę. Rozważ zwiększenie aktywności fizycznej i konsultację z dietetykiem."),
        Knowledge(id_system=1, condition="BMI >= 30",
                  advice="Masz otyłość. Skonsultuj się z lekarzem i dietetykiem.")
    ]

    system_forms = [
        SystemForm(id_system=1, id_form=1),
        SystemForm(id_system=1, id_form=2),
        SystemForm(id_system=2, id_form=1),
        SystemForm(id_system=2, id_form=2),
        SystemForm(id_system=2, id_form=3),
        SystemForm(id_system=2, id_form=4),
    ]

    db.session.bulk_save_objects(systems)
    db.session.bulk_save_objects(forms)
    db.session.bulk_save_objects(equations)
    db.session.bulk_save_objects(knowledge)
    db.session.bulk_save_objects(system_forms)

    db.session.commit()

    print("Database populated")

    return {
        "systems": System.query.all(),
        "forms": Form.query.all(),
        "equations": Equation.query.all(),
        "knowledge": Knowledge.query.all(),
        "system_forms": SystemForm.query.all()
    }


def reset_db():
    """Komenda resetująca bazę danych"""
    db.drop_all()
    db.create_all()
    populate_db()
    create_user("admin", "1234")
    print("Database reset and ready to use")


def init_app(app):
    """Inicjalizacja komend dla aplikacji"""
    for command in [create_db, drop_db, populate_db, reset_db]:
        app.cli.add_command(app.cli.command()(command))

    # add a single command
    @app.cli.command()
    @click.option("--username", "-u")
    @click.option("--password", "-p")
    def add_user(username, password):
        """Komenda dodająca użytkownika"""
        return create_user(username, password)
