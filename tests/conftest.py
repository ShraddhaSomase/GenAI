"""Shared pytest fixtures for MudraMitra tests."""

import json
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Sample records fixture
# ---------------------------------------------------------------------------

SAMPLE_RECORDS = [
    {
        "loan_category": "Shishu",
        "amount_range": "upto Rs.50,000/-",
        "who_can_apply": "Any Indian Citizen with a non-farm business plan",
        "margin_or_contribution": "Not specified",
        "repayment": "Term Loan - Maximum tenure 7 years",
        "source_doc": "pmmy_faq.pdf",
    },
    {
        "loan_category": "Kishor",
        "amount_range": "above Rs.50,000/- and upto Rs. 5.00 Lakh",
        "who_can_apply": "Any Indian Citizen with a non-farm business plan",
        "margin_or_contribution": "Not specified",
        "repayment": "Term Loan - Maximum tenure 7 years",
        "source_doc": "pmmy_faq.pdf",
    },
    {
        "loan_category": "Tarun",
        "amount_range": "above Rs. 5.00 lakh and upto Rs.10.00 lakh",
        "who_can_apply": "Any Indian Citizen with a non-farm business plan",
        "margin_or_contribution": "Not specified",
        "repayment": "Term Loan - Maximum tenure 7 years",
        "source_doc": "pmmy_faq.pdf",
    },
]


@pytest.fixture
def sample_records():
    return SAMPLE_RECORDS


# ---------------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    """Return a TestClient for the FastAPI app with LLM calls patched."""
    from fastapi.testclient import TestClient

    # Patch the LLM client used by rag.py so no real API calls are made
    fake_choice = MagicMock()
    fake_choice.message.content = json.dumps({
        "found": True,
        "answer": "MUDRA loans have three categories: Shishu, Kishor, and Tarun.",
        "citations": [1],
    })

    fake_response = MagicMock()
    fake_response.choices = [fake_choice]

    with patch("app.rag.client") as mock_rag_client, \
         patch("app.llm.client") as mock_llm_client:

        mock_rag_client.chat.completions.create.return_value = fake_response
        mock_llm_client.chat.completions.create.return_value = fake_response

        from app.main import app
        client = TestClient(app)
        yield client
