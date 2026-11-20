import json
import sqlite3
from pathlib import Path
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt

from app.agent_loop import MODEL_NAME
from app.llm import client
from app.tools import TOOLS, execute_tool

# SQLite database for persistent conversation memory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "agent_memory.sqlite"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

connection = sqlite3.connect(
    str(DB_PATH),
    check_same_thread=False
)

checkpointer = SqliteSaver(connection)


# LangGraph state
class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    action: str
    question: str
    tool_name: str
    arguments: dict
    approved: bool
    tool_result: Any
    answer: str
    tools_used: list


# Node 1: LLM selects a tool or produces a direct answer
def plan_node(state: AgentState):

    history = []

    for message in state.get("messages", [])[-10:]:
        role = "assistant" if message.type == "ai" else "user"
        history.append({
            "role": role,
            "content": str(message.content)
        })

    system_prompt = """
You are the MudraMitra AI agent.

Available tools:

1. search_records
Arguments: {"keyword": "text"}

2. count_records
Arguments: {"field": "purpose"}

3. get_record
Arguments: {"record_id": "LN-000001"}

4. rag_search
Arguments: {"question": "text", "top_k": 4}

5. emi_schedule
Arguments: {"loan_amount": 100000, "annual_rate": 12, "months": 12}
Purpose: Calculate monthly EMI and provide a month-wise principal and interest schedule.

For EMI or loan repayment calculations, use emi_schedule instead of calculating manually.

Choose a tool when the question requires records or document information.

Return only JSON.

For a tool call:
{
  "action": "tool",
  "tool_name": "rag_search",
  "arguments": {"question": "your question", "top_k": 4}
}

For a direct answer:
{
  "action": "final",
  "answer": "your answer"
}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            *history
        ],
        temperature=0,
        max_tokens=500,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content or "{}"

    try:
        decision = json.loads(raw)
    except json.JSONDecodeError:
        answer = "I could not understand the agent response."
        return {
            "action": "final",
            "answer": answer,
            "messages": [AIMessage(content=answer)],
            "tools_used": []
        }

    if decision.get("action") == "final":
        answer = str(decision.get("answer", "No answer generated."))
        return {
            "action": "final",
            "answer": answer,
            "messages": [AIMessage(content=answer)],
            "tools_used": []
        }

    tool_name = decision.get("tool_name")
    arguments = decision.get("arguments", {})

    if decision.get("action") != "tool":
        answer = "The agent selected an unsupported action."
        return {
            "action": "final",
            "answer": answer,
            "messages": [AIMessage(content=answer)],
            "tools_used": []
        }

    if tool_name not in TOOLS or not isinstance(arguments, dict):
        answer = "The agent selected an invalid tool or arguments."
        return {
            "action": "final",
            "answer": answer,
            "messages": [AIMessage(content=answer)],
            "tools_used": []
        }

    return {
        "action": "tool",
        "tool_name": tool_name,
        "arguments": arguments,
        "tools_used": []
    }


# Node 2: Ask a human to approve the tool call
def approval_node(state: AgentState):

    decision = interrupt({
        "message": "Human approval is required before tool execution.",
        "tool_name": state["tool_name"],
        "arguments": state["arguments"]
    })

    return {"approved": decision is True}


# Node 3: Execute the approved tool
def execute_node(state: AgentState):

    try:
        result = execute_tool(
            state["tool_name"],
            state["arguments"]
        )
    except Exception as error:
        result = {"error": str(error)}

    return {
        "tool_result": result,
        "tools_used": [state["tool_name"]]
    }


# Node 4: Generate the final answer using the tool result
def response_node(state: AgentState):

    question = state["messages"][-1].content

    result_text = json.dumps(
        state.get("tool_result", {}),
        ensure_ascii=False,
        default=str
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are MudraMitra. Answer the user's question "
                    "using the supplied tool result. Do not invent facts. "
                    "Keep the answer simple and clear."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Tool result: {result_text}"
                )
            }
        ],
        temperature=0,
        max_tokens=700
    )

    answer = response.choices[0].message.content or "No answer generated."

    return {
        "answer": answer,
        "messages": [AIMessage(content=answer)]
    }


# Node 5: Handle rejected approval
def denied_node(state: AgentState):

    answer = "The tool execution was not approved by the user."

    return {
        "answer": answer,
        "messages": [AIMessage(content=answer)]
    }


# Conditional routing
def route_after_plan(state: AgentState):
    if state.get("action") == "tool":
        return "approval"
    return END


def route_after_approval(state: AgentState):
    if state.get("approved") is True:
        return "execute"
    return "denied"


# Build the LangGraph workflow
builder = StateGraph(AgentState)

builder.add_node("plan", plan_node)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)
builder.add_node("respond", response_node)
builder.add_node("denied", denied_node)

builder.add_edge(START, "plan")

builder.add_conditional_edges(
    "plan",
    route_after_plan,
    {
        "approval": "approval",
        END: END
    }
)

builder.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "execute": "execute",
        "denied": "denied"
    }
)

builder.add_edge("execute", "respond")
builder.add_edge("respond", END)
builder.add_edge("denied", END)

agent_graph = builder.compile(checkpointer=checkpointer)

print("MudraMitra LangGraph workflow created successfully.")
