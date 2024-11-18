from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash

from miasi.ext.database import db


class User(db.Model, SerializerMixin):
    """
    Model bazy danych reprezentujący użytkownika
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True) # KLUCZ GŁÓWNY

    username = db.Column(db.String(140)) # Nazwa użytkownika
    password_hash = db.Column(db.String(512)) # Hasło użytkownika w postaci zahaszowanej

    def __init__(self, username: str, password_plain: str):
        """
        Konstruktor klasy User
        :param username: Nazwa użytkownika
        :param password_plain: Hasło użytkownika w postaci zwykłego tekstu
        """
        self.username = username
        self.password = self._hash_password(password_plain)

    @staticmethod
    def _hash_password(password: str):
        """
        Metoda haszująca hasło użytkownika
        :param password: Hasło w postaci zwykłego tekstu
        """
        return generate_password_hash(password)

class System(db.Model, SerializerMixin):
    """
    Model bazy danych reprezentujący system (np. BMI, WHR)
    """
    __tablename__ = 'system'

    id = db.Column(db.Integer, primary_key=True)  # GŁÓWNY KLUCZ

    name = db.Column(db.String(140))  # Nazwa systemu używana w kodzie
    name_human_readable = db.Column(db.String(512))  # Nazwa systemu używana w interfejsie użytkownika
    description = db.Column(db.Text)  # Opis systemu

    system_forms = db.relationship('SystemForm', back_populates='system', cascade='all, delete-orphan')  # Relacja wiele-do-wielu

    def __init__(self, name: str, name_human_readable: str, description: str):
        """
        Konstruktor klasy System
        :param name: Nazwa systemu używana w kodzie
        :param name_human_readable: Nazwa systemu używana w interfejsie użytkownika
        :param description: Opis systemu
        """
        self.name = name
        self.name_human_readable = name_human_readable
        self.description = description

class Form(db.Model, SerializerMixin):
    """
    Model bazy danych reprezentujący pole formularza (np. Wzrost, Waga)
    """
    __tablename__ = 'form'

    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY

    name = db.Column(db.String(140))  # Nazwa pola formularza używana w kodzie
    name_human_readable = db.Column(db.String(512))  # Nazwa pola formularza używana w interfejsie użytkownika
    input_type = db.Column(db.String(50))  # Typ pola formularza (np. "number", "text", "select")
    description = db.Column(db.Text)  # Opis pola formularza
    select_options = db.Column(db.Text, nullable=True)  # Opcje wyboru dla pól typu "select"

    system_forms = db.relationship('SystemForm', back_populates='form', cascade='all, delete-orphan')  # Relacja wiele-do-wielu

    def __init__(self, name: str, name_human_readable: str, input_type: str, description: str, select_options: str = None):
        """
        Konstruktor klasy Form
        :param name: Nazwa pola formularza używana w kodzie
        :param name_human_readable: Nazwa pola formularza używana w interfejsie użytkownika
        :param input_type: Typ pola formularza (np. "number", "text", "select")
        :param description: Opis pola formularza
        :param select_options: Opcje wyboru dla pól typu "select"
        """
        self.name = name
        self.name_human_readable = name_human_readable
        self.input_type = input_type
        self.description = description
        self.select_options = select_options

class SystemForm(db.Model, SerializerMixin):
    """
    Model bazy danych reprezentujący relację wiele-do-wielu między systemem a formularzem
    """
    __tablename__ = 'system_form'

    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), primary_key=True, nullable=True)  # KLUCZ OBCY DO SYSTEMU
    id_form = db.Column(db.Integer, db.ForeignKey('form.id'), primary_key=True, nullable=True)  # KLUCZ OBCY DO FORMULARZA

    system = db.relationship('System', back_populates='system_forms')  # Relacja do System
    form = db.relationship('Form', back_populates='system_forms')  # Relacja do Form

    def __init__(self, id_system=None, id_form=None, system=None, form=None):
        """
        Konstruktor klasy SystemForm
        :param id_system: ID systemu
        :param id_form: ID formularza
        :param system: Obiekt systemu
        :param form: Obiekt formularza
        """

        if system and form:
            self.id_system = system.id
            self.id_form = form.id
        elif id_system and id_form:
            self.id_system = id_system
            self.id_form = id_form
        else:
            raise ValueError("Either system and form objects or id_system and id_form must be provided")

class Equation(db.Model, SerializerMixin):
    """
    Model bazy danych reprezentujący równanie (np. BMI, BMR)
    """
    __tablename__ = 'equation'

    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU

    name = db.Column(db.String(140))  # Nazwa równania, używana w kodzie
    name_human_readable = db.Column(db.String(512))  # Nazwa równania, używana w interfejsie użytkownika
    formula = db.Column(db.Text)  # Wyrażenie matematyczne jako string (np. "weight / (height ** 2)")
    sex = db.Column(db.Integer, nullable=True)  # None - both, 1 - Male, 0 - Female

    system = db.relationship('System', backref='equations')  # Powiązanie z tabelą System

    def __init__(self, id_system: int, name: str, name_human_readable: str, formula: str, sex: int = None):
        """
        Konstruktor klasy Equation
        :param id_system: ID systemu
        :param name: Nazwa równania, używana w kodzie
        :param name_human_readable: Nazwa równania, używana w interfejsie użytkownika
        :param formula: Wyrażenie matematyczne jako string (np. "weight / (height ** 2)")
        :param sex: Płeć, dla której równanie jest obliczane (None - oba, 1 - mężczyzna, 0 - kobieta)
        """

        self.id_system = id_system
        self.name = name
        self.name_human_readable = name_human_readable
        self.formula = formula
        self.sex = sex

class Knowledge(db.Model, SerializerMixin):
    """
    Model bazy danych reprezentujący wiedzę systemu (np. "BMI < 18.5 -> Twoja waga jest zbyt niska")
    """
    __tablename__ = 'knowledge'

    id = db.Column(db.Integer, primary_key=True)  # KLUCZ GŁÓWNY
    id_system = db.Column(db.Integer, db.ForeignKey('system.id'), nullable=False)  # KLUCZ OBCY DO SYSTEMU

    condition = db.Column(db.String(512))  # Wyrażenie logiczne jako string (np. "value < 18.5")
    advice = db.Column(db.Text)  # Rada, którą system udzieli, jeśli warunek jest spełniony

    system = db.relationship('System', backref='knowledge')  # Relacja z tabelą System

    def __init__(self, id_system: int, condition: str, advice: str):
        """
        Konstruktor klasy Knowledge
        :param id_system: ID systemu
        :param condition: Wyrażenie logiczne jako string (np. "value < 18.5")
        :param advice: Rada, którą system udzieli, jeśli warunek jest spełniony
        """

        self.id_system = id_system
        self.condition = condition
        self.advice = advice
