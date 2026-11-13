
import json
from pathlib import Path

DATA_FILE = Path("data/records.json")


def load_records():
    """Load loan records from JSON file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            print("Error: JSON data must contain a list.")
            return []

        return records

    except (json.JSONDecodeError, OSError) as error:
        print("Error loading records:", error)
        return []


def save_records(records):
    """Save records into JSON file."""
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=4)

        print("Records saved successfully!")

    except OSError as error:
        print("Error saving records:", error)


def add_record(record):
    """Add a new record."""
    records = load_records()
    records.append(record)
    save_records(records)


def get_all_records():
    """Return all records."""
    return load_records()


def search_records(keyword):
    """Search records using a keyword."""
    records = load_records()

    return [
        record for record in records
        if keyword.lower() in str(record).lower()
    ]


def get_record_count():
    """Return total number of records."""
    return len(load_records())


if __name__ == "__main__":
    records = load_records()

    print("Total loan records:", len(records))
    print("\nFirst 5 records:")

    for record in records[:5]:
        print(record)
