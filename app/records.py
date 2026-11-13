"""MudraMitra - records module (Day 2).

Handles loading, saving, adding and summarising money records.
Each record is a dict: id, date, type, category, amount, mode, note.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# Use data/records.json if it exists, otherwise fall back to the sample file
DATA_FILE = DATA_DIR / "records.json"
if not DATA_FILE.exists():
    DATA_FILE = DATA_DIR / "sample_records.json"

VALID_TYPES = ("income", "expense")


def load_records(path=DATA_FILE):
    """Read all records from the JSON file. Returns [] if the file is missing."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_records(records, path=DATA_FILE):
    """Write all records back to the JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def next_id(records):
    """Return the next free record id."""
    return max((r["id"] for r in records), default=0) + 1


def add_record(records, rec_type, category, amount, mode, note="", date=None):
    """Validate and append a new record. Returns the new record."""
    rec_type = rec_type.strip().lower()
    if rec_type not in VALID_TYPES:
        raise ValueError("type must be 'income' or 'expense'")
    if amount <= 0:
        raise ValueError("amount must be greater than 0")
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    else:
        datetime.strptime(date, "%Y-%m-%d")  # raises ValueError if bad format

    record = {
        "id": next_id(records),
        "date": date,
        "type": rec_type,
        "category": category.strip().title(),
        "amount": round(float(amount), 2),
        "mode": mode.strip(),
        "note": note.strip(),
    }
    records.append(record)
    return record


def filter_by_type(records, rec_type):
    return [r for r in records if r["type"] == rec_type.lower()]


def filter_by_category(records, category):
    return [r for r in records if r["category"].lower() == category.strip().lower()]


def search_notes(records, keyword):
    keyword = keyword.lower()
    return [r for r in records if keyword in r["note"].lower()]


def delete_record(records, record_id):
    """Remove a record by id. Returns True if something was deleted."""
    for i, r in enumerate(records):
        if r["id"] == record_id:
            del records[i]
            return True
    return False


def total(records, rec_type):
    return round(sum(r["amount"] for r in records if r["type"] == rec_type), 2)


def balance(records):
    return round(total(records, "income") - total(records, "expense"), 2)


def summary_by_category(records, rec_type="expense"):
    ""f"Return {category: total} for the given type, highest first."""
    totals = {}
    for r in records:
        if r["type"] == rec_type:
            totals[r["category"]] = totals.get(r["category"], 0) + r["amount"]
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))