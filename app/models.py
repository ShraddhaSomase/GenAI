
from dataclasses import dataclass


@dataclass
class Record:
    loan_category: str
    amount_range: str
    who_can_apply: str
    margin_or_contribution: str
    repayment: str
    source_doc: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
