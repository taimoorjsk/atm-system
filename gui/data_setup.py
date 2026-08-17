"""Dummy data factory — mirrors the original console main.py setup."""

from entities import Card, Customer
from accounts import SavingsAccount, CurrentAccount
from atm import ATM


def setup_dummy_data():
    """Create and wire up an ATM, customer, card, and linked accounts."""
    my_atm = ATM(location="Main Branch")
    my_card = Card(pin="1234")

    customer = Customer(
        customer_id="C-001",
        name="Test User",
        contact="test@email.com",
        card=my_card,
    )

    savings = SavingsAccount(
        account_number="1001",
        holder_name="Test User",
        initial_balance=25000,
        pin="1234",
    )
    current = CurrentAccount(
        account_number="2001",
        holder_name="Test User",
        initial_balance=10000,
        pin="1234",
    )

    customer.add_account(savings)
    customer.add_account(current)

    return my_atm, customer
