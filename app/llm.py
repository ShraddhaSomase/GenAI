import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from app.records import load_records
from app.smart_search import smart_search

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = PROJECT_ROOT / "prompts"

# Load .env if present (local dev). On Render/CI the key comes from env directly.
load_dotenv(PROJECT_ROOT / ".env", override=False)

api_key = os.getenv("GROQ_API_KEY")

# Defer the error to request time so the app still starts on Render
# even if the secret is not yet configured.
client = Groq(api_key=api_key) if api_key else None


def _get_client():
    if client is None:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Add it as an environment variable on Render (or in .env locally)."
        )
    return client


def load_prompt(filename):
    """Read a prompt file."""
    prompt_path = PROMPT_DIR / filename
    with open(prompt_path, "r", encoding="utf-8-sig") as file:
        return file.read()


def get_llm_response(user_message, task_version="v2"):
    """Retrieve MUDRA records and generate a structured LLM response."""
    if task_version not in ("v1", "v2"):
        raise ValueError("task_version must be v1 or v2")

    groq = _get_client()
    records = load_records()

    retrieved_records = smart_search(
        records,
        user_message,
        top_k=4,
        diversify_categories=True,
    )

    context = json.dumps(retrieved_records, ensure_ascii=False, indent=2)
    system_prompt = load_prompt("system_prompt.md")
    task_prompt = load_prompt(f"task_prompt_{task_version}.md")

    user_content = f"""
Use the following retrieved MudraMitra records as your source of information.

RETRIEVED RECORDS:
{context}

USER QUESTION:
{user_message}

IMPORTANT:
- Answer only using the retrieved records.
- Do not use guessed or invented information.
- If the records do not contain the answer, clearly say that the information is unavailable.
- Do not treat a missing interest rate or policy detail as known.
- Return only valid JSON with answer, confidence, and follow_up.
"""

    response = groq.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt + "\n\n" + task_prompt},
            {"role": "user",   "content": user_content},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    result = response.choices[0].message.content

    try:
        data = json.loads(result)
        confidence = str(data.get("confidence", "low")).lower()
        if confidence not in ("high", "medium", "low"):
            confidence = "low"
        return {
            "answer":    str(data.get("answer",   "No answer generated.")),
            "confidence": confidence,
            "follow_up": str(data.get("follow_up", "Would you like more information?")),
        }

    except (json.JSONDecodeError, TypeError):
        return {
            "answer":    result or "No answer generated.",
            "confidence": "low",
            "follow_up": "Would you like me to try again?",
        }
