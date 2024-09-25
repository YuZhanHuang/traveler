from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)


def on_api_error(e):
    return jsonify(e.to_dict()), e.status_code


@errors.app_errorhandler(Exception)
def on_base_api_error(e):

    print(f'e {e}', flush=True)

    return jsonify({'code': 50000, 'message': f'Internal Service Error'}), 500
