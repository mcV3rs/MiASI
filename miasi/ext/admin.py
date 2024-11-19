import os

from flask import current_app, send_file, request, flash, redirect, url_for
from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView, BaseView, expose
from flask_admin.form import Select2Widget
from flask_simplelogin import login_required
from werkzeug.utils import secure_filename
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField
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

class DownloadDatabaseView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        """Send the database file for download."""
        # Ścieżka do pliku bazy danych
        db_filename = current_app.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        db_path = os.path.join(current_app.instance_path, db_filename)

        print(f"Database Path: {db_path}")

        # Sprawdź, czy plik istnieje
        if not os.path.exists(db_path):
            return "Database file not found.", 404

        # Pobierz plik bazy danych
        return send_file(
            db_path,
            as_attachment=True,
            download_name="database.db",
            mimetype="application/octet-stream"
        )

class ImportDatabaseView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    @login_required
    def index(self):
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
                filename = secure_filename(file.filename)
                db_path = os.path.join(current_app.instance_path, filename)

                # Zapisanie pliku do folderu instance
                file.save(db_path)
                flash("Database imported successfully.", "success")

                # Przeładowanie aplikacji
                os.utime(db_path, None)  # Dotknięcie pliku, aby Flask zauważył zmianę
                return redirect(url_for('admin.index'))

            flash("Invalid file format. Please upload a .db file.", "error")
            return redirect(request.url)

        # Formularz przesyłania pliku
        return self.render('admin/import_database.html')

# Specjalne widoki
class FormAdmin(ModelView):
    """
    Panel administracyjny dla tabeli Form.
    """
    column_list = ("name", "name_human_readable", "description")
    form_columns = ("name", "name_human_readable", "input_type", "description", "select_options", "select_values")

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        self.extra_js = ["/static/js/admin_dynamic_fields.js"]  # Dodanie własnego JS

    form_extra_fields = {
        "input_type": SelectField(
            "Input Type",
            choices=[
                ("text", "Text"),
                ("number", "Number"),
                ("sex", "Sex"),
                ("select", "Select")  # Nowy typ pola
            ],
            render_kw={"id": "input_type"}  # ID dla JavaScript
        ),
        "select_options": StringField(
            "Select Options",
            description="Enter options separated by commas (e.g., Option1, Option2, Option3)",
            render_kw={
                "id": "select_options",  # ID dla JavaScript
                "disabled": True,  # Domyślnie wyłączone
                "placeholder": "Add options for the select field"
            }
        ),
        "select_values": StringField(
            "Select Values",
            description="Enter values separated by commas (e.g., 1, 2, 3)",
            render_kw={
                "id": "select_values",  # ID dla JavaScript
                "disabled": True,  # Domyślnie wyłączone
                "placeholder": "Add values for the select field"
            }
        )
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
    """Admin panel for the System table."""
    column_list = ("name", "name_human_readable", "description")
    form_columns = ("name", "name_human_readable", "description", "forms")
    form_changed = False

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
        """Update the system-form relationship."""
        print("Form Data:", form.forms.data)  # Debugging line

        if 'forms' in form.data:
            # Wyczyszczenie istniejących powiązań
            model.system_forms = []
            db.session.flush()  # Upewnij się, że zmiany są zapisane w bazie

            # Dodanie nowych formularzy
            for form_obj in form.forms.data:
                print(f"Form Object: {form_obj}")  # Debugging line to check the form object
                system_form = SystemForm(system=model, form=form_obj)
                model.system_forms.append(system_form)

        super().on_model_change(form, model, is_created)

    def on_form_prefill(self, form, id):
        """Pre-fill the form with the data from the database."""
        # Pobierz obiekt systemu
        system = System.query.get(id)
        if system:
            # Pobierz przypisane formularze do systemu
            form.forms.data = [system_form.form for system_form in system.system_forms]
        print(f"Form Data in Prefill: {form.forms.data}")


class EquationAdmin(sqla.ModelView):
    column_list = ("name_human_readable", 'formula', "sex")
    form_columns = ['name', 'name_human_readable', 'formula', 'system', 'sex']

    form_extra_fields = {
        'system': QuerySelectField(
            label='System',
            query_factory=lambda: db.session.query(System),
            get_label='name_human_readable',
            allow_blank=False
        ),
        'sex': SelectField(
            label='Sex',
            choices=[
                (None, 'Nie zależy od płci'),
                (1, 'Mężczyźni'),
                (0, 'Kobiety')
            ]
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


class KnowledgeAdmin(sqla.ModelView):
    # Kolumny wyświetlane w panelu
    column_list = ['condition', 'advice', 'system.name_human_readable']

    # Mapowanie nazw kolumn na bardziej przyjazne
    column_labels = {
        'condition': 'Warunek',
        'advice': 'Porada',
        'system.name_human_readable': 'Nazwa systemu'
    }

    # Kolumny, po których można sortować
    column_sortable_list = ['condition', 'advice', ('system.name_human_readable', 'system.name_human_readable')]

    # Kolumny dostępne w formularzu
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


admin = Admin(index_view=ProtectedAdminIndexView())

def init_app(app):
    admin.name = app.config.TITLE
    admin.template_mode = app.config.FLASK_ADMIN_TEMPLATE_MODE
    admin.init_app(app)

    # Widoki do edycji bazy danych
    admin.add_view(FormAdmin(Form, db.session, name="Pola Formularza"))
    admin.add_view(SystemAdmin(System, db.session, name="Systemy"))
    admin.add_view(EquationAdmin(Equation, db.session, name="Równania"))
    admin.add_view(KnowledgeAdmin(Knowledge, db.session, name="Baza wiedzy"))

    # Dodatkowe widoki
    admin.add_view(DownloadDatabaseView(name="Eksport", endpoint="download-database"))
    admin.add_view(ImportDatabaseView(name="Import", endpoint="import-database"))
