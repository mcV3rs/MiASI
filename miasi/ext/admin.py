from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import AdminIndexView
from flask_simplelogin import login_required
from werkzeug.security import generate_password_hash
from wtforms_sqlalchemy.fields import QuerySelectField

from miasi.ext.database import db
from miasi.models import Product, User, System, Form, Equation, EquationFields


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
class FormAdmin(sqla.ModelView):
    form_columns = ['name', 'name_human_readable', 'input_type', 'description', 'system']

    form_extra_fields = {
        'system': QuerySelectField(
            label='System',
            query_factory=lambda: System.query,
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

class EquationAdmin(sqla.ModelView):
    form_columns = ['name', 'name_human_readable', 'formula', 'description', 'system']

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
    form_columns = ['variable_name', 'description', 'equation', 'form_field']

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

admin = Admin(index_view=ProtectedAdminIndexView())

def init_app(app):
    admin.name = app.config.TITLE
    admin.template_mode = app.config.FLASK_ADMIN_TEMPLATE_MODE
    admin.init_app(app)

    # Widoki
    admin.add_view(ProtectedModelView(Product, db.session))
    admin.add_view(ProtectedModelView(System, db.session))
    admin.add_view(FormAdmin(Form, db.session))
    admin.add_view(EquationAdmin(Equation, db.session))
    admin.add_view(EquationFieldsAdmin(EquationFields, db.session))
    admin.add_view(ProtectedModelView(User, db.session))

