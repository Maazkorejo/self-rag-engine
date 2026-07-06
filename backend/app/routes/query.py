from flask import Blueprint, request, jsonify
from app.services.pipeline import run_self_rag_pipeline
from app.services.query_log_store import log_query, get_query_log

query_bp = Blueprint("query", __name__)


@query_bp.route("/query", methods=["POST"])
def run_query():
    data = request.get_json(silent=True)

    if not data or "query" not in data or not data["query"].strip():
        return jsonify({"error": "Request body must include a non-empty 'query' field."}), 400

    query_text = data["query"]
    top_k = data.get("top_k", 5)
    force_retrieve = data.get("force_retrieve", False)

    try:
        result = run_self_rag_pipeline(query_text, top_k=top_k, force_retrieve=force_retrieve)

        query_id = log_query(
            query_text=query_text,
            reflection_log=result["reflection_log"],
            utility_score=result["utility_score"]
        )

        return jsonify({
            "query_id": query_id,
            "final_answer": result["final_answer"],
            "reflection_log": result["reflection_log"],
            "utility_score": result["utility_score"],
            "sources_used": result["sources_used"],
            "hallucination_risk": result["hallucination_risk"]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Query failed: {str(e)}"}), 500


@query_bp.route("/reflection/<query_id>", methods=["GET"])
def get_reflection(query_id):
    log = get_query_log(query_id)

    if not log:
        return jsonify({"error": "Query not found."}), 404

    return jsonify(log), 200