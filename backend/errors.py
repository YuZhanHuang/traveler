from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)


def on_api_error(e):
    return jsonify(e.to_dict()), e.status_code


@errors.app_errorhandler(Exception)
def on_base_api_error(e):
    return jsonify({'code': 50000, 'message': 'Internal Service Error'}), 500
