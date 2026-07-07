from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config

limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    limiter.init_app(app)

    from app.routes.health import health_bp
    from app.routes.ingest import ingest_bp
    from app.routes.query import query_bp
    from app.routes.documents import documents_bp

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(ingest_bp, url_prefix="/api/v1")
    app.register_blueprint(query_bp, url_prefix="/api/v1")
    app.register_blueprint(documents_bp, url_prefix="/api/v1")
    swagger_bp = get_swaggerui_blueprint(
        "/api/docs", "/static/openapi.yaml", config={"app_name": "Self-RAG Engine API"}
    )
    app.register_blueprint(swagger_bp, url_prefix="/api/docs")

    return app