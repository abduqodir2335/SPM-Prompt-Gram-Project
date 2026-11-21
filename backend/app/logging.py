import json
import time
import uuid

from flask import g, request


def configure_request_logging(app) -> None:
    @app.before_request
    def start_request() -> None:
        g.request_started = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def finish_request(response):
        response.headers["X-Request-ID"] = g.request_id
        duration_ms = round((time.perf_counter() - g.request_started) * 1000, 3)
        app.logger.info(
            json.dumps(
                {
                    "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "level": "INFO",
                    "request_id": g.request_id,
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "user_id": getattr(g, "user_id", None),
                }
            )
        )
        return response
