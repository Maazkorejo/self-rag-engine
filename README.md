# Self-Reflective RAG Engine

A production-grade implementation of the **Self-RAG** architecture — adaptive retrieval, relevance filtering, groundedness verification, and utility scoring — built with prompt engineering over Groq's LLaMA 3.3 70B, rather than fine-tuning.

> Inspired by: Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2024). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.* ICLR 2024 (Oral, Top 1%). [arXiv:2310.11511](https://arxiv.org/abs/2310.11511)

## How This Differs From the Paper

The original Self-RAG paper fine-tunes a 7B/13B LLaMA model on data annotated with special reflection tokens by a GPT-4 critic. This project instead implements the same four-step reasoning architecture through structured prompts over a hosted LLM (Groq), making it deployable on free-tier infrastructure without any training. See the [PRD](./SelfRAG_PRD_MuhammadMaaz_v2.docx) for a full breakdown of scope and design decisions.

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
| Backend | Flask + Gunicorn (Python 3.11) |
| Frontend | React 18 + Vite + Tailwind CSS v4 |
| Deployment | Railway (backend) + Vercel (frontend) |

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
| POST | `/api/v1/ingest` | ✅ | Upload and index a document |
| POST | `/api/v1/query` | ✅ | Run the full Self-RAG pipeline |
| GET | `/api/v1/documents` | ✅ | List indexed documents |
| DELETE | `/api/v1/documents/:id` | ✅ | Remove a document |
| GET | `/api/v1/health` | ❌ | Service health check |
| GET | `/api/v1/reflection/:query_id` | ✅ | Retrieve a past query's reflection trace |

## Setup

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Fill in .env with GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
python run.py
```

### Frontend
```bash
cd frontend
npm install
# Fill in .env with VITE_API_KEY
npm run dev
```

## Testing

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

46 tests, 100% coverage on all route and pipeline logic.

## Author

**Muhammad Maaz** — AI Developer & Backend Engineer, University of Sindh