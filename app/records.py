
import json
from pathlib import Path

# JSON file location
DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_records.json"
)


def load_records():
    """Load all MUDRA records."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search(records, keyword):
    """Search records by keyword."""

    keyword = keyword.lower().strip()

    if not keyword:
        return []

    results = []

    for record in records:
        text = " ".join(str(value) for value in record.values())

        if keyword in text.lower():
            results.append(record)

    return results


def count_by(records, field):
    """Count records by category or another field."""

    counts = {}

    for record in records:
        value = record.get(field, "Unknown")
        counts[value] = counts.get(value, 0) + 1

    return counts


def get_by_id(records, record_id):
    """Find a record by ID."""

    for record in records:
        if record.get("id") == record_id:
            return record

    return None
