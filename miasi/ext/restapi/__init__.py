from flask import Blueprint
from flask_restful import Api

from .resources import FormsSubmissionResource

bp = Blueprint("restapi", __name__, url_prefix="/api/v1")
api = Api(bp)


def init_app(app):
    api.add_resource(FormsSubmissionResource, "/system/<system_id>/form/submit")

    app.register_blueprint(bp)
