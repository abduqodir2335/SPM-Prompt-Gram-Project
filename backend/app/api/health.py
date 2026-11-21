import os

from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db

health_blueprint = Blueprint("health", __name__, url_prefix="/api")


@health_blueprint.get("/health")
def health():
    version = os.getenv("APP_VERSION", "development")
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        db.session.rollback()
        return (
            jsonify(status="degraded", version=version, db="error"),
            503,
        )
    return jsonify(status="ok", version=version, db="ok")
