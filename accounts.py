# accounts.py
from abc import ABC, abstractmethod
from exceptions import (
    InsufficientBalanceError, InvalidAmountError, 
    AccountInactiveError, InvalidPINError
)

class Account(ABC):
    def __init__(self, account_number: str, holder_name: str, initial_balance: float, pin: str):
        self.account_number = account_number
        self.holder_name = holder_name
        # Encapsulated attributes
        self.__balance = initial_balance
        self.__pin = pin
        self.__is_active = True
        self.transaction_history = []

    def get_balance(self) -> float:
        return self.__balance

    def is_active(self) -> bool:
        return self.__is_active
        
    def block_account(self):
        self.__is_active = False

    def validate_pin(self, entered_pin: str) -> bool:
        if entered_pin != self.__pin:
            raise InvalidPINError("Account PIN is incorrect.")
        return True

    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        if self.validate_pin(old_pin):
            self.__pin = new_pin
            return True
        return False

    def deposit(self, amount: float):
        if not self.__is_active:
            raise AccountInactiveError()
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive.")
        
        self.__balance += amount
        return self.__balance

    def withdraw(self, amount: float):
        if not self.__is_active:
            raise AccountInactiveError()
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.")
        
        # Polymorphic validation step: defers to the child classes
        self._validate_withdrawal(amount)
        
        self.__balance -= amount
        return self.__balance

    @abstractmethod
    def _validate_withdrawal(self, amount: float):
        """Abstract method to be implemented by child classes for custom withdrawal logic."""
        pass


class SavingsAccount(Account):
    def __init__(self, account_number: str, holder_name: str, initial_balance: float, pin: str):
        super().__init__(account_number, holder_name, initial_balance, pin)
        self.minimum_balance = 5000
        self.withdrawal_limit = 50000

    def _validate_withdrawal(self, amount: float):
        if amount > self.withdrawal_limit:
            raise InvalidAmountError(f"Withdrawal exceeds per-transaction limit of {self.withdrawal_limit}.")
        if (self.get_balance() - amount) < self.minimum_balance:
            raise InsufficientBalanceError(f"Must maintain minimum balance of {self.minimum_balance}.")


class CurrentAccount(Account):
    def __init__(self, account_number: str, holder_name: str, initial_balance: float, pin: str):
        super().__init__(account_number, holder_name, initial_balance, pin)
        self.overdraft_limit = 50000

    def _validate_withdrawal(self, amount: float):
        if (self.get_balance() + self.overdraft_limit) < amount:
            raise InsufficientBalanceError("Withdrawal exceeds overdraft limit.")