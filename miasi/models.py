from sqlalchemy_serializer import SerializerMixin

from miasi.ext.database import db


class Product(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    price = db.Column(db.Numeric())
    description = db.Column(db.Text)


class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(140))
    password = db.Column(db.String(512))

class Systems(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True) # KLUCZ GŁÓWNY

    name = db.Column(db.String(140)) # Nazwa systemu, używana w kodzie
    name_human_readable = db.Column(db.String(512)) # Nazwa systemu, używana w interfejsie użytkownika
    description = db.Column(db.Text) # Opis systemu

    forms = db.relationship('Forms', backref='system', lazy=True) # Relacja jeden do wielu z tabelą Forms

class Forms(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True) # KLUCZ GŁÓWNY
    id_systems = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False) # KLUCZ OBCY DO SYSTEMU

    name = db.Column(db.String(140)) # Nazwa formularza, używana w kodzie
    name_human_readable = db.Column(db.String(512)) # Nazwa formularza, używana w interfejsie użytkownika
    input_type = db.Column(db.String(50))  # Typ pola formularza
    description = db.Column(db.Text) # Opis formularza
    order = db.Column(db.Integer, nullable=True)  # Kolejność wyświetlania pola
    validation_rule = db.Column(db.String(512), nullable=True)  # Reguła walidacji np. regex

class Equations(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_systems = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU

    name = db.Column(db.String(140))  # Nazwa równania, używana w kodzie
    name_human_readable = db.Column(db.String(512))  # Nazwa równania, używana w interfejsie użytkownika
    formula = db.Column(db.Text)  # Wyrażenie matematyczne jako string (np. "weight / (height ** 2)")
    description = db.Column(db.Text)  # Opis równania

    system = db.relationship('Systems', backref='equations')  # Powiązanie z tabelą Systems


class EquationFields(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_equations = db.Column(db.Integer, db.ForeignKey('equations.id'), nullable=False)  # KLUCZ OBCY DO RÓWNANIA
    id_forms = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)  # KLUCZ OBCY DO POLA FORMULARZA

    variable_name = db.Column(db.String(50))  # Nazwa zmiennej w równaniu (np. "weight", "height")
    description = db.Column(db.String(512))  # Opcjonalny opis pola (np. "waga w kilogramach")

    equation = db.relationship('Equations', backref='fields')  # Relacja z równaniem
    form_field = db.relationship('Forms', backref='equation_mappings')  # Relacja z polem formularza

class Knowledge(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_systems = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU
    id_equations = db.Column(db.Integer, db.ForeignKey('equations.id'), nullable=False)  # KLUCZ OBCY DO RÓWNANIA

    condition = db.Column(db.String(512))  # Wyrażenie logiczne jako string (np. "value < 18.5")
    advice = db.Column(db.Text)  # Rada, którą system udzieli, jeśli warunek jest spełniony

    system = db.relationship('Systems', backref='knowledge')  # Relacja z tabelą Systems
    equation = db.relationship('Equations', backref='knowledge_rules')  # Relacja z tabelą Equations


