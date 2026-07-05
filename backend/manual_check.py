from app.services.reflection import should_retrieve, is_relevant, is_supported, is_useful
from app.services.chunking import chunk_text

# ---------- Reflection functions ----------

print("should_retrieve('What is the capital of France?'):", should_retrieve("What is the capital of France?"))
print("should_retrieve('What were Q3 2025 revenue figures for Acme Corp?'):", should_retrieve("What were Q3 2025 revenue figures for Acme Corp?"))

print("is_relevant (relevant passage):", is_relevant("What is pgvector?", "pgvector is a PostgreSQL extension for vector similarity search."))
print("is_relevant (irrelevant passage):", is_relevant("What is pgvector?", "The weather in Paris is sunny today."))

print("is_supported:", is_supported("pgvector enables cosine similarity search in Postgres.", ["pgvector is a PostgreSQL extension for vector similarity search."]))

print("is_useful:", is_useful("What is pgvector?", "pgvector is a PostgreSQL extension that enables vector similarity search."))

# ---------- Chunking ----------

sample = " ".join([f"word{i}" for i in range(1200)])
chunks = chunk_text(sample)
print(f"Total chunks: {len(chunks)}")
print(f"First chunk word count: {len(chunks[0].split())}")
print(f"Last chunk word count: {len(chunks[-1].split())}")

# ---------- Embeddings ----------

from app.services.embeddings import generate_embedding, generate_embeddings_batch

emb = generate_embedding("pgvector enables similarity search in Postgres.")
print(f"Single embedding length: {len(emb)}")
print(f"First 5 values: {emb[:5]}")

batch = generate_embeddings_batch(["First passage.", "Second passage."])
print(f"Batch size: {len(batch)}")
print(f"Each embedding length: {len(batch[0])}")

# ---------- Supabase storage ----------

from app.services.document_store import create_document, insert_chunks, list_documents

doc_id = create_document("test_document.txt")
print(f"Created document with id: {doc_id}")

test_chunks = ["This is the first test chunk.", "This is the second test chunk."]
test_embeddings = generate_embeddings_batch(test_chunks)

inserted_count = insert_chunks(doc_id, test_chunks, test_embeddings)
print(f"Inserted {inserted_count} chunks")

docs = list_documents()
print(f"Total documents in database: {len(docs)}")