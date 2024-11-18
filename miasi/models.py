from sqlalchemy_serializer import SerializerMixin

from miasi.ext.database import db


class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(140))
    password = db.Column(db.String(512))

class System(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key

    name = db.Column(db.String(140))  # System name used in code
    name_human_readable = db.Column(db.String(512))  # System name used in the user interface
    description = db.Column(db.Text)  # System description

    system_forms = db.relationship('SystemForm', back_populates='system', cascade='all, delete-orphan')  # Many-to-many relationship

class Form(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key

    name = db.Column(db.String(140))  # Form name used in code
    name_human_readable = db.Column(db.String(512))  # Form name used in the user interface
    input_type = db.Column(db.String(50))  # Form field type
    description = db.Column(db.Text)  # Form description
    order = db.Column(db.Integer, nullable=True)  # Display order of the field TODO - prawdopodobnie niepotrzebne
    validation_rule = db.Column(db.String(512), nullable=True)  # Validation rule, e.g., regex
    select_options = db.Column(db.Text, nullable=True)  # Options for select fields

    system_forms = db.relationship('SystemForm', back_populates='form', cascade='all, delete-orphan')  # Many-to-many relationship

class SystemForm(db.Model, SerializerMixin):
    __tablename__ = 'system_form'

    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), primary_key=True)  # Foreign Key to System
    id_form = db.Column(db.Integer, db.ForeignKey('form.id'), primary_key=True)  # Foreign Key to Form

    system = db.relationship('System', back_populates='system_forms')  # Relationship to System
    form = db.relationship('Form', back_populates='system_forms')  # Relationship to Form

    def __init__(self, id_system=None, id_form=None, system=None, form=None):
        if system and form:
            self.id_system = system.id
            self.id_form = form.id
        elif id_system and id_form:
            self.id_system = id_system
            self.id_form = id_form
        else:
            raise ValueError("Either system and form objects or id_system and id_form must be provided")

class Equation(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU

    name = db.Column(db.String(140))  # Nazwa równania, używana w kodzie
    name_human_readable = db.Column(db.String(512))  # Nazwa równania, używana w interfejsie użytkownika
    formula = db.Column(db.Text)  # Wyrażenie matematyczne jako string (np. "weight / (height ** 2)")
    sex = db.Column(db.Integer, nullable=True)  # None - both, 1 - Male, 0 - Female

    system = db.relationship('System', backref='equations')  # Powiązanie z tabelą System


class EquationFields(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_equation = db.Column(db.Integer, db.ForeignKey('equation.id'), nullable=False)  # KLUCZ OBCY DO RÓWNANIA
    id_form = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)  # KLUCZ OBCY DO POLA FORMULARZA

    variable_name = db.Column(db.String(50))  # Nazwa zmiennej w równaniu (np. "weight", "height")

    equation = db.relationship('Equation', backref='fields')  # Relacja z równaniem
    form_field = db.relationship('Form', backref='equation_mappings')  # Relacja z polem formularza

class Knowledge(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU

    condition = db.Column(db.String(512))  # Wyrażenie logiczne jako string (np. "value < 18.5")
    advice = db.Column(db.Text)  # Rada, którą system udzieli, jeśli warunek jest spełniony

    system = db.relationship('System', backref='knowledge')  # Relacja z tabelą System