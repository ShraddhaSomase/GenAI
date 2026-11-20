# app.py — Hugging Face Spaces entry point
# HF Spaces expects a file called app.py in the repo root when sdk=docker is NOT used.
# Since we use sdk: docker, this file is not executed — the Dockerfile CMD runs instead.
# It is kept here only as a fallback hint.
from app.main import app  # noqa: F401  (re-export for `uvicorn app:app`)
