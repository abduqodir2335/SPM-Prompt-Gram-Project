import os
from pathlib import Path


class BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/promptgram-uploads"))


class DevelopmentConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://promptgram:dev@localhost:5432/promptgram",
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-not-secret")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


def get_config() -> type[BaseConfig]:
    environment = os.getenv("APP_ENV", "development")
    if environment == "test" and not os.getenv("DATABASE_URL"):
        raise RuntimeError("Tests require DATABASE_URL")
    if environment == "production":
        database_url = os.getenv("DATABASE_URL")
        secret_key = os.getenv("SECRET_KEY")
        if not database_url:
            raise RuntimeError("Production requires DATABASE_URL")
        if not secret_key:
            raise RuntimeError("Production requires SECRET_KEY")
    if environment not in {"development", "test", "production"}:
        raise RuntimeError(f"Unknown APP_ENV: {environment}")
    return {
        "development": DevelopmentConfig,
        "test": TestConfig,
        "production": ProductionConfig,
    }[environment]
