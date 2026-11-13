
from dataclasses import dataclass


@dataclass
class Record:
    credit_policy: int
    purpose: str
    interest_rate: float
    installment: float
    log_annual_income: float
    dti: float
    fico: int
    days_with_cr_line: float
    revolving_balance: float
    revolving_utilization: float
    inquiries_last_6_months: int
    delinquencies_2_years: int
    public_records: int
    not_fully_paid: int

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
