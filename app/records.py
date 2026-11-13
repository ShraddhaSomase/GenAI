
import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data" / "sample_records.json"
)

def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search(records, keyword):
    keyword = keyword.lower()

    return [
        record for record in records
        if any(
            keyword in str(value).lower()
            for value in record.values()
        )
    ]


def count_by(records, field):
    counts = {}

    for record in records:
        category = record.get(field, "Unknown")
        counts[category] = counts.get(category, 0) + 1

    return counts


def get_by_id(records, id):
    for record in records:
        if record.get("application_id") == id:
            return record

    return None
