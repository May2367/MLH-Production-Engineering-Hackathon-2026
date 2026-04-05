import logging
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from app.database import init_db
from app.routes import register_routes


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"}
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def create_app():
    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    init_db(app)
    from app import models
    register_routes(app)

    @app.after_request
    def log_request(response):
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
            }
        )
        return response

    @app.route("/health")
    def health():
        logger.info("health check")
        return jsonify(status="ok")

    @app.errorhandler(404)
    def not_found(e):
        logger.warning("not found", extra={"path": request.path})
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error("server error", extra={"error": str(e)})
        return jsonify({"error": "Internal server error"}), 500

    return app