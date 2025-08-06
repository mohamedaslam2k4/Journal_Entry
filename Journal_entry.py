import datetime
import os

def create():
    date = datetime.date.today()
    entry = input("Enter your journal entry: ")
    filename = f"journal_{date}.txt"
    with open(filename, "a") as file:
        file.write(f"{datetime.datetime.now().strftime('%H:%M')} - {entry}\n")
    print(f"Journal entry created successfully! Filename:journal_{date}.txt")

def view():
    date = input("Enter the date (YYYY-MM-DD) to view journal entries, or press Enter to view all: ")
    if date:
        filename = f"journal_{date}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                print(file.read())
        else:
            print("No journal entries found for this date.")
    else:
        for filename in os.listdir():
            if filename.startswith("journal_") and filename.endswith(".txt"):
                print(f"\nJournal Entries for {filename[8:-4]}:")
                with open(filename, "r") as file:
                    print(file.read())

def delete():
    date = input("Enter the date (YYYY-MM-DD) of the journal entry to delete: ")
    filename = f"journal_{date}.txt"
    if os.path.exists(filename):
        os.remove(filename)
        print("Journal entry deleted successfully!")
    else:
        print("No journal entry found for this date.")

def main():
    while True:
        print("\n+-------------------------+  ")
        print("| Daily Journal Menu:     |")
        print("+-------------------------+")
        print("| 1. Create Journal Entry |")
        print("| 2. View Journal Entries |")
        print("| 3. Delete Journal Entry |")
        print("| 4. Quit                 |")
        print("+-------------------------+")
        choice= input("\nChoose an option: ")
        if choice == "1":
            create()
        elif choice == "2":
            view()
        elif choice == "3":
            delete()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()