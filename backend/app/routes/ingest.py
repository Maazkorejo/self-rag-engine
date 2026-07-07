from flask import Blueprint, request, jsonify
from app.services.file_parser import extract_text
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embeddings_batch
from app.services.document_store import create_document, insert_chunks
from app.services.auth_decorator import require_api_key
from app import limiter

ingest_bp = Blueprint("ingest", __name__)


@ingest_bp.route("/ingest", methods=["POST"])
@require_api_key
@limiter.limit("100 per hour")
def ingest_document():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Attach a file under the 'file' field."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    allowed_extensions = ("pdf", "txt", "md")
    extension = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""

    if extension not in allowed_extensions:
        return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"}), 400

    try:
        file_bytes = file.read()
        text = extract_text(file_bytes, file.filename)

        if not text.strip():
            return jsonify({"error": "No extractable text found in file."}), 400

        chunks = chunk_text(text)
        embeddings = generate_embeddings_batch(chunks)

        document_id = create_document(file.filename)
        chunk_count = insert_chunks(document_id, chunks, embeddings)

        return jsonify({
            "document_id": document_id,
            "filename": file.filename,
            "chunk_count": chunk_count
        }), 201

    except Exception as e:
        return jsonify({"error": f"Ingestion failed: {str(e)}"}), 500