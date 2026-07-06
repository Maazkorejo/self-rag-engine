from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    from app.routes.health import health_bp
    from app.routes.ingest import ingest_bp

    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(ingest_bp, url_prefix="/api/v1")

    return app