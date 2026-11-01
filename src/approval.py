def get_human_approval(draft):
    print("\n===== HUMAN APPROVAL =====")
    print("\nDraft Reply:\n")
    print(draft)

    print("\nOptions:")
    print("1. Approve")
    print("2. Reject")

    choice = input("\nChoose an option: ").strip()
    return choice == "1"
