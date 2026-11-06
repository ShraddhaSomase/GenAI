
"""MudraMitra - records module (Day 2)."""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"

VALID_TYPES = ("income", "expense")


def load_records(path=DATA_FILE):
    """Load records and safely handle older JSON formats."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            return []

        cleaned_records = []

        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                continue

            # Support older sample records
            cleaned_records.append({
                "id": record.get("id", index),
                "date": record.get(
                    "date", datetime.now().strftime("%Y-%m-%d")
                ),
                "type": str(record.get("type", "expense")).lower(),
                "category": record.get(
                    "category", record.get("product", "Other")
                ),
                "amount": float(record.get("amount", 0)),
                "mode": record.get("mode", "Cash"),
                "note": record.get(
                    "note",
                    record.get("name", record.get("status", ""))
                )
            })

        return cleaned_records

    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        raise ValueError("sample_records.json contains invalid JSON")


def save_records(records, path=DATA_FILE):
    """Save records to JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


def next_id(records):
    """Generate the next available ID."""
    return max(
        (int(r.get("id", 0)) for r in records),
        default=0
    ) + 1


def add_record(records, rec_type, category, amount,
               mode, note="", date=None):

    rec_type = str(rec_type).strip().lower()

    if rec_type not in VALID_TYPES:
        raise ValueError("Enter only income or expense")

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number")

    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    if not str(category).strip():
        raise ValueError("Category cannot be empty")

    if date is None or not str(date).strip():
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be YYYY-MM-DD")

    record = {
        "id": next_id(records),
        "date": date,
        "type": rec_type,
        "category": category.strip().title(),
        "amount": round(amount, 2),
        "mode": mode.strip().title(),
        "note": note.strip()
    }

    records.append(record)
    return record


def filter_by_type(records, rec_type):
    return [
        r for r in records
        if r.get("type") == rec_type.lower()
    ]


def filter_by_category(records, category):
    return [
        r for r in records
        if str(r.get("category", "")).lower()
        == category.strip().lower()
    ]


def search_notes(records, keyword):
    keyword = keyword.lower()

    return [
        r for r in records
        if keyword in str(r.get("note", "")).lower()
    ]


def delete_record(records, record_id):
    for index, record in enumerate(records):
        if int(record.get("id", 0)) == record_id:
            del records[index]
            return True

    return False


def total(records, rec_type):
    return round(
        sum(
            float(r.get("amount", 0))
            for r in records
            if r.get("type") == rec_type.lower()
        ),
        2
    )


def balance(records):
    return round(
        total(records, "income") - total(records, "expense"),
        2
    )


def summary_by_category(records, rec_type="expense"):
    """Return category totals, highest first."""
    totals = {}

    for record in records:
        if record.get("type") == rec_type.lower():
            category = record.get("category", "Other")
            totals[category] = (
                totals.get(category, 0)
                + float(record.get("amount", 0))
            )

    return dict(
        sorted(totals.items(), key=lambda item: item[1], reverse=True)
    )
