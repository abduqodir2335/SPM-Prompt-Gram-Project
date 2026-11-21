from flask import Flask, jsonify


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return (
            jsonify(error={"code": "not_found", "message": "Resource not found."}),
            404,
        )

    @app.errorhandler(500)
    def internal_error(_error):
        message = "Internal server error."
        return (
            jsonify(error={"code": "internal_error", "message": message}),
            500,
        )
