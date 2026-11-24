# MudraMitra — Resume Bullets

## Three Resume Bullets

**1. AI Loan Assistant (RAG + LangGraph)**
Built *MudraMitra*, a production-ready AI assistant for MUDRA and Stand-Up India loan schemes using Python, FastAPI, and Retrieval-Augmented Generation (RAG); achieved **92.77% overall evaluation score** (100% answerability accuracy at top_k=5) by implementing hybrid semantic + keyword search with reciprocal rank fusion over government PDFs.

**2. Production Hardening**
Added in-memory response cache (128-entry LRU, 5-minute TTL) that eliminates repeated LLM calls; measured **average /ask latency of ~1,200 ms** (live, uncached) vs **< 5 ms** (cache hit); instrumented every request with structured logs (latency_ms, prompt_tokens, completion_tokens); enforced 2,000-character input limit and prompt-injection safeguards validated by automated tests.

**3. Full CI/CD Pipeline**
Wrote 50 pytest tests covering records, smart search, RAG with fake LLM, agent tools (EMI schedule), and prompt-injection protection; configured GitHub Actions CI (ruff lint ? pytest ? Docker build) with green badge; containerised the full stack with Docker Compose (CPU-only FastAPI API + Streamlit UI); deployed API to Hugging Face Spaces with public `/health` endpoint.

---

## Technology Stack

| Category | Tools |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| AI / RAG | Groq LLM, ChromaDB, Sentence Transformers, LangGraph |
| Search | TF-IDF + cosine (scikit-learn), hybrid reciprocal rank fusion |
| Frontend | Streamlit (loan picker, citations, feedback) |
| Testing | Pytest (50 tests), unittest.mock |
| Lint / Format | Ruff |
| CI/CD | GitHub Actions, Docker, Docker Compose |
| Deployment | Hugging Face Spaces |
| Data | PMMY FAQ PDF, Stand-Up India FAQ PDF, JSON records |

---

## Project Links

- GitHub: https://github.com/ShraddhaSomase/GenAI
- Live API: https://mudramitra-api.onrender.com/health
- Swagger: https://mudramitra-api.onrender.com/docs
