# main.py — Application launcher
#
# Default: launches the graphical interface.
# Console mode: python main.py --console

import sys

from gui.data_setup import setup_dummy_data


def run_console():
    """Original text-based ATM interface (kept for reference/testing)."""
    from exceptions import (
        CardBlockedError,
        InvalidPINError,
        InsufficientBalanceError,
        InsufficientATMFundsError,
        InvalidAmountError,
    )

    atm, customer = setup_dummy_data()
    print("Welcome to the ATM System")

    authenticated = False
    while not authenticated:
        try:
            entered_pin = input("Please enter your 4-digit PIN: ")
            if customer.card.validate_pin(entered_pin):
                authenticated = True
                print("\nAuthentication Successful!")
        except (InvalidPINError, CardBlockedError) as e:
            print(f"Error: {e}")
            if isinstance(e, CardBlockedError):
                return

    current_account = customer.get_account("1001")

    while True:
        print("\n====== ATM ======")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer Money")
        print("5. Change PIN")
        print("6. Mini Statement")
        print("7. Exit")

        choice = input("Select an option (1-7): ")

        try:
            if choice == "1":
                print(f"Current Balance: Rs. {current_account.get_balance():,.2f}")

            elif choice == "2":
                amount = float(input("Enter deposit amount: Rs. "))
                txn = atm.process_deposit(current_account, amount)
                print(f"Success! Transaction ID: {txn.transaction_id}")
                print(f"New Balance: Rs. {current_account.get_balance():,.2f}")

            elif choice == "3":
                amount = float(input("Enter withdrawal amount (Multiples of 500): Rs. "))
                txn = atm.process_withdrawal(current_account, amount)
                print(f"Please collect your cash. Transaction ID: {txn.transaction_id}")
                print(f"Remaining Balance: Rs. {current_account.get_balance():,.2f}")

            elif choice == "4":
                target_acc_num = input("Enter receiver account number (Try '2001' for Current Account): ")
                target_account = customer.get_account(target_acc_num)

                if not target_account:
                    print("Error: Receiver account not found.")
                    continue

                amount = float(input("Enter transfer amount: Rs. "))
                txn = atm.process_transfer(current_account, target_account, amount)
                print(f"Transfer successful! Transaction ID: {txn.transaction_id}")

            elif choice == "5":
                old_pin = input("Enter current PIN: ")
                new_pin = input("Enter new 4-digit PIN: ")
                if current_account.change_pin(old_pin, new_pin):
                    customer.card.change_pin(old_pin, new_pin)
                    print("PIN changed successfully.")

            elif choice == "6":
                print("\n" + atm.get_mini_statement(current_account))

            elif choice == "7":
                print("Thank you for using the ATM. Goodbye!")
                break

            else:
                print("Invalid option. Please select a number from 1 to 7.")

        except ValueError:
            print("Error: Please enter a valid numerical amount.")
        except (InsufficientBalanceError, InsufficientATMFundsError, InvalidAmountError, InvalidPINError) as e:
            print(f"Transaction Failed: {e}")


def main():
    if "--console" in sys.argv:
        run_console()
    else:
        from gui.app import run_gui
        run_gui()


if __name__ == "__main__":
    main()
