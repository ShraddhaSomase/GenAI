"""Hand-written agent loop for MudraMitra."""

import json
import re

from app.llm import client
from app.tools import execute_tool

MODEL_NAME = "qwen/qwen3.8-27b"
MAX_ITERATIONS = 3

SYSTEM_PROMPT = """
You are the MudraMitra AI agent.

You can use these tools:

1. search_records
   Arguments: {"keyword": "text"}
   Purpose: Search loan application records.

2. count_records
   Arguments: {"field": "purpose"}
   Purpose: Count records grouped by a field.

3. get_record
   Arguments: {"record_id": "LN-000001"}
   Purpose: Find a loan application by ID.

4. rag_search
   Arguments: {"question": "text", "top_k": 4}
   Purpose: Answer questions using MUDRA documents with citations.

Choose a tool when the question requires information from records
or documents.

Return ONLY valid JSON.

To call a tool:
{
  "action": "tool",
  "tool_name": "rag_search",
  "arguments": {"question": "What is Shishu category?"}
}

To give the final answer:
{
  "action": "final",
  "answer": "Your final answer"
}

Use the tool result to prepare your final answer.
Never invent tool results or document information.
"""


def clean_json(text):
    """Remove optional Markdown JSON code fences."""
    return re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        text.strip(),
        flags=re.IGNORECASE
    )


def run_agent(question):
    """Run the agent until it produces a final answer."""

    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "tools_used": [],
            "steps": 0
        }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    tools_used = []

    for step in range(1, MAX_ITERATIONS + 1):

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0,
            max_tokens=700,
            response_format={"type": "json_object"}
        )

        raw_response = response.choices[0].message.content or ""

        try:
            decision = json.loads(clean_json(raw_response))
        except (json.JSONDecodeError, TypeError):
            return {
                "answer": "The agent could not process the response.",
                "tools_used": tools_used,
                "steps": step
            }

        if decision.get("action") == "final":
            return {
                "answer": str(decision.get("answer", "")),
                "tools_used": tools_used,
                "steps": step
            }

        if decision.get("action") != "tool":
            return {
                "answer": "The agent returned an unsupported action.",
                "tools_used": tools_used,
                "steps": step
            }

        tool_name = decision.get("tool_name")
        arguments = decision.get("arguments", {})

        try:
            tool_result = execute_tool(tool_name, arguments)
        except Exception as error:
            tool_result = {
                "error": str(error)
            }

        tools_used.append(tool_name)

        messages.append({
            "role": "assistant",
            "content": raw_response
        })

        messages.append({
            "role": "user",
            "content": (
                "Tool result:\n"
                + json.dumps(tool_result, ensure_ascii=False, default=str)
                + "\nUse this result to answer the original question. "
                "If another tool is needed, select it. Otherwise return "
                "your final answer as JSON."
            )
        })

    return {
        "answer": "The agent reached its maximum number of tool calls.",
        "tools_used": tools_used,
        "steps": MAX_ITERATIONS
    }
