
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "data" / "records.json"

with open(file_path, "r") as file:
    records = json.load(file)

df = pd.DataFrame(records)

print("TOTAL LOAN RECORDS:")
print(len(df))

print("\nAVERAGE ANNUAL INCOME:")
print(df["annual_income"].mean())

print("\nLOAN DECISION DISTRIBUTION:")
print(df["decision"].value_counts())
