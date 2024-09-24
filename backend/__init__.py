from flask import request_started

from backend import factory
from backend.errors import on_api_error
from backend.exceptions import APIError


def create_app(settings_override=None):
    app = factory.create_app(__name__, __file__, settings_override)
    app.errorhandler(APIError)(on_api_error)
    app.register_blueprint(errors)
    request_started.connect(on_request_started, app)
    return app


def on_request_started(sender, **extra):
    """
    記錄任何請求的基本資料
    """
    ...
