from flask import Blueprint

from .views import index, only_admin, secret, system

bp = Blueprint("webui", __name__, template_folder="templates")

bp.add_url_rule("/", view_func=index)
bp.add_url_rule("/secret", view_func=secret, endpoint="secret")
bp.add_url_rule("/only_admin", view_func=only_admin, endpoint="onlyadmin")
bp.add_url_rule("/system/<system_id>", view_func=system, endpoint="systemview")


def init_app(app):
    app.register_blueprint(bp)
