
"""MudraMitra - FastAPI service (day-04).

Run from the project root:
    uvicorn app.main:app --reload

Docs: http://127.0.0.1:8000/docs
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app import records as rec
from app.smart_search import smart_search

# Create FastAPI application
app = FastAPI(
    title="MudraMitra API",
    description="API for managing loan records and user questions",
    version="1.0.0"
)

# Questions file path
QUESTIONS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "questions.json"
)


class QuestionRequest(BaseModel):
    question: str


# 1. Health check
@app.get("/health")
def health():
    return {"status": "ok"}


# 2. List records with optional limit
@app.get("/records")
def list_records(limit: Optional[int] = Query(None, ge=1)):
    records = rec.load_records()

    return records[:limit] if limit else records


# 3. Get one loan record by position
@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = rec.load_records()

    if record_id < 1 or record_id > len(records):
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return records[record_id - 1]


# 4. Smart search using TF-IDF and cosine similarity
@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):
    results = smart_search(
        rec.load_records(),
        q,
        top_k=3
    )

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# 5. Save user question
@app.post("/questions", status_code=201)
def submit_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            questions = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        questions = []

    entry = {
        "id": len(questions) + 1,
        "question": question,
        "asked_at": datetime.now().isoformat(timespec="seconds")
    }

    questions.append(entry)

    QUESTIONS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            questions,
            f,
            indent=2,
            ensure_ascii=False
        )

    return entry
