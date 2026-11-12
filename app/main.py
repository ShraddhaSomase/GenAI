
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
import json

from app.records import load_records

app = FastAPI(
    title="GenAI Loan Record API",
    description="API for managing loan records and user questions",
    version="1.0.0"
)

# Questions file path
QUESTIONS_FILE = Path(__file__).resolve().parent.parent / "data" / "questions.json"


# Request model
class Question(BaseModel):
    question: str


# 1. Health Check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }


# 2. Get All Records with Optional Limit
@app.get("/records")
def get_records(limit: int | None = Query(default=None, ge=1)):
    records = load_records()

    if limit is not None:
        records = records[:limit]

    return {
        "total": len(records),
        "records": records
    }


# 3. Get Record by ID
@app.get(f"/records/{id}")
def get_record(id: str):
    records = load_records()

    for record in records:
        if str(record.get("id")) == id:
            return record

    raise HTTPException(
        status_code=404,
        detail="Record not found"
    )


# 4. Search Records
@app.get("/search")
def search_records(q: str = Query(..., min_length=1)):
    records = load_records()
    keyword = q.lower()

    results = [
        record for record in records
        if keyword in json.dumps(record).lower()
    ]

    return {
        "keyword": q,
        "total": len(results),
        "results": results
    }


# 5. Save User Question
@app.post("/questions")
def save_question(data: Question):
    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
            questions = json.load(file)
    else:
        questions = []

    new_question = {
        "id": len(questions) + 1,
        "question": question
    }

    questions.append(new_question)

    with open(QUESTIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(questions, file, indent=4)

    return {
        "message": "Question saved successfully",
        "data": new_question
    }
