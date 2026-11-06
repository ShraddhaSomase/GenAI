
import csv
import requests
from pathlib import Path

from app.models import Record

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CSV_FILE = RAW_DIR / "loan_data.csv"

# GitHub raw CSV URL
DATA_URL = "https://raw.githubusercontent.com/ShraddhaSomase/GenAI/refs/heads/main/data/raw/loan_data.csv"


def fetch_data():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        print("Downloading loan dataset...")

        response = requests.get(DATA_URL, timeout=15)
        response.raise_for_status()

        CSV_FILE.write_bytes(response.content)

        print("Dataset downloaded successfully!")
        print(f"Saved at: {CSV_FILE}")

        return True

    except requests.exceptions.Timeout:
        print("Error: Request timed out.")

    except requests.exceptions.ConnectionError:
        print("Error: Connection failed.")

    except requests.exceptions.HTTPError as error:
        print(f"HTTP Error: {error}")

    except requests.exceptions.RequestException as error:
        print(f"Download Error: {error}")

    return False


def load_records():
    records = []

    try:
        with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    record = Record(
                        application_id=row["application_id"],
                        application_date=row["application_date"],
                        age=int(row["age"] or 0),
                        annual_income=float(row["annual_income"] or 0),
                        employment_years=int(row["employment_years"] or 0),
                        home_ownership=row["home_ownership"] or "Unknown",
                        purpose=row["purpose"] or "Unknown",
                        loan_amount=float(row["loan_amount"] or 0),
                        term_months=int(row["term_months"] or 0),
                        credit_score=int(row["credit_score"] or 0),
                        dti_pct=float(row["dti_pct"] or 0),
                        decision=row["decision"] or "Unknown",
                        interest_rate=float(row["interest_rate"] or 0),
                        monthly_payment=float(row["monthly_payment"] or 0),
                        loan_status=row["loan_status"] or "Unknown"
                    )

                    records.append(record)

                except (ValueError, KeyError) as error:
                    print(f"Skipping invalid row: {error}")

        print(f"Total Record objects created: {len(records)}")
        return records

    except FileNotFoundError:
        print("Error: CSV file not found.")
        return []

    except OSError as error:
        print(f"File Error: {error}")
        return []


if __name__ == "__main__":

    downloaded = fetch_data()

    if downloaded or CSV_FILE.exists():
        records = load_records()

        print("\n========== FIRST 5 RECORDS ==========")

        for record in records[:5]:
            print(record)
    else:
        print("No dataset available.")
