import os
from datetime import datetime

from flask import current_app, send_file, request, flash, redirect, url_for
from flask_admin import Admin
from flask_admin.base import AdminIndexView, BaseView, expose
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask_simplelogin import login_required
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from miasi.ext.database import db
from miasi.models import System, Form, Equation, Knowledge, SystemForm


# Chronione widoki
class ProtectedAdminIndexView(AdminIndexView):
    @login_required
    def _handle_view(self, name, **kwargs):
        return super()._handle_view(name, **kwargs)


class ProtectedModelView(ModelView):
    @login_required
    def _handle_view(self, name, **kwargs):
        return super()._handle_view(name, **kwargs)


class CustomAdminIndexView(AdminIndexView):
    def is_visible(self):
        # Ukrywa link do strony głównej w navbarze
        return False


class DownloadDatabaseView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        """Przetwarzanie żądania pobrania bazy danych."""

        # Ścieżka do pliku bazy danych
        db_filename = current_app.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        db_path = os.path.join(current_app.instance_path, db_filename)

        # Sprawdź, czy plik istnieje
        if not os.path.exists(db_path):
            return "Database file not found.", 404

        # Generowanie nazwy pliku do pobrania
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        download_name = f"database_{timestamp}.db"

        # Pobierz plik bazy danych
        return send_file(
            db_path,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/octet-stream"
        )


class ImportDatabaseView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    @login_required
    def index(self):
        """Przetwarzanie żądania importu bazy danych."""

        if request.method == 'POST':
            # Sprawdzenie, czy w żądaniu znajduje się plik
            if 'file' not in request.files:
                flash("No file part in the request.", "error")
                return redirect(request.url)

            file = request.files['file']

            # Sprawdzenie, czy wybrano plik
            if file.filename == '':
                flash("No file selected.", "error")
                return redirect(request.url)

            # Sprawdzenie poprawności pliku
            if file and file.filename.endswith('.db'):
                # Pobranie nazwy pliku docelowego z konfiguracji aplikacji
                db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
                if not db_uri.startswith('sqlite:///'):
                    flash("Only SQLite databases are supported for import.", "error")
                    return redirect(request.url)

                # Wyodrębnienie ścieżki i nazwy pliku bazy danych
                db_filename = db_uri.replace('sqlite:///', '')
                db_path = os.path.join(current_app.instance_path, os.path.basename(db_filename))

                # Zapisanie przesłanego pliku jako docelowej bazy danych
                try:
                    file.save(db_path)
                    flash(f"Database imported successfully and renamed to {os.path.basename(db_path)}.", "success")

                    # Przeładowanie aplikacji (dotknięcie pliku)
                    os.utime(db_path, None)
                except Exception as e:
                    flash(f"Error saving database file: {str(e)}", "error")
                    return redirect(request.url)

                return redirect(url_for('admin.index'))

            flash("Invalid file format. Please upload a .db file.", "error")
            return redirect(request.url)

        # Formularz przesyłania pliku
        return self.render('admin/import_database.html')


# Specjalne widoki
class FormAdmin(ModelView):
    """Panel administracyjny dla tabeli Form."""
    column_list = ("name", "name_human_readable", "description")
    form_columns = (
        "name", "name_human_readable", "input_type", "description", "unit", "min_value", "max_value", "select_options",
        "select_values")

    # Mapowanie nazw kolumn
    column_labels = {
        'name': 'Code Name',
        'name_human_readable': 'Name (Human Readable)',
        'description': 'Description',
    }

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        self.extra_js = ["/static/js/admin_dynamic_fields.js"]  # Dodanie własnego JS
        self.extra_css = ["/static/css/admin.css"]  # Dodanie własnego CSS

    form_extra_fields = {
        "input_type": SelectField(
            "Input Type",
            choices=[
                ("number", "Number"),
                ("sex", "Sex"),
                ("select", "Select")
            ],
            render_kw={"id": "input_type"}  # ID dla JavaScript
        ),
        "select_options": TextAreaField(
            "Select Options",
            description="Enter options separated by commas (e.g., Option1, Option2, Option3)",
            render_kw={
                "id": "select_options",  # ID dla JavaScript
                "placeholder": "Add options for the select field"
            }
        ),
        "select_values": TextAreaField(
            "Select Values",
            description="Enter values separated by commas (e.g., 1, 2, 3)",
            render_kw={
                "id": "select_values",  # ID dla JavaScript
                "placeholder": "Add values for the select field"
            }
        )
    }

    form_args = {
        'min_value': {
            'label': 'Minimum Value',  # Ustawienie etykiety
            'description': 'If empty, minimum value will be set to 0'  # Ustawienie opisu
        },
        'max_value': {
            'label': 'Maximum Value',  # Ustawienie etykiety
            'description': 'If empty, no maximum value will be set'  # Ustawienie opisu
        }
    }

    def on_model_change(self, form, model, is_created):
        """
        Handle the saving of the select_options if input_type is 'select'.
        """
        if form.input_type.data == "select":
            model.select_options = form.select_options.data  # Save options
        else:
            model.select_options = None  # Clear options for non-select types
        super().on_model_change(form, model, is_created)


class SystemAdmin(ModelView):
    """Panel administracyjny dla tabeli System."""
    column_list = ("name", "name_human_readable", "description")
    form_columns = ("name", "name_human_readable", "description", "forms", "system_type")
    form_changed = False

    # Mapowanie nazw kolumn
    column_labels = {
        'name': 'Code Name',
        'name_human_readable': 'Name (Human Readable)',
        'description': 'Description',
    }

    # Konfiguracja pól formularza
    form_args = {
        'system_type': {
            'label': 'Multi-advice system',  # Ustawienie etykiety
            'description': 'Check, if the system is a multi-advice system'  # Ustawienie opisu
        }
    }

    form_extra_fields = {
        "forms": QuerySelectMultipleField(
            "Assigned Forms",
            query_factory=lambda: db.session.query(Form).all(),
            get_label="name_human_readable",
            widget=Select2Widget(multiple=True),
            allow_blank=True
        )
    }

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        self.form_widget_args = {
            'forms': {
                'query_factory': lambda: db.session.query(Form).all(),
                'get_label': 'name_human_readable',
                'widget': Select2Widget(multiple=True),
            }
        }

    def on_model_change(self, form, model, is_created):
        if 'forms' in form.data:
            model.system_forms = []
            db.session.flush()

            for form_obj in form.forms.data:
                system_form = SystemForm(system=model, form=form_obj)
                model.system_forms.append(system_form)

        super().on_model_change(form, model, is_created)

    def on_form_prefill(self, form, id):
        system = System.query.get(id)
        if system:
            form.forms.data = [system_form.form for system_form in system.system_forms]


class EquationAdmin(sqla.ModelView):
    """Panel administracyjny dla tabeli Equation."""
    column_list = ("name_human_readable", 'formula', "sex")
    form_columns = ['name', 'name_human_readable', 'formula', 'system', 'sex', 'is_internal']

    column_formatters = {
        'sex': lambda v, c, m, p: '-' if m.sex == 'None' else ('Female' if m.sex == 0 else 'Male')
    }

    form_extra_fields = {
        'system': QuerySelectField(
            label='System Name',
            query_factory=lambda: db.session.query(System),
            get_label='name_human_readable',
            allow_blank=False
        ),
        'sex': SelectField(
            label='Sex',
            choices=[
                (None, 'Both'),
                (1, 'Male'),
                (0, 'Female')
            ]
        ),
    }

    # Konfiguracja pól formularza
    form_args = {
        'is_internal': {
            'label': 'Internal Equation',  # Ustawienie etykiety
            'description': 'Check, if equation is internal, it won\'t be displayed in user side'  # Ustawienie opisu
        }
    }

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        self.form_args = {
            'system': {
                'query_factory': lambda: System.query,
                'get_label': 'name_human_readable'
            }
        }


class KnowledgeAdmin(sqla.ModelView):
    """Panel administracyjny dla tabeli Knowledge."""

    column_list = ['condition', 'advice', 'system.name_human_readable']
    column_labels = {
        'system.name_human_readable': 'System Name'
    }

    column_sortable_list = ['condition', 'advice', ('system.name_human_readable', 'system.name_human_readable')]

    form_columns = ['condition', 'advice', 'system']

    form_extra_fields = {
        'system': QuerySelectField(
            label='System',
            query_factory=lambda: db.session.query(System),
            get_label='name_human_readable',
            allow_blank=False
        )
    }

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        self.form_args = {
            'system': {
                'query_factory': lambda: System.query,
                'get_label': 'name_human_readable'
            }
        }


# Deklaracja instancji Admin
admin = Admin(index_view=ProtectedAdminIndexView())


def init_app(app):
    # Stworzenie niestandardowej instancji AdminIndexView
    admin_index_view = CustomAdminIndexView(name=None)

    admin = Admin(
        app,
        name=app.config.TITLE,
        index_view=admin_index_view,
        template_mode=app.config.FLASK_ADMIN_TEMPLATE_MODE
    )

    # Dodajemy widoki do edycji bazy danych
    admin.add_view(FormAdmin(Form, db.session, name="Form Inputs"))
    admin.add_view(SystemAdmin(System, db.session, name="Systems"))
    admin.add_view(EquationAdmin(Equation, db.session, name="Equations"))
    admin.add_view(KnowledgeAdmin(Knowledge, db.session, name="Knowledge Base"))

    # Dodajemy dodatkowe widoki
    admin.add_view(DownloadDatabaseView(name="Export", endpoint="download-database"))
    admin.add_view(ImportDatabaseView(name="Import", endpoint="import-database"))
