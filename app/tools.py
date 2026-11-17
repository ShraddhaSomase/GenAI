"""Tools available to the MudraMitra agent."""

from app.records import load_records, search, count_by, get_by_id
from app.rag import ask_question


def search_records(keyword):
    """Search Mudra loan records using a keyword."""
    records = load_records()
    results = search(records, keyword)

    return {
        "total_found": len(results),
        "records": results
    }


def count_records(field="purpose"):
    """Count loan records grouped by a field."""
    records = load_records()
    return count_by(records, field)


def get_record(record_id):
    """Find a loan record using its application ID."""
    records = load_records()
    result = get_by_id(records, record_id)

    if result is None:
        return {"found": False, "message": "Record not found"}

    return {"found": True, "record": result}


def rag_search(question, top_k=4):
    """Answer a question using retrieved MUDRA documents."""
    return ask_question(question, top_k=top_k)


TOOLS = {
    "search_records": search_records,
    "count_records": count_records,
    "get_record": get_record,
    "rag_search": rag_search,
}


def execute_tool(tool_name, arguments):
    """Execute an approved tool by name."""
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary")

    return TOOLS[tool_name](**arguments)
