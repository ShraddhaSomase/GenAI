# ── MudraMitra API ───────────────────────────────────────────────────────────
# CPU-only image. sentence-transformers runs on CPU (no CUDA).
# Build arg SKIP_MODEL_DOWNLOAD=1 lets CI skip the ~90 MB HF download.

FROM python:3.11-slim AS builder

ARG SKIP_MODEL_DOWNLOAD=0

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch — avoids pulling any CUDA / triton / nvidia wheels
RUN pip install --no-cache-dir --prefix=/install \
    "torch==2.2.2+cpu" \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt \
        --extra-index-url https://download.pytorch.org/whl/cpu

# Pre-download the embedding model (skipped in CI via build arg)
RUN if [ "$SKIP_MODEL_DOWNLOAD" = "0" ]; then \
      PYTHONPATH=/install/lib/python3.11/site-packages \
      /install/bin/python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"; \
    fi


# ── Stage 2: lean runtime image ──────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install     /usr/local
COPY --from=builder /root/.cache /root/.cache

COPY app/        ./app/
COPY prompts/    ./prompts/
COPY data/records.json         ./data/records.json
COPY data/source_manifest.json ./data/source_manifest.json
COPY data/standup_faq.txt      ./data/standup_faq.txt
COPY data/feedback.json        ./data/feedback.json
COPY data/questions.json       ./data/questions.json

RUN mkdir -p /app/data/chroma_db

RUN useradd -m appuser \
    && chown -R appuser /app \
    && chown -R appuser /root/.cache 2>/dev/null || true
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
