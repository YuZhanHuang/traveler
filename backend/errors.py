from flask import Blueprint, jsonify

from backend.logger import get_logger

errors = Blueprint('errors', __name__)
logger = get_logger(__name__)


def on_api_error(e):
    logger.error('on_api_error', msg=str(e), exc_info=True)
    return jsonify(e.to_dict()), e.status_code


@errors.app_errorhandler(Exception)
def on_base_api_error(e):
    logger.error('on_base_api_error', msg=str(e), exc_info=True)
    return jsonify({'code': 50000, 'message': 'Internal Service Error'}), 500