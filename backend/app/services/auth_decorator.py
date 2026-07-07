from functools import wraps
from flask import request, jsonify
from app.services.auth import verify_api_key


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header. Expected: Bearer <api_key>"}), 401

        raw_key = auth_header.split("Bearer ", 1)[1].strip()

        if not verify_api_key(raw_key):
            return jsonify({"error": "Invalid or inactive API key."}), 401

        return f(*args, **kwargs)

    return decorated