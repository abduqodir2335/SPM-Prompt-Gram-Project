from alembic import context
from flask import current_app

config = context.config


def run_migrations_offline() -> None:
    url = current_app.config["SQLALCHEMY_DATABASE_URI"]
    context.configure(url=url, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with current_app.app_context():
        connectable = current_app.extensions["sqlalchemy"].engine
        with connectable.connect() as connection:
            context.configure(connection=connection, compare_type=True)
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
