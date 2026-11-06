

def show_menu():
    print("\n===== MUDRAMITRA =====")
    print("1. About Project")
    print("2. View Features")
    print("3. Exit")


while True:
    show_menu()

    choice = input("Enter your choice: ")

    if choice == "1":
        print("MudraMitra is a financial management project.")

    elif choice == "2":
        print("Features: Manage and view financial records.")

    elif choice == "3":
        print("Thank you for using MudraMitra!")
        break

    else:
        print("Invalid choice. Try again.")