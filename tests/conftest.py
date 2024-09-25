import pytest

from backend import create_app
from backend.config import configs
from backend.core import db as _db


@pytest.fixture(scope='session', autouse=True)
def app():
    config = configs['testing']
    app = create_app(settings_override=config)
    return app


@pytest.fixture(scope='function', autouse=True)
def db(app):
    """
    https://github.com/pytest-dev/pytest-flask/issues/70
    """
    with app.app_context():
        _db.create_all()
        _db.session.commit()

        import warnings
        from sqlalchemy import exc as sa_exc
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=sa_exc.SAWarning)
            yield _db
            _db.session.remove()
            _db.drop_all()


@pytest.fixture(scope='session')
def test_client(app):
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


