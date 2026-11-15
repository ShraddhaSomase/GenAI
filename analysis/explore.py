"""Explore MudraMitra scheme records using pandas.

Run from the project root:
    python analysis/explore.py
"""

from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"

df = pd.read_json(DATA_FILE)

print(f"Loaded {len(df)} scheme records from {DATA_FILE.name}")
print(f"Columns: {list(df.columns)}")

print("\n--- Records by loan category ---")
category_counts = df["loan_category"].value_counts()

print(category_counts.to_string())

print("\n--- Loan amount ranges ---")
for category, group in df.groupby("loan_category"):
    print(f"\n{category}:")
    for amount in group["amount_range"].dropna().unique():
        print(f"  {amount}")

print("\n--- Eligibility information ---")
for category, group in df.groupby("loan_category"):
    print(f"\n{category}:")
    for applicant in group["who_can_apply"].dropna().unique():
        print(f"  - {applicant}")

print("\nMUDRAMITRA data exploration completed.")
