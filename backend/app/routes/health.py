from flask import Blueprint, jsonify
from app.config import Config

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    groq_configured = bool(Config.GROQ_API_KEY)
    supabase_configured = bool(Config.SUPABASE_URL and Config.SUPABASE_KEY)

    return jsonify({
        "status": "ok",
        "service": "self-rag-engine",
        "groq_configured": groq_configured,
        "supabase_configured": supabase_configured
    }), 200