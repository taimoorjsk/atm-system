import random
from abc import ABC, abstractmethod
from datetime import datetime


class Transaction(ABC):
    _counter = 10000

    def __init__(self, account, amount: float, description: str = ""):
        Transaction._counter += 1
        self.transaction_id = f"TXN-{Transaction._counter}"
        self.amount = amount
        self.date_time = datetime.now()
        self.account = account
        self.status = "SUCCESS"
        self.description = description

    @abstractmethod
    def transaction_type(self) -> str:
        pass

    @abstractmethod
    def format_for_statement(self) -> str:
        pass

    def to_receipt_line(self) -> str:
        return (
            f"{self.transaction_id} | {self.transaction_type()} | "
            f"Rs. {self.amount:,.2f} | {self.date_time.strftime('%d-%b-%Y %H:%M')}"
        )


class DepositTransaction(Transaction):
    def transaction_type(self) -> str:
        return "Deposit"

    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Deposit    +{self.amount:,.2f}"


class WithdrawalTransaction(Transaction):
    def __init__(self, account, amount: float, notes_dispensed: dict | None = None):
        super().__init__(account, amount)
        self.notes_dispensed = notes_dispensed or {}

    def transaction_type(self) -> str:
        return "Withdrawal"

    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Withdrawal -{self.amount:,.2f}"


class TransferTransaction(Transaction):
    def __init__(self, account, amount: float, target_account, target_holder: str = ""):
        super().__init__(account, amount, description=f"To {target_account.account_number}")
        self.target_account = target_account
        self.target_holder = target_holder or target_account.holder_name

    def transaction_type(self) -> str:
        return "Transfer"

    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Transfer   -{self.amount:,.2f} -> {self.target_account.account_number}"


class BillPaymentTransaction(Transaction):
    def __init__(self, account, amount: float, biller: str, consumer_id: str):
        super().__init__(account, amount, description=f"{biller} ({consumer_id})")
        self.biller = biller
        self.consumer_id = consumer_id

    def transaction_type(self) -> str:
        return "Bill Pay"

    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Bill Pay   -{self.amount:,.2f} {self.biller}"


class ReceivedTransferTransaction(Transaction):
    def __init__(self, account, amount: float, sender_account: str, sender_holder: str):
        super().__init__(account, amount, description=f"From {sender_account}")
        self.sender_account = sender_account
        self.sender_holder = sender_holder

    def transaction_type(self) -> str:
        return "Received"

    def format_for_statement(self) -> str:
        date_str = self.date_time.strftime("%d-%b")
        return f"{date_str:<10} Received   +{self.amount:,.2f} <- {self.sender_account}"
