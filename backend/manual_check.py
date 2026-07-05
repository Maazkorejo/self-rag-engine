from app.services.reflection import should_retrieve, is_relevant, is_supported, is_useful

# Test [Retrieve]
print("should_retrieve('What is the capital of France?'):", should_retrieve("What is the capital of France?"))
print("should_retrieve('What were Q3 2025 revenue figures for Acme Corp?'):", should_retrieve("What were Q3 2025 revenue figures for Acme Corp?"))

# Test [IsRel]
print("is_relevant (relevant passage):", is_relevant("What is pgvector?", "pgvector is a PostgreSQL extension for vector similarity search."))
print("is_relevant (irrelevant passage):", is_relevant("What is pgvector?", "The weather in Paris is sunny today."))

# Test [IsSup]
print("is_supported:", is_supported("pgvector enables cosine similarity search in Postgres.", ["pgvector is a PostgreSQL extension for vector similarity search."]))

# Test [IsUse]
print("is_useful:", is_useful("What is pgvector?", "pgvector is a PostgreSQL extension that enables vector similarity search."))