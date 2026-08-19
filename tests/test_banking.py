import unittest

from banking import BankService
from database import Database
from exceptions import (
    AccountClosedError,
    CardBlockedError,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidPINError,
)


class BankingServiceTests(unittest.TestCase):
    def setUp(self):
        self.bank = BankService(Database(":memory:"))
        self.account = self.bank.create_account(
            "Alice Example",
            "03001234567",
            "alice@example.com",
            "Lahore",
            "Current",
            10_000,
            "1234",
            "1234",
        )
        self.receiver = self.bank.create_account(
            "Bob Example",
            "03007654321",
            "bob@example.com",
            "Karachi",
            "Current",
            5_000,
            "5678",
            "5678",
        )

    def tearDown(self):
        self.bank.database.close()

    def test_account_creation_and_hashed_pin(self):
        self.assertTrue(self.bank.database.verify_pin(self.account, "1234"))
        self.assertFalse(self.bank.database.verify_pin(self.account, "9999"))
        self.assertEqual(self.bank.database.get_account(self.account)["account_type"], "Current")

    def test_invalid_pin_locks_after_three_attempts(self):
        for _ in range(2):
            with self.assertRaises(InvalidPINError):
                self.bank.authenticate(self.account, "0000")
        with self.assertRaises(CardBlockedError):
            self.bank.authenticate(self.account, "0000")
        with self.assertRaises(CardBlockedError):
            self.bank.authenticate(self.account, "1234")

    def test_deposit_withdraw_transfer_and_history(self):
        self.bank.deposit(self.account, 1_000)
        self.bank.withdraw(self.account, 500)
        self.bank.transfer(self.account, self.receiver, 1_000)
        self.assertEqual(self.bank.database.get_account(self.account)["balance"], 9_500)
        self.assertEqual(self.bank.database.get_account(self.receiver)["balance"], 6_000)
        self.assertEqual(len(self.bank.transactions(self.account, None)), 3)
        self.assertEqual(len(self.bank.transactions(self.receiver, None)), 1)

    def test_invalid_amount_and_insufficient_funds(self):
        with self.assertRaises(InvalidAmountError):
            self.bank.deposit(self.account, 0)
        with self.assertRaises(InsufficientBalanceError):
            self.bank.withdraw(self.account, 65_000)

    def test_account_closure_is_soft(self):
        self.bank.withdraw(self.account, 10_000)
        self.bank.close_account(self.account, "1234")
        self.assertEqual(self.bank.database.get_account(self.account)["status"], "CLOSED")
        with self.assertRaises(AccountClosedError):
            self.bank.authenticate(self.account, "1234")
        self.assertEqual(len(self.bank.transactions(self.account, None)), 1)


if __name__ == "__main__":
    unittest.main()
