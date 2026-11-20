# ── MudraMitra API ───────────────────────────────────────────────────────────
# Multi-stage build: keeps the final image lean.
# Stage 1: install Python dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# System packages needed to compile some wheels (scikit-learn, chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: lean runtime image ──────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/        ./app/
COPY prompts/    ./prompts/
COPY data/records.json         ./data/records.json
COPY data/source_manifest.json ./data/source_manifest.json
COPY data/standup_faq.txt      ./data/standup_faq.txt
COPY data/feedback.json        ./data/feedback.json
COPY data/questions.json       ./data/questions.json

# ChromaDB will store its data in a mounted volume (see docker-compose.yml)
# so we only create the directory; actual DB files come from the volume.
RUN mkdir -p /app/data/chroma_db

# Non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
