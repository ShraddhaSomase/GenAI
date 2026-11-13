"""MudraMitra - explore the data with pandas.

Run from the project root:
    python analysis/explore.py
"""

import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
path = DATA_DIR / "records.json"
if not path.exists():
    path = DATA_DIR / "sample_records.json"

df = pd.read_json(path)
print(f"Loaded {len(df)} records from {path.name}\n")

income = df[df["type"] == "income"]["amount"].sum()
expense = df[df["type"] == "expense"]["amount"].sum()
top_cat = df[df["type"] == "expense"].groupby("category")["amount"].sum().idxmax()
top_amt = df[df["type"] == "expense"].groupby("category")["amount"].sum().max()
top_mode = df["mode"].value_counts().idxmax()
top_mode_n = df["mode"].value_counts().max()

print(f"Fact 1: Total income is Rs {:.2f} and total expense is Rs {:.2f} (balance Rs {:.2f}).".format(
    income, expense, income - expense))
print(f"Fact 2: The biggest expense category is {top_cat} at Rs {top_amt:.2f}.")
print(f"Fact 3: The most used payment mode is {top_mode} ({top_mode_n} of {len(df)} records).")