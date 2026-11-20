"""Tests for app/records.py — load, search, count_by, get_by_id."""


from app.records import count_by, get_by_id, search

# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------

class TestSearch:
    def test_returns_matching_records(self, sample_records):
        results = search(sample_records, "Shishu")
        assert len(results) == 1
        assert results[0]["loan_category"] == "Shishu"

    def test_case_insensitive(self, sample_records):
        results = search(sample_records, "shishu")
        assert len(results) == 1

    def test_empty_keyword_returns_empty_list(self, sample_records):
        assert search(sample_records, "") == []

    def test_whitespace_keyword_returns_empty_list(self, sample_records):
        assert search(sample_records, "   ") == []

    def test_no_match_returns_empty_list(self, sample_records):
        assert search(sample_records, "nonexistent_xyz") == []

    def test_matches_across_all_fields(self, sample_records):
        # "pmmy_faq.pdf" is in source_doc for all records
        results = search(sample_records, "pmmy_faq")
        assert len(results) == 3


# ---------------------------------------------------------------------------
# count_by()
# ---------------------------------------------------------------------------

class TestCountBy:
    def test_counts_by_loan_category(self, sample_records):
        counts = count_by(sample_records, "loan_category")
        assert counts == {"Shishu": 1, "Kishor": 1, "Tarun": 1}

    def test_missing_field_uses_unknown(self, sample_records):
        counts = count_by(sample_records, "nonexistent_field")
        assert counts == {"Unknown": 3}

    def test_empty_records_returns_empty(self):
        assert count_by([], "loan_category") == {}


# ---------------------------------------------------------------------------
# get_by_id()
# ---------------------------------------------------------------------------

class TestGetById:
    def test_returns_none_when_not_found(self, sample_records):
        assert get_by_id(sample_records, "DOES_NOT_EXIST") is None

    def test_returns_none_on_empty_list(self):
        assert get_by_id([], "LN-001") is None
