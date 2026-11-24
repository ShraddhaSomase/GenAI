"""Tests for the /ask RAG endpoint with a fake LLM."""

import json
from unittest.mock import MagicMock, patch


def _make_fake_groq_client(found=True, answer="Test answer.", citations=None):
    """Return a mock Groq client whose create() returns the given payload."""
    if citations is None:
        citations = [1] if found else []

    fake_choice = MagicMock()
    fake_choice.message.content = json.dumps(
        {"found": found, "answer": answer, "citations": citations}
    )
    fake_resp = MagicMock()
    fake_resp.choices = [fake_choice]
    fake_resp.usage = None

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = fake_resp
    return mock_client


class TestAskEndpoint:
    def test_ask_returns_answer(self, api_client):
        response = api_client.post(
            "/ask", json={"question": "What is Shishu loan?"}
        )
        assert response.status_code == 200
        body = response.json()
        assert "answer" in body
        assert "found" in body
        assert "citations" in body

    def test_ask_empty_question_returns_422(self, api_client):
        response = api_client.post("/ask", json={"question": ""})
        assert response.status_code == 422

    def test_ask_missing_question_returns_422(self, api_client):
        response = api_client.post("/ask", json={})
        assert response.status_code == 422

    def test_ask_top_k_respected(self, api_client):
        response = api_client.post(
            "/ask", json={"question": "MUDRA loan limit", "top_k": 3}
        )
        assert response.status_code == 200

    def test_ask_llm_not_found_returns_found_false(self):
        """When the fake LLM says found=False the endpoint passes it through."""
        from fastapi.testclient import TestClient

        fake_client = _make_fake_groq_client(
            found=False,
            answer="Information not available.",
            citations=[],
        )

        with patch("app.rag._get_client", return_value=fake_client), \
             patch("app.llm._get_client", return_value=fake_client), \
             patch("app.rag.hybrid_search") as mock_search:

            mock_search.return_value = [
                {
                    "id": "chunk-1",
                    "text": "Some context",
                    "source": "pmmy_faq.pdf",
                    "page": 1,
                    "title": "PMMY FAQ",
                }
            ]

            from app.main import app
            client = TestClient(app)
            response = client.post(
                "/ask",
                json={"question": "What is the interest rate?"},
            )

        assert response.status_code == 200
        assert response.json()["found"] is False

    def test_ask_with_fake_llm_citation_included(self):
        """Verify citations list is populated when LLM returns citation [1]."""
        from fastapi.testclient import TestClient

        fake_client = _make_fake_groq_client(
            found=True,
            answer="Shishu covers up to Rs.50,000.",
            citations=[1],
        )

        with patch("app.rag._get_client", return_value=fake_client), \
             patch("app.llm._get_client", return_value=fake_client), \
             patch("app.rag.hybrid_search") as mock_search:

            mock_search.return_value = [
                {
                    "id": "chunk-1",
                    "text": "Shishu loans are up to 50000.",
                    "source": "pmmy_faq.pdf",
                    "page": 1,
                    "title": "PMMY FAQ",
                }
            ]

            from app.main import app
            client = TestClient(app)
            response = client.post(
                "/ask",
                json={"question": "What is Shishu?"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["found"] is True
        assert len(body["citations"]) == 1
        assert body["citations"][0]["source"] == "pmmy_faq.pdf"
