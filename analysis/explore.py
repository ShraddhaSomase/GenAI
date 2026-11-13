"""MudraMitra - explore the data with pandas.

Run from the project root:
    python analysis/explore.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
path = DATA_DIR / "records.json"
if not path.exists():
    path = DATA_DIR / "sample_records.json"

df = pd.read_json(path)
print(f"Loaded {len(df)} records and {len(df.columns)} columns from {path.name}\n")

# Fact 1: how many loans were not fully paid
unpaid_pct = df["not_fully_paid"].mean() * 100
print(f"Fact 1: {unpaid_pct:.1f}% of loans were not fully paid "
      f"({int(df['not_fully_paid'].sum())} of {len(df)}).")

# Fact 2: most common loan purpose
top_purpose = df["purpose"].value_counts().idxmax()
top_n = df["purpose"].value_counts().max()
print(f"Fact 2: The most common loan purpose is '{top_purpose}' ({top_n} loans).")

# Fact 3: average FICO score for fully paid vs not fully paid loans
fico = df.groupby("not_fully_paid")["fico"].mean()
print(f"Fact 3: Average FICO score is {fico[0]:.0f} for fully paid loans "
      f"and {fico[1]:.0f} for not fully paid loans.")