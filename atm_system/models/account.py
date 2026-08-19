from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from atm_system.exceptions import (
    AccountInactiveError,
    FixedDepositLockError,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidPINError,
)


class Account(ABC):
    def __init__(self, account_number: str, holder_name: str, initial_balance: float, pin: str):
        self.account_number = account_number
        self.holder_name = holder_name
        self.__balance = initial_balance
        self.__pin = pin
        self.__is_active = True
        self.transaction_history: list = []
        self.opened_on = datetime.now()

    @abstractmethod
    def account_type(self) -> str:
        pass

    @abstractmethod
    def _validate_withdrawal(self, amount: float) -> None:
        pass

    def get_balance(self) -> float:
        return self.__balance

    def is_active(self) -> bool:
        return self.__is_active

    def block_account(self) -> None:
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

    def deposit(self, amount: float) -> float:
        if not self.__is_active:
            raise AccountInactiveError()
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive.")
        self.__balance += amount
        return self.__balance

    def withdraw(self, amount: float) -> float:
        if not self.__is_active:
            raise AccountInactiveError()
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.")
        self._validate_withdrawal(amount)
        self.__balance -= amount
        return self.__balance

    def account_details(self) -> dict:
        return {
            "number": self.account_number,
            "holder": self.holder_name,
            "type": self.account_type(),
            "balance": self.get_balance(),
            "active": self.is_active(),
            "opened_on": self.opened_on.strftime("%d-%b-%Y"),
        }


class SavingsAccount(Account):
    def __init__(self, account_number: str, holder_name: str, initial_balance: float, pin: str):
        super().__init__(account_number, holder_name, initial_balance, pin)
        self.minimum_balance = 5_000
        self.withdrawal_limit = 50_000
        self.interest_rate = 0.06

    def account_type(self) -> str:
        return "Savings"

    def _validate_withdrawal(self, amount: float) -> None:
        if amount > self.withdrawal_limit:
            raise InvalidAmountError(f"Withdrawal exceeds limit of Rs. {self.withdrawal_limit:,.0f}.")
        if (self.get_balance() - amount) < self.minimum_balance:
            raise InsufficientBalanceError(f"Must maintain minimum balance of Rs. {self.minimum_balance:,.0f}.")

    def account_details(self) -> dict:
        details = super().account_details()
        details.update(
            {
                "minimum_balance": self.minimum_balance,
                "withdrawal_limit": self.withdrawal_limit,
                "interest_rate": f"{self.interest_rate * 100:.1f}% p.a.",
            }
        )
        return details


class CurrentAccount(Account):
    def __init__(self, account_number: str, holder_name: str, initial_balance: float, pin: str):
        super().__init__(account_number, holder_name, initial_balance, pin)
        self.overdraft_limit = 50_000

    def account_type(self) -> str:
        return "Current"

    def _validate_withdrawal(self, amount: float) -> None:
        if (self.get_balance() + self.overdraft_limit) < amount:
            raise InsufficientBalanceError("Withdrawal exceeds overdraft limit.")

    def account_details(self) -> dict:
        details = super().account_details()
        details.update({"overdraft_limit": self.overdraft_limit})
        return details


class FixedDepositAccount(Account):
    def __init__(
        self,
        account_number: str,
        holder_name: str,
        initial_balance: float,
        pin: str,
        lock_months: int = 6,
    ):
        super().__init__(account_number, holder_name, initial_balance, pin)
        self.minimum_deposit = 10_000
        self.interest_rate = 0.08
        self.lock_months = lock_months
        self.maturity_date = datetime.now() + timedelta(days=lock_months * 30)
        self.early_withdrawal_penalty = 0.02

    def account_type(self) -> str:
        return "Fixed Deposit"

    def is_matured(self) -> bool:
        return datetime.now() >= self.maturity_date

    def _validate_withdrawal(self, amount: float) -> None:
        if amount > self.get_balance():
            raise InsufficientBalanceError("Insufficient fixed deposit balance.")

        if not self.is_matured():
            penalty = amount * self.early_withdrawal_penalty
            if (self.get_balance() - amount - penalty) < 0:
                raise InsufficientBalanceError("Insufficient balance after early withdrawal penalty.")
            raise FixedDepositLockError(
                f"FD matures on {self.maturity_date.strftime('%d-%b-%Y')}. "
                f"Early withdrawal penalty: {self.early_withdrawal_penalty * 100:.0f}%."
            )

    def force_early_withdrawal(self, amount: float) -> float:
        if not self.__is_active:
            raise AccountInactiveError()
        if amount <= 0 or amount > self.get_balance():
            raise InvalidAmountError("Invalid withdrawal amount.")

        penalty = amount * self.early_withdrawal_penalty
        self.__balance -= amount + penalty
        return self.__balance

    def account_details(self) -> dict:
        details = super().account_details()
        details.update(
            {
                "interest_rate": f"{self.interest_rate * 100:.1f}% p.a.",
                "maturity_date": self.maturity_date.strftime("%d-%b-%Y"),
                "is_matured": self.is_matured(),
                "lock_months": self.lock_months,
            }
        )
        return details
