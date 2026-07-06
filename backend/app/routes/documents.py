from flask import Blueprint, jsonify
from app.services.document_store import list_documents, delete_document

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/documents", methods=["GET"])
def get_documents():
    try:
        docs = list_documents()
        return jsonify({"documents": docs, "count": len(docs)}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list documents: {str(e)}"}), 500


@documents_bp.route("/documents/<document_id>", methods=["DELETE"])
def remove_document(document_id):
    try:
        delete_document(document_id)
        return jsonify({"message": f"Document {document_id} deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500