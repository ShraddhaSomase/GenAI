
import csv
import json
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "loan_data.csv"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


# Convert and clean numeric values
def clean_number(value, data_type=float):

    if value is None or value.strip() == "":
        return None

    return data_type(value)


# Load and clean CSV records
def load_and_clean_records():

    records = []
    bad_rows = 0

    try:
        with open(RAW_FILE, "r", encoding="utf-8-sig") as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=1):

                try:
                    record_id = row["application_id"].strip()

                    if not record_id:
                        raise ValueError("Missing application ID")

                    record = {
                        "id": record_id,
                        "name": f"Applicant {record_id}",

                        "application_date": row["application_date"].strip(),

                        "age": clean_number(row["age"], int),

                        "annual_income": clean_number(
                            row["annual_income"]
                        ),

                        "employment_years": clean_number(
                            row["employment_years"], int
                        ),

                        "home_ownership": row["home_ownership"].strip().title(),

                        "product": row["purpose"].strip().title(),

                        "amount": clean_number(row["loan_amount"]),

                        "term_months": clean_number(
                            row["term_months"], int
                        ),

                        "credit_score": clean_number(
                            row["credit_score"], int
                        ),

                        "dti_pct": clean_number(row["dti_pct"]),

                        "decision": row["decision"].strip().title(),

                        "interest_rate": clean_number(
                            row["interest_rate"]
                        ),

                        "monthly_payment": clean_number(
                            row["monthly_payment"]
                        ),

                        "status": row["loan_status"].strip().title()
                    }

                    # Validate important fields
                    if record["amount"] is not None and record["amount"] <= 0:
                        raise ValueError("Loan amount must be positive")

                    records.append(record)

                except (ValueError, KeyError, TypeError, AttributeError) as error:

                    bad_rows += 1
                    print(f"Skipping row {row_number}: {error}")

    except FileNotFoundError:
        print("Error: CSV file not found!")
        return

    except Exception as error:
        print("File processing error:", error)
        return

    # Save cleaned records to JSON
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    print("\n========== INGESTION REPORT ==========")
    print("Total clean records:", len(records))
    print("Bad rows:", bad_rows)
    print("Total processed:", len(records) + bad_rows)
    print("JSON file saved:", OUTPUT_FILE)
    print("======================================")


# Main function
if __name__ == "__main__":
    load_and_clean_records()
