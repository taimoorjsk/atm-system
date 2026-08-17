# main.py
from entities import Card, Customer
from accounts import SavingsAccount, CurrentAccount
from atm import ATM
from exceptions import (
    CardBlockedError, InvalidPINError, InsufficientBalanceError,
    InsufficientATMFundsError, InvalidAmountError
)

def setup_dummy_data():
    # Create an ATM with default cash inventory
    my_atm = ATM(location="Main Branch")
    
    # Create a Card (Default PIN: 1234)
    my_card = Card(pin="1234")
    
    # Create a Customer
    customer = Customer(customer_id="C-001", name="Test User", contact="test@email.com", card=my_card)
    
    # Create Accounts (Using the subclasses to demonstrate polymorphism)
    savings = SavingsAccount(account_number="1001", holder_name="Test User", initial_balance=25000, pin="1234")
    current = CurrentAccount(account_number="2001", holder_name="Test User", initial_balance=10000, pin="1234")
    
    # Link Accounts to the Customer
    customer.add_account(savings)
    customer.add_account(current)
    
    return my_atm, customer

def main():
    atm, customer = setup_dummy_data()
    print("Welcome to the ATM System")
    
    # Authentication Loop
    authenticated = False
    while not authenticated:
        try:
            entered_pin = input("Please enter your 4-digit PIN: ")
            # Validates the card PIN; throws exceptions if wrong or blocked
            if customer.card.validate_pin(entered_pin):
                authenticated = True
                print("\nAuthentication Successful!")
        except (InvalidPINError, CardBlockedError) as e:
            print(f"Error: {e}")
            if isinstance(e, CardBlockedError):
                return # Exit the program if the card gets blocked

    # For simplicity in this menu, we default to the Savings Account.
    # The advanced challenge allows letting the user select an account first.
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
            if choice == '1':
                print(f"Current Balance: Rs. {current_account.get_balance():,.2f}")
                
            elif choice == '2':
                amount = float(input("Enter deposit amount: Rs. "))
                txn = atm.process_deposit(current_account, amount)
                print(f"Success! Transaction ID: {txn.transaction_id}")
                print(f"New Balance: Rs. {current_account.get_balance():,.2f}")
                
            elif choice == '3':
                amount = float(input("Enter withdrawal amount (Multiples of 500): Rs. "))
                txn = atm.process_withdrawal(current_account, amount)
                print(f"Please collect your cash. Transaction ID: {txn.transaction_id}")
                print(f"Remaining Balance: Rs. {current_account.get_balance():,.2f}")
                
            elif choice == '4':
                target_acc_num = input("Enter receiver account number (Try '2001' for Current Account): ")
                target_account = customer.get_account(target_acc_num)
                
                if not target_account:
                    print("Error: Receiver account not found.")
                    continue
                    
                amount = float(input("Enter transfer amount: Rs. "))
                txn = atm.process_transfer(current_account, target_account, amount)
                print(f"Transfer successful! Transaction ID: {txn.transaction_id}")
                
            elif choice == '5':
                old_pin = input("Enter current PIN: ")
                new_pin = input("Enter new 4-digit PIN: ")
                if current_account.change_pin(old_pin, new_pin):
                    customer.card.change_pin(old_pin, new_pin)
                    print("PIN changed successfully.")
                    
            elif choice == '6':
                print("\n" + atm.get_mini_statement(current_account))
                
            elif choice == '7':
                print("Thank you for using the ATM. Goodbye!")
                break
                
            else:
                print("Invalid option. Please select a number from 1 to 7.")
                
        except ValueError:
            print("Error: Please enter a valid numerical amount.")
        except (InsufficientBalanceError, InsufficientATMFundsError, InvalidAmountError, InvalidPINError) as e:
            # Catching all our custom business logic errors cleanly
            print(f"Transaction Failed: {e}")

if __name__ == "__main__":
    main()