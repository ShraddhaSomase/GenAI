"""Tests for app/smart_search.py — TF-IDF + cosine similarity search."""

from app.smart_search import record_to_text, remove_duplicates, smart_search

RECORDS = [
    {
        "loan_category": "Shishu",
        "amount_range": "upto Rs.50,000/-",
        "who_can_apply": "Any Indian Citizen with a non-farm business plan",
        "repayment": "Term Loan - Maximum tenure 7 years",
    },
    {
        "loan_category": "Kishor",
        "amount_range": "above Rs.50,000/- and upto Rs. 5.00 Lakh",
        "who_can_apply": "Any Indian Citizen with a non-farm business plan",
        "repayment": "Term Loan - Maximum tenure 7 years",
    },
    {
        "loan_category": "Tarun",
        "amount_range": "above Rs. 5.00 lakh and upto Rs.10.00 lakh",
        "who_can_apply": "Any Indian Citizen with a non-farm business plan",
        "repayment": "Term Loan - Maximum tenure 7 years",
    },
]


class TestRecordToText:
    def test_includes_all_values(self):
        record = {"loan_category": "Shishu", "amount_range": "50000"}
        text = record_to_text(record)
        assert "Shishu" in text
        assert "50000" in text

    def test_replaces_underscores_with_spaces(self):
        record = {"loan_category": "Tarun_Plus"}
        text = record_to_text(record)
        assert "_" not in text


class TestRemoveDuplicates:
    def test_removes_exact_duplicates(self):
        dupes = RECORDS + [RECORDS[0]]
        result = remove_duplicates(dupes)
        assert len(result) == 3

    def test_preserves_order(self):
        result = remove_duplicates(RECORDS)
        assert [r["loan_category"] for r in result] == [
            "Shishu", "Kishor", "Tarun"
        ]


class TestSmartSearch:
    def test_empty_question_returns_empty(self):
        assert smart_search(RECORDS, "") == []

    def test_empty_records_returns_empty(self):
        assert smart_search([], "MUDRA loan") == []

    def test_returns_at_most_top_k(self):
        results = smart_search(RECORDS, "loan tenure repayment", top_k=2)
        assert len(results) <= 2

    def test_result_contains_score(self):
        results = smart_search(RECORDS, "Shishu loan amount", top_k=1)
        if results:
            assert "score" in results[0]

    def test_diversify_categories(self):
        results = smart_search(
            RECORDS,
            "loan amount",
            top_k=3,
            diversify_categories=True,
        )
        categories = [r["loan_category"] for r in results]
        # With diversification all 3 categories should appear
        assert len(set(categories)) == len(results)
