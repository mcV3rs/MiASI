from flask import Blueprint

from .views import index, system

"""Rejestracja blueprinta dla modułu webui"""
bp = Blueprint("webui", __name__, template_folder="templates")

bp.add_url_rule("/", view_func=index)
bp.add_url_rule("/system/<system_id>", view_func=system, endpoint="systemview")


def init_app(app):
    app.register_blueprint(bp)
