
from app.records import load_records, search, count_by, get_by_id


def main():
    records = load_records()

    while True:
        print("\n===== MUDRAMITRA =====")
        print("1. View all records")
        print("2. Search by keyword")
        print("3. Count by category")
        print("4. Search by application ID")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            for record in records:
                print(record)

        elif choice == "2":
            keyword = input("Enter keyword: ")
            results = search(records, keyword)

            for record in results:
                print(record)

            print("Total found:", len(results))

        elif choice == "3":
            print(count_by(records, "purpose"))

        elif choice == "4":
            app_id = input("Enter application ID: ")
            result = get_by_id(records, app_id)
            print(result if result else "Record not found")

        elif choice == "5":
            print("Thank you!")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
