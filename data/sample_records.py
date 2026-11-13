import csv
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "raw" / "loan_data.csv"
JSON_FILE = BASE_DIR / "sample_records.json"

# Read 20 real records from the original dataset
with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    records = [dict(row) for row in reader][:20]

# Save records in JSON format
with open(JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(records, file, indent=4)

# Print all records
print("\nALL RECORDS:")
for record in records:
    print(record)

# Search by keyword
def search_records(records, keyword):
    return [
        record for record in records
        if any(keyword.lower() in str(value).lower()
               for value in record.values())
    ]

# Count records by category
def count_by_category(records):
    return dict(Counter(record["purpose"] for record in records))

keyword = input("\nEnter keyword to search: ")

print("\nSEARCH RESULTS:")
for record in search_records(records, keyword):
    print(record)

print("\nCATEGORY COUNTS:")
print(count_by_category(records))

print("\nTotal records:", len(records))
