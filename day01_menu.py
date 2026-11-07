while True:
    print("\n--- TeekaTimer ---")
    print("1. About TeekaTimer")
    print("2. Sample questions")
    print("3. Check baby's vaccine stage")
    print("0. Exit")
    choice = input("Choose: ")

    if choice == "1":
        print("TeekaTimer tells you which govt vaccines are due for your baby.")
    elif choice == "2":
        print("- Which vaccines are due at 6 weeks?")
        print("- My baby missed a dose. Is it too late?")
    elif choice == "3":
        weeks = int(input("Baby's age in weeks: "))
        if weeks < 6:
            print("Birth doses (BCG, OPV-0, Hep B) apply. Ask your health worker.")
        elif weeks < 10:
            print("The 6-week doses are due now.")
        elif weeks < 14:
            print("The 10-week doses are due now.")
        else:
            print("The 14-week doses or later apply. Check the schedule.")
    elif choice == "0":
        print("Goodbye!")
        break
    else:
        print("Invalid choice, try again.")