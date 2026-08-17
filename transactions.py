# transactions.py
import datetime
import random
from abc import ABC, abstractmethod

class Transaction(ABC):
    def __init__(self, account, amount: float):
        # Generating a random transaction ID like TXN-10234
        self.transaction_id = f"TXN-{random.randint(10000, 99999)}"
        self.amount = amount
        self.date_time = datetime.datetime.now()
        self.account = account
        self.status = "SUCCESS"

    @abstractmethod
    def format_for_statement(self) -> str:
        """Abstract method to ensure every transaction type formats itself for the mini statement."""
        pass

class DepositTransaction(Transaction):
    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Deposit    +{self.amount:,.2f}"

class WithdrawalTransaction(Transaction):
    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Withdrawal -{self.amount:,.2f}"

class TransferTransaction(Transaction):
    def __init__(self, account, amount: float, target_account):
        super().__init__(account, amount)
        self.target_account = target_account

    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Transfer   -{self.amount:,.2f}"