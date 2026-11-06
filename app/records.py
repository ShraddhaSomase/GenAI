import json

FILE_PATH = "data/sample_records.json"


def load_records():
    with open(FILE_PATH, "r") as file:
        return json.load(file)


def display_records():
    records = load_records()

    for record in records:
        print(record)


def search_record(record_id):
    records = load_records()

    for record in records:
        if record["id"] == record_id:
            return record

    return "Record not found"


def filter_records(amount):
    records = load_records()

    for record in records:
        if record["amount"] <= amount:
            print(record)