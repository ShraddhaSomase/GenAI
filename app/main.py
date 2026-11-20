
"""MudraMitra - FastAPI service.

Run from the project root:
    uvicorn app.main:app --reload

Docs: http://127.0.0.1:8000/docs
"""

import json
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app import records as rec
from app.smart_search import smart_search
from app.vectorstore import semantic_search

APP_VERSION = "2.0.0"
_START_TIME = time.time()

# Create FastAPI application
app = FastAPI(
    title="MudraMitra API",
    description="AI-powered loan assistant for MUDRA and Stand-Up India schemes",
    version=APP_VERSION,
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
    uptime_seconds = int(time.time() - _START_TIME)
    return {
        "status": "ok",
        "version": APP_VERSION,
        "uptime_seconds": uptime_seconds,
    }


# 2. List records with optional limit
@app.get("/records")
def list_records(limit: int | None = Query(None, ge=1)):
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

# Day 06 - LLM Chat Integration
from pydantic import Field

from app.llm import get_llm_response


# Chat request model
class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000
    )


# 6. AI Chat endpoint
@app.post("/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        result = get_llm_response(question)

        return {
            "answer": result["answer"],
            "confidence": result["confidence"],
            "follow_up": result["follow_up"]
        }

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed"
        )



# Day 07 - Semantic Search using ChromaDB
@app.get("/search/semantic")
def search_semantic(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20)):
    question = q.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    results = semantic_search(question, n_results=limit)

    return {
        "query": question,
        "total_results": len(results),
        "results": results
    }

# Day 08 - RAG Question Answering API
from app.rag import ask_question


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=10, ge=1, le=10)


@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        result = ask_question(
            question,
            top_k=request.top_k
        )

        return {
            "question": question,
            "answer": result["answer"],
            "found": result["found"],
            "citations": result["citations"],
            "retrieved_chunks": result["retrieved_chunks"]
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to process the RAG request"
        )

# Day 09 - LangGraph Agent API
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.graph import agent_graph


class AgentRequest(BaseModel):
    question: str | None = None
    thread_id: str = Field(min_length=1, max_length=100)
    approved: bool | None = None


@app.post("/agent")
def run_langgraph_agent(request: AgentRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    try:
        # First request: start a new agent conversation
        if request.approved is None:

            question = (request.question or "").strip()

            if not question:
                raise HTTPException(
                    status_code=400,
                    detail="Question is required."
                )

            result = agent_graph.invoke(
                {
                    "messages": [
                        HumanMessage(content=question)
                    ],
                    "tools_used": []
                },
                config=config
            )

        # Follow-up request: resume after human approval
        else:

            result = agent_graph.invoke(
                Command(resume=request.approved),
                config=config
            )

        # Check whether the graph is waiting for approval
        interruptions = result.get("__interrupt__", [])

        if interruptions:
            return {
                "status": "approval_required",
                "thread_id": request.thread_id,
                "approval": interruptions[0].value
            }

        return {
            "status": "completed",
            "thread_id": request.thread_id,
            "answer": result.get("answer", ""),
            "tools_used": result.get("tools_used", [])
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Agent execution failed: {error!s}"
        )

