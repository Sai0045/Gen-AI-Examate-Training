from app.records import load_records, search, count_by, get_by_id


def show(r):
    print(r["id"], "-", r["vaccine"], "| due:", r["due_age"], "| latest:", r["latest_age"])


def main():
    records = load_records()
    print("Loaded", len(records), "records")

    while True:
        print("\n--- TeekaTimer records ---")
        print("1. Print all")
        print("2. Search by keyword")
        print("3. Count by a field")
        print("4. Get record by id")
        print("0. Exit")
        choice = input("Choose: ")

        if choice == "1":
            for r in records:
                show(r)
        elif choice == "2":
            word = input("Keyword: ")
            results = search(records, word)
            if len(results) == 0:
                print("Nothing found")
            for r in results:
                show(r)
        elif choice == "3":
            field = input("Count by which field (route_site / dose / latest_age): ")
            print(count_by(records, field))
        elif choice == "4":
            try:
                number = int(input("Record id: "))
            except ValueError:
                print("Please type a number")
                continue
            r = get_by_id(records, number)
            if r is None:
                print("No record with that id")
            else:
                print(r)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
