"""Tests for agent tools — emi_schedule and search_records."""

import pytest

from app.tools import emi_schedule, execute_tool


class TestEmiSchedule:
    def test_basic_calculation(self):
        result = emi_schedule(
            loan_amount=100_000,
            annual_rate=12.0,
            months=12,
        )
        assert result["monthly_emi"] > 0
        assert result["loan_amount"] == 100_000.0
        assert len(result["schedule"]) == 12

    def test_total_payment_exceeds_principal(self):
        result = emi_schedule(100_000, 10.0, 24)
        assert result["total_payment"] > result["loan_amount"]

    def test_total_interest_non_negative(self):
        result = emi_schedule(50_000, 8.0, 36)
        assert result["total_interest"] >= 0

    def test_zero_interest_rate(self):
        result = emi_schedule(12_000, 0.0, 12)
        assert result["monthly_emi"] == pytest.approx(1000.0, rel=1e-3)

    def test_closing_balance_zero_at_end(self):
        result = emi_schedule(50_000, 10.0, 12)
        assert result["schedule"][-1]["closing_balance"] == pytest.approx(
            0.0, abs=1.0
        )

    def test_invalid_loan_amount_raises(self):
        with pytest.raises(ValueError):
            emi_schedule(0, 10.0, 12)

    def test_negative_loan_amount_raises(self):
        with pytest.raises(ValueError):
            emi_schedule(-1000, 10.0, 12)

    def test_boolean_loan_amount_raises(self):
        with pytest.raises(ValueError):
            emi_schedule(True, 10.0, 12)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            emi_schedule(100_000, -1.0, 12)

    def test_zero_months_raises(self):
        with pytest.raises(ValueError):
            emi_schedule(100_000, 10.0, 0)


class TestExecuteTool:
    def test_unknown_tool_raises(self):
        with pytest.raises(ValueError, match="Unknown tool"):
            execute_tool("nonexistent_tool", {})

    def test_non_dict_arguments_raises(self):
        with pytest.raises(ValueError, match="dictionary"):
            execute_tool("emi_schedule", [1, 2, 3])

    def test_emi_schedule_via_execute_tool(self):
        result = execute_tool(
            "emi_schedule",
            {"loan_amount": 100_000, "annual_rate": 12.0, "months": 12},
        )
        assert "monthly_emi" in result
        assert result["monthly_emi"] > 0
