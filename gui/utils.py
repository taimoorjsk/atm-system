"""Shared GUI helpers — exception popups and formatting."""

import customtkinter as ctk
from tkinter import messagebox

from exceptions import (
    CardBlockedError,
    InvalidPINError,
    InsufficientBalanceError,
    InsufficientATMFundsError,
    InvalidAmountError,
    AccountInactiveError,
)


def format_currency(amount: float) -> str:
    return f"Rs. {amount:,.2f}"


def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)


def show_success(title: str, message: str) -> None:
    messagebox.showinfo(title, message)


def show_warning(title: str, message: str) -> None:
    messagebox.showwarning(title, message)


def handle_transaction_error(exc: Exception) -> None:
    """Map backend exceptions to user-friendly popup messages."""
    if isinstance(exc, InvalidPINError):
        show_error("Invalid PIN", str(exc))
    elif isinstance(exc, CardBlockedError):
        show_error("Card Blocked", str(exc))
    elif isinstance(exc, InsufficientBalanceError):
        show_error("Insufficient Balance", str(exc))
    elif isinstance(exc, InsufficientATMFundsError):
        show_error("ATM Out of Cash", str(exc))
    elif isinstance(exc, InvalidAmountError):
        show_error("Invalid Amount", str(exc))
    elif isinstance(exc, AccountInactiveError):
        show_error("Account Inactive", str(exc))
    elif isinstance(exc, ValueError):
        show_error("Invalid Input", "Please enter a valid numerical amount.")
    else:
        show_error("Error", str(exc))


def account_type_label(account) -> str:
    """Return a readable account type name from the class."""
    return type(account).__name__.replace("Account", " Account")
