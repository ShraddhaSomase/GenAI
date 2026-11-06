from dataclasses import dataclass


@dataclass
class Record:
    application_id: str
    application_date: str
    age: int
    annual_income: float
    employment_years: int
    home_ownership: str
    purpose: str
    loan_amount: float
    term_months: int
    credit_score: int
    dti_pct: float
    decision: str
    interest_rate: float
    monthly_payment: float
    loan_status: str