from sqlalchemy_serializer import SerializerMixin

from miasi.ext.database import db


class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(140))
    password = db.Column(db.String(512))

class System(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True) # KLUCZ GŁÓWNY

    name = db.Column(db.String(140)) # Nazwa systemu, używana w kodzie
    name_human_readable = db.Column(db.String(512)) # Nazwa systemu, używana w interfejsie użytkownika
    description = db.Column(db.Text) # Opis systemu

    forms = db.relationship('Form', back_populates='system', lazy=True) # Relacja jeden do wielu z tabelą Form

class Form(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True) # KLUCZ GŁÓWNY
    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False) # KLUCZ OBCY DO SYSTEMU

    name = db.Column(db.String(140)) # Nazwa formularza, używana w kodzie
    name_human_readable = db.Column(db.String(512)) # Nazwa formularza, używana w interfejsie użytkownika
    input_type = db.Column(db.String(50))  # Typ pola formularza
    description = db.Column(db.Text) # Opis formularza
    order = db.Column(db.Integer, nullable=True)  # Kolejność wyświetlania pola
    validation_rule = db.Column(db.String(512), nullable=True)  # Reguła walidacji np. regex

    system = db.relationship('System', back_populates='forms') # Relacja z tabelą System (jeden do wielu)


class Equation(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU

    name = db.Column(db.String(140))  # Nazwa równania, używana w kodzie
    name_human_readable = db.Column(db.String(512))  # Nazwa równania, używana w interfejsie użytkownika
    formula = db.Column(db.Text)  # Wyrażenie matematyczne jako string (np. "weight / (height ** 2)")

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