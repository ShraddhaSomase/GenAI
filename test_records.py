from app.records import load_records, search, count_by, get_by_id

records = load_records()

print("Total records:", len(records))
print("Category count:", count_by(records, "loan_category"))
print("Search Dairy:", search(records, "Dairy"))
print("MUDRA001:", get_by_id(records, "MUDRA001"))
print("Invalid ID:", get_by_id(records, "INVALID"))
