import os
from urllib.parse import urlparse

import pytest

from app import create_app
from app.extensions import db


def _assert_test_database() -> None:
    if os.getenv("APP_ENV") != "test":
        raise RuntimeError("Tests require APP_ENV=test")
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("Tests require DATABASE_URL ending in _test")
    database_name = urlparse(database_url).path.lstrip("/")
    if not database_name.endswith("_test"):
        raise RuntimeError("Refusing to run tests against a database not named *_test")


_assert_test_database()


@pytest.fixture
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "UPLOAD_DIR": tmp_path,
        }
    )
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
