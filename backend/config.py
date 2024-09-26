import logging
import os


class Config:
    # Basic settings
    TESTING = False
    PROJECT_ID = os.environ.get('PROJECT_ID')
    LOG_LEVEL = logging.INFO
    SECRET_KEY = os.environ.get('SECRET_KEY', '5566neverdie')
    CORS_HEADERS = "Content-Type"

    # database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = "postgresql://{username}:{password}@{host}/{database_name}".format(
        username=os.environ.get('DB_USER', 'unicorn_user'),
        password=os.environ.get('DB_PASS', 'magical_password'),
        host=os.environ.get('DB_HOST', 'postgres'),
        database_name=os.environ.get('DB_NAME', 'postgres'),
    )


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False


class TestingConfig(Config):
    FLASK_ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'my secret'
    ACCOUNT_MANAGER_ENABLED = False


configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
