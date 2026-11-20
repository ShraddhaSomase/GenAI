"""Tools available to the MudraMitra agent."""

from app.rag import ask_question
from app.records import count_by, get_by_id, load_records, search


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


def emi_schedule(loan_amount, annual_rate, months):
    """Calculate monthly EMI and a month-wise repayment schedule."""
    if isinstance(loan_amount, bool) or not isinstance(loan_amount, (int, float)):
        raise ValueError("Loan amount must be a number.")
    if isinstance(annual_rate, bool) or not isinstance(annual_rate, (int, float)):
        raise ValueError("Annual interest rate must be a number.")
    if isinstance(months, bool) or not isinstance(months, int):
        raise ValueError("Months must be a whole number.")

    if loan_amount <= 0:
        raise ValueError("Loan amount must be greater than zero.")
    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")
    if months <= 0:
        raise ValueError("Months must be greater than zero.")

    principal = float(loan_amount)
    monthly_rate = float(annual_rate) / (12 * 100)

    if monthly_rate == 0:
        emi = principal / months
    else:
        factor = (1 + monthly_rate) ** months
        emi = principal * monthly_rate * factor / (factor - 1)

    monthly_emi = round(emi, 2)
    balance = principal
    schedule = []

    for month in range(1, months + 1):
        opening_balance = balance
        interest = round(opening_balance * monthly_rate, 2)

        if month == months:
            principal_paid = round(opening_balance, 2)
            payment = round(principal_paid + interest, 2)
        else:
            payment = monthly_emi
            principal_paid = round(payment - interest, 2)
            principal_paid = min(principal_paid, round(opening_balance, 2))

        balance = round(max(0, opening_balance - principal_paid), 2)

        schedule.append({
            "month": month,
            "opening_balance": round(opening_balance, 2),
            "emi": payment,
            "principal": principal_paid,
            "interest": interest,
            "closing_balance": balance
        })

    total_payment = round(sum(row["emi"] for row in schedule), 2)
    total_interest = round(total_payment - principal, 2)

    return {
        "loan_amount": round(principal, 2),
        "annual_interest_rate": float(annual_rate),
        "months": months,
        "monthly_emi": monthly_emi,
        "total_interest": total_interest,
        "total_payment": total_payment,
        "schedule": schedule
    }


TOOLS = {
    "search_records": search_records,
    "count_records": count_records,
    "get_record": get_record,
    "rag_search": rag_search,
    "emi_schedule": emi_schedule,
}


def execute_tool(tool_name, arguments):
    """Execute an approved tool by name."""
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary")

    return TOOLS[tool_name](**arguments)
