import os

from flask import Flask

from backend.config import configs
from backend.core import db, migrate
from backend.helper import register_blueprints, JSONEncoder

root_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(root_dir, 'admin_dealer', 'templates')


def create_app(package_name, package_path=None, settings_override=None):
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    # instantiate the app
    app = Flask(package_name, template_folder=template_dir)

    # set config
    app.config.from_object(configs[config_name])
    app.json_encoder = JSONEncoder

    if settings_override:
        app.config.from_object(settings_override)

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprint
    if package_path:
        register_blueprints(app, package_name, package_path)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app


