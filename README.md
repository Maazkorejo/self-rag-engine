# Self-Reflective RAG Engine

A production-grade implementation of the **Self-RAG** architecture — adaptive retrieval, relevance filtering, groundedness verification, and utility scoring — built with prompt engineering over Groq's LLaMA 3.3 70B, rather than fine-tuning.

> Inspired by: Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2024). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.* ICLR 2024 (Oral, Top 1%). [arXiv:2310.11511](https://arxiv.org/abs/2310.11511)

## What It Does

Standard RAG pipelines retrieve documents indiscriminately and never verify whether a generated answer is actually grounded in what was retrieved — a major source of confident-sounding hallucinations. This engine adds four explicit self-critique checkpoints before returning an answer:

1. **`[Retrieve]`** — decides whether external documents are even needed for this query
2. **`[IsRel]`** — filters out irrelevant retrieved passages before generation
3. **`[IsSup]`** — verifies the generated answer is grounded in the retrieved passages, retrying (up to 2x) if not
4. **`[IsUse]`** — scores the final answer's usefulness on a 1-5 scale

If an answer still isn't well-grounded after retries, the API flags `hallucination_risk: true` rather than silently returning it.

## How This Differs From the Paper

The original Self-RAG paper fine-tunes a 7B/13B LLaMA model on data annotated with special reflection tokens by a GPT-4 critic. This project instead implements the same four-step reasoning architecture through structured prompts over a hosted LLM (Groq), making it deployable without any training step. See the [PRD](./SelfRAG_PRD_MuhammadMaaz_v2.docx) for the full breakdown of scope and design decisions.

## Architecture
┌─────────────────────┐
                    │   POST /api/v1/query │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   [Retrieve] check     │  Should I fetch documents?
                    └──────────┬───────────┘
                        YES    │    NO
                 ┌─────────────┘    └──────────────┐
      ┌──────────▼──────────┐                       │
      │  pgvector similarity │                       │
      │  search (top-k)      │                       │
      └──────────┬──────────┘                       │
                  │                                   │
      ┌──────────▼──────────┐                       │
      │   [IsRel] filter      │  Discard irrelevant   │
      │   (parallel per chunk)│  passages              │
      └──────────┬──────────┘                       │
                  │                                   │
                  └─────────────┬─────────────────────┘
                                │
                    ┌──────────▼───────────┐
                    │   Generate answer      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   [IsSup] verify       │  Retry up to 2x if
                    │   groundedness         │  NOT_SUPPORTED
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   [IsUse] score 1-5    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Structured JSON reply │
                    │  + reflection_log      │
                    └───────────────────────┘

                    ## Tech Stack

| Layer | Technology |
|---|---|
| LLM Inference | Groq API — LLaMA 3.3 70B |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, 384-dim) |
| Vector Store | Supabase PostgreSQL + pgvector |
| Backend | Flask + Gunicorn (Python 3.12), containerized with Docker |
| Frontend | React 18 + Vite + Tailwind CSS v4 |
| Auth | SHA-256 hashed API keys, Bearer token auth |
| Rate Limiting | Flask-Limiter (100 requests/hour on LLM-calling endpoints) |
| API Docs | Swagger UI via OpenAPI 3.0 spec |
| Testing | pytest, 46 tests, 100% coverage on all routes and pipeline logic |

## The Four Reflection Tokens

| Token | Function | Decision |
|---|---|---|
| `[Retrieve]` | `should_retrieve()` | Is external knowledge needed for this query? |
| `[IsRel]` | `is_relevant()` | Is this retrieved passage relevant? |
| `[IsSup]` | `is_supported()` | Is the answer grounded in the passages? |
| `[IsUse]` | `is_useful()` | How useful is the final answer (1-5)? |

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/ingest` | ✅ | Upload and index a document (PDF/TXT/MD) |
| POST | `/api/v1/query` | ✅ | Run the full Self-RAG pipeline |
| GET | `/api/v1/documents` | ✅ | List indexed documents |
| DELETE | `/api/v1/documents/:id` | ✅ | Remove a document and its chunks |
| GET | `/api/v1/health` | ❌ | Service health check |
| GET | `/api/v1/reflection/:query_id` | ✅ | Retrieve a past query's reflection trace |

Interactive docs available at `/api/docs` once running.

## Setup

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Fill in .env with GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY, FLASK_SECRET_KEY
python run.py
```

### Frontend
```bash
cd frontend
npm install
# Fill in .env with VITE_API_KEY
npm run dev
```

### Docker (backend)
```bash
cd backend
docker build -t self-rag-engine .
docker run -p 8080:8080 --env-file .env self-rag-engine
```

## Testing

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

46 tests, 100% coverage on all routes, pipeline logic, and auth.

## Deployment Status

The backend has been containerized and verified to build and run correctly in Docker (tested via Back4app). A permanent, always-on free-tier deployment is still in progress — several free hosting options are being evaluated to avoid card-required tiers. This section will be updated once a stable public URL is live.

## Project Status

- ✅ Document ingestion pipeline (chunking, embeddings, pgvector storage)
- ✅ Full Self-RAG reflection pipeline with retry logic and hallucination flagging
- ✅ REST API with API key auth and rate limiting
- ✅ React frontend with live reflection pipeline visualizer
- ✅ Swagger/OpenAPI documentation
- 🔶 Production deployment (in progress)

## Author

**Muhammad Maaz** — AI Developer & Backend Engineer, University of Sindh