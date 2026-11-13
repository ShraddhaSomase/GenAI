
import csv
import json
from dataclasses import asdict
from pathlib import Path

from app.models import Record

RAW_FILE = Path("data/raw/loan_data.csv")
OUTPUT_FILE = Path("data/records.json")


def ingest_data():
    clean_records = []
    bad_rows = 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with RAW_FILE.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    record = Record(
                        credit_policy=int(row["credit.policy"]),
                        purpose=str(row["purpose"]).strip(),
                        interest_rate=float(row["int.rate"]),
                        installment=float(row["installment"]),
                        log_annual_income=float(row["log.annual.inc"]),
                        dti=float(row["dti"]),
                        fico=int(row["fico"]),
                        days_with_cr_line=float(row["days.with.cr.line"]),
                        revolving_balance=float(row["revol.bal"]),
                        revolving_utilization=float(row["revol.util"]),
                        inquiries_last_6_months=int(row["inq.last.6mths"]),
                        delinquencies_2_years=int(row["delinq.2yrs"]),
                        public_records=int(row["pub.rec"]),
                        not_fully_paid=int(row["not.fully.paid"])
                    )

                    clean_records.append(asdict(record))

                except (ValueError, TypeError, KeyError):
                    bad_rows += 1
                    continue

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(clean_records, file, indent=4)

        print("\n========== INGESTION REPORT ==========")
        print("Total clean records:", len(clean_records))
        print("Bad rows:", bad_rows)
        print("Total processed:", len(clean_records) + bad_rows)
        print("JSON saved at:", OUTPUT_FILE)

    except FileNotFoundError:
        print("Error: loan_data.csv not found in data/raw/")

    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    ingest_data()
