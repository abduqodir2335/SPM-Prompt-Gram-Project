from flask import Flask

from app.config import get_config
from app.extensions import csrf, db, migrate
from app.logging import configure_request_logging


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    configure_request_logging(app)

    from app.api.health import health_blueprint

    app.register_blueprint(health_blueprint)

    from app.errors import register_error_handlers

    register_error_handlers(app)
    return app
