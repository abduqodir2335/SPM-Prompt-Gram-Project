# Backend conventions

- Flask app factory lives in `app/__init__.py`.
- API blueprints handle HTTP only.
- Services contain business rules; models contain SQLAlchemy data structures.
- Pydantic models validate request and response bodies.
- Use environment configuration and typed exceptions.
- Ruff formats and lints all Python files.
