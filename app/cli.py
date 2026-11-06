from .records import (
    load_records,
    display_records,
    search_record,
    filter_records
)


def main():
    print("Welcome to MudraMitra")

    print("1. Display Records")
    print("2. Search Record")
    print("3. Filter by Amount")

    choice = input("Enter your choice: ")

    if choice == "1":
        display_records()

    elif choice == "2":
        record_id = int(input("Enter ID: "))
        print(search_record(record_id))

    elif choice == "3":
        amount = int(input("Enter amount: "))
        filter_records(amount)

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()