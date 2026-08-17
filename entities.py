# entities.py
from exceptions import CardBlockedError, InvalidPINError

class Card:
    def __init__(self, pin: str):
        # Encapsulating sensitive data
        self.__pin = pin
        self.__is_blocked = False
        self.__failed_attempts = 0

    def is_blocked(self) -> bool:
        return self.__is_blocked

    def validate_pin(self, entered_pin: str) -> bool:
        if self.__is_blocked:
            raise CardBlockedError()
        
        if entered_pin == self.__pin:
            self.__failed_attempts = 0  # Reset on success
            return True
        else:
            self.__failed_attempts += 1
            if self.__failed_attempts >= 3:
                self.__is_blocked = True
                raise CardBlockedError("Maximum attempts reached. Card is now blocked.")
            
            # Using the custom exception we built earlier
            raise InvalidPINError(f"Invalid PIN. Attempts remaining: {3 - self.__failed_attempts}")

    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        # Validate the old PIN before allowing a change
        if self.validate_pin(old_pin):
            self.__pin = new_pin
            return True
        return False

class Customer:
    def __init__(self, customer_id: str, name: str, contact: str, card: Card):
        self.customer_id = customer_id
        self.name = name
        self.contact = contact
        self.card = card
        # Using a dictionary to store accounts, keyed by account number for quick lookups
        self.accounts = {} 

    def add_account(self, account):
        self.accounts[account.account_number] = account

    def get_account(self, account_number: str):
        return self.accounts.get(account_number)