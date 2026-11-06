
"""MudraMitra - command line interface (Day 2)."""

from app import records as rec

MENU = """
===== MudraMitra =====
1. View all records
2. Add a record
3. Filter by category
4. Search notes
5. Delete a record
6. Summary (income, expense, balance)
7. Expense by category
0. Exit
"""


def show(records):
    if not records:
        print("No records found.")
        return

    print(
        f"{'ID':<4} {'Date':<12} {'Type':<9} "
        f"{'Category':<15} {'Amount':>10} {'Mode':<14} Note"
    )
    print("-" * 90)

    for r in records:
        print(
            f"{r.get('id', '-'):<4} "
            f"{r.get('date', '-'):<12} "
            f"{r.get('type', '-'):<9} "
            f"{r.get('category', '-'):<15} "
            f"{float(r.get('amount', 0)):>10.2f} "
            f"{r.get('mode', '-'):<14} "
            f"{r.get('note', '')}"
        )


def ask_add(records):
    try:
        rec_type = input("Type (income/expense): ").strip().lower()

        if rec_type not in ("income", "expense"):
            print("Invalid type! Enter income or expense.")
            return

        category = input("Category: ").strip()
        amount = input("Amount (Rs): ").strip()
        mode = input("Mode (UPI/Cash/Card/Bank Transfer): ").strip()
        note = input("Note (optional): ").strip()
        date = input("Date YYYY-MM-DD (blank = today): ").strip()

        new = rec.add_record(
            records,
            rec_type,
            category,
            amount,
            mode,
            note,
            date or None
        )

        rec.save_records(records)
        print(f"\nRecord #{new['id']} saved successfully!")

    except ValueError as err:
        print(f"Could not add record: {err}")


def main():
    records = rec.load_records()

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            show(records)

        elif choice == "2":
            ask_add(records)

        elif choice == "3":
            category = input("Enter category: ")
            show(rec.filter_by_category(records, category))

        elif choice == "4":
            keyword = input("Enter keyword: ")
            show(rec.search_notes(records, keyword))

        elif choice == "5":
            try:
                rid = int(input("Record ID to delete: "))

                if rec.delete_record(records, rid):
                    rec.save_records(records)
                    print("Record deleted successfully!")
                else:
                    print("Record not found.")

            except ValueError:
                print("Please enter a valid number.")

        elif choice == "6":
            print("\n===== Financial Summary =====")
            print(f"Total income : Rs {rec.total(records, 'income'):.2f}")
            print(f"Total expense: Rs {rec.total(records, 'expense'):.2f}")
            print(f"Balance      : Rs {rec.balance(records):.2f}")

        elif choice == "7":
            print("\n===== Expense by Category =====")

            summary = rec.summary_by_category(records)

            if not summary:
                print("No expense records found.")
            else:
                for category, amount in summary.items():
                    print(f"{category:<15} Rs {amount:>10.2f}")

        elif choice == "0":
            print("Thank you for using MudraMitra!")
            break

        else:
            print("Invalid option! Please choose 0-7.")


if __name__ == "__main__":
    main()
