from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_admin.form import Select2Widget
from flask_simplelogin import login_required
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

# Specjalne widoki
class FormAdmin(ModelView):
    """
    Panel administracyjny dla tabeli Form.
    """
    column_list = ("name", "name_human_readable", "description")
    form_columns = ("name", "name_human_readable", "input_type", "description", "select_options")

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
    form_columns = ['condition', 'advice', 'system', 'equation']

    form_extra_fields = {
        'system': QuerySelectField(
            label='System',
            query_factory=lambda: db.session.query(System),
            get_label='name_human_readable',
            allow_blank=False
        ),
        'equation': QuerySelectField(
            label='Equation',
            query_factory=lambda: db.session.query(Equation),
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
            },
            'equation': {
                'query_factory': lambda: Equation.query,
                'get_label': 'name_human_readable'
            }
        }

admin = Admin(index_view=ProtectedAdminIndexView())

def init_app(app):
    admin.name = app.config.TITLE
    admin.template_mode = app.config.FLASK_ADMIN_TEMPLATE_MODE
    admin.init_app(app)

    # Widoki
    admin.add_view(FormAdmin(Form, db.session))
    admin.add_view(SystemAdmin(System, db.session))

    admin.add_view(EquationAdmin(Equation, db.session))
    admin.add_view(KnowledgeAdmin(Knowledge, db.session))
