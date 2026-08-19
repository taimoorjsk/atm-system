from atm_system.models.account import CurrentAccount, FixedDepositAccount, SavingsAccount
from atm_system.models.card import Card
from atm_system.models.customer import Customer
from atm_system.services.atm_service import ATMService
from atm_system.services.audit_log import AuditLog
from atm_system.services.bank_registry import BankRegistry


def build_system():
    registry = BankRegistry()
    audit_log = AuditLog()
    atm = ATMService(atm_id="ATM-001", location="Main Branch — Karachi", registry=registry, audit_log=audit_log)

    taimoor = Customer(
        customer_id="C-001",
        name="M. Taimoor Jahangir",
        contact="taimoor@email.com",
        card=Card(card_number="4532123456789012", pin="1234"),
    )
    taimoor.add_account(SavingsAccount("1001", "M. Taimoor Jahangir", 75_000, "1234"))
    taimoor.add_account(CurrentAccount("2001", "M. Taimoor Jahangir", 25_000, "1234"))
    taimoor.add_account(FixedDepositAccount("3001", "M. Taimoor Jahangir", 100_000, "1234", lock_months=6))

    ali = Customer(
        customer_id="C-002",
        name="Ali Ahmed",
        contact="ali@email.com",
        card=Card(card_number="5420987654321098", pin="5678"),
    )
    ali.add_account(SavingsAccount("4001", "Ali Ahmed", 40_000, "5678"))

    registry.register_customer(taimoor)
    registry.register_customer(ali)

    return atm, registry, taimoor


def build_demo_customer():
    atm, registry, customer = build_system()
    return atm, customer, registry
