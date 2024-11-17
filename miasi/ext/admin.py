from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_admin.form import Select2Widget
from flask_simplelogin import login_required
from wtforms.fields.choices import SelectField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from miasi.ext.database import db
from miasi.models import System, Form, Equation, EquationFields, Knowledge, SystemForm


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
    """Admin panel for the Form table."""
    column_list = ("name", "name_human_readable", "description")
    form_columns = ("name", "name_human_readable", "input_type", "description", "order", "validation_rule")

    form_extra_fields = {
        "input_type": SelectField(
            "Input Type",
            choices=[("text", "Text"), ("number", "Number"), ("sex", "Sex")]
        )
    }


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

    # def edit_form(self, obj=None):
    #     """Customize the edit form."""
    #     form = super().edit_form(obj)
    #     if obj and not self.form_changed:
    #         # Pobierz przypisane formularze do systemu
    #         form.forms.data = [system_form.form for system_form in obj.system_forms]
    #         print(f"Form Data in Edit: {form.forms.data}")  # Debugging line
    #         self.form_changed = True
    #     return form

    # Funkcja aktywowana przy przesłaniu formularza
    def on_form_prefill(self, form, id):
        """Pre-fill the form with the data from the database."""
        # Pobierz obiekt systemu
        system = System.query.get(id)
        if system:
            # Pobierz przypisane formularze do systemu
            form.forms.data = [system_form.form for system_form in system.system_forms]
        print(f"Form Data in Prefill: {form.forms.data}")


class EquationAdmin(sqla.ModelView):
    form_columns = ['name', 'name_human_readable', 'formula', 'system']

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

class EquationFieldsAdmin(sqla.ModelView):
    form_columns = ['variable_name', 'equation', 'form_field']

    form_extra_fields = {
        'equation': QuerySelectField(
            label='Equation',
            query_factory=lambda: db.session.query(Equation),
            get_label='name_human_readable',
            allow_blank=False
        ),
        'form_field': QuerySelectField(
            label='Form Field',
            query_factory=lambda: db.session.query(Form),
            get_label='name_human_readable',
            allow_blank=False
        )
    }

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        self.form_args = {
            'equation': {
                'query_factory': lambda: Equation.query,
                'get_label': 'name_human_readable'
            },
            'form_field': {
                'query_factory': lambda: Form.query,
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
    # admin.add_view(ProtectedModelView(System, db.session))
    admin.add_view(FormAdmin(Form, db.session))
    admin.add_view(SystemAdmin(System, db.session))

    admin.add_view(EquationAdmin(Equation, db.session))
    admin.add_view(EquationFieldsAdmin(EquationFields, db.session))
    admin.add_view(KnowledgeAdmin(Knowledge, db.session))
