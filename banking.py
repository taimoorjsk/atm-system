"""Application service for persistent account and transaction workflows."""

from __future__ import annotations

import re

from accounts import CurrentAccount, SavingsAccount
from atm import ATM
from database import Database
from exceptions import (
    AccountClosedError,
    AccountNotFoundError,
    CardBlockedError,
    InvalidAccountError,
    InvalidAmountError,
    InvalidPINError,
)


class BankService:
    """Coordinates SQLite state with the existing account and ATM objects."""

    MAX_PIN_ATTEMPTS = 3

    def __init__(self, database: Database | None = None, atm: ATM | None = None):
        self.database = database or Database()
        self.atm = atm or ATM(location="Main Branch")

    def create_account(
        self,
        name: str,
        phone: str,
        email: str,
        address: str,
        account_type: str,
        initial_deposit: float,
        pin: str,
        confirm_pin: str,
    ) -> str:
        name = name.strip()
        phone = phone.strip()
        email = email.strip()
        address = address.strip()
        account_type = account_type.strip().title()

        if not name:
            raise InvalidAccountError("Name cannot be empty.")
        if not phone or not re.fullmatch(r"[0-9+() -]{7,20}", phone):
            raise InvalidAccountError("Enter a valid phone number.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise InvalidAccountError("Enter a valid email address.")
        if account_type not in {"Savings", "Current"}:
            raise InvalidAccountError("Account type must be Savings or Current.")
        if initial_deposit < 0:
            raise InvalidAmountError("Initial deposit cannot be negative.")
        if account_type == "Savings" and initial_deposit < 5_000:
            raise InvalidAmountError("Savings accounts require a minimum opening balance of Rs. 5,000.")
        if not pin.isdigit() or len(pin) != 4:
            raise InvalidPINError("PIN must contain exactly 4 digits.")
        if pin != confirm_pin:
            raise InvalidPINError("PIN and confirmation do not match.")

        customer_id = self.database.add_customer(name, phone, email, address)
        account_number = self.database.next_account_number()
        self.database.add_account(account_number, customer_id, account_type, initial_deposit, pin)
        return account_number

    def authenticate(self, account_number: str, pin: str):
        account = self.database.get_account(account_number.strip())
        if not account:
            raise AccountNotFoundError("Account number was not found.")
        if account["status"] != "ACTIVE":
            raise AccountClosedError("This account is closed and cannot be accessed.")
        if self.database.is_blocked(account_number):
            raise CardBlockedError()
        if not self.database.verify_pin(account_number, pin):
            attempts = self.database.register_failed_pin_attempt(
                account_number, self.MAX_PIN_ATTEMPTS
            )
            if self.database.is_blocked(account_number):
                raise CardBlockedError("Maximum attempts reached. Account is now blocked.")
            raise InvalidPINError(
                f"Invalid PIN. Attempts remaining: {self.MAX_PIN_ATTEMPTS - attempts}"
            )
        self.database.reset_pin_attempts(account_number)
        return account

    def _load_account(self, account_number: str):
        row = self.database.get_account(account_number)
        if not row:
            raise AccountNotFoundError("Account number was not found.")
        if row["status"] != "ACTIVE":
            raise AccountClosedError("This account is closed.")
        account_class = SavingsAccount if row["account_type"] == "Savings" else CurrentAccount
        return account_class(row["account_number"], row["name"], row["balance"], "0000"), row

    def deposit(self, account_number: str, amount: float):
        account, _ = self._load_account(account_number)
        txn = self.atm.process_deposit(account, amount)
        self.database.update_balance(account_number, account.get_balance())
        txn.transaction_id = self.database.record_transaction(account_number, "DEPOSIT", amount, "Cash deposit")
        return txn

    def withdraw(self, account_number: str, amount: float):
        account, _ = self._load_account(account_number)
        txn = self.atm.process_withdrawal(account, amount)
        self.database.update_balance(account_number, account.get_balance())
        txn.transaction_id = self.database.record_transaction(account_number, "WITHDRAWAL", amount, "ATM cash withdrawal")
        return txn

    def transfer(self, source_number: str, target_number: str, amount: float):
        if source_number == target_number:
            raise InvalidAccountError("Cannot transfer to the same account.")
        source, _ = self._load_account(source_number)
        target, _ = self._load_account(target_number)
        txn = self.atm.process_transfer(source, target, amount)
        self.database.update_balance(source_number, source.get_balance())
        self.database.update_balance(target_number, target.get_balance())
        txn.transaction_id = self.database.record_transaction(
            source_number, "TRANSFER", amount, "Transfer to account", target_number
        )
        self.database.record_transaction(
            target_number, "TRANSFER_IN", amount, "Transfer received", source_number
        )
        return txn

    def close_account(self, account_number: str, pin: str) -> None:
        account = self.authenticate(account_number, pin)
        if account["balance"] != 0:
            raise InvalidAmountError("Account balance must be zero before closing.")
        self.database.update_account_status(account_number, "CLOSED")

    def update_profile(self, account_number: str, name: str, phone: str, email: str, address: str) -> None:
        account = self.database.get_account(account_number)
        if not account:
            raise AccountNotFoundError("Account number was not found.")
        if not name.strip():
            raise InvalidAccountError("Name cannot be empty.")
        if not re.fullmatch(r"[0-9+() -]{7,20}", phone.strip()):
            raise InvalidAccountError("Enter a valid phone number.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            raise InvalidAccountError("Enter a valid email address.")
        self.database.update_customer(
            account["customer_id"], name.strip(), phone.strip(), email.strip(), address.strip()
        )

    def change_pin(self, account_number: str, old_pin: str, new_pin: str, confirm_pin: str) -> None:
        self.authenticate(account_number, old_pin)
        if not new_pin.isdigit() or len(new_pin) != 4:
            raise InvalidPINError("PIN must contain exactly 4 digits.")
        if new_pin != confirm_pin:
            raise InvalidPINError("PIN and confirmation do not match.")
        self.database.update_pin(account_number, new_pin)

    def transactions(self, account_number: str, limit: int | None = 5):
        if not self.database.get_account(account_number):
            raise AccountNotFoundError("Account number was not found.")
        return self.database.get_transactions(account_number, limit)
