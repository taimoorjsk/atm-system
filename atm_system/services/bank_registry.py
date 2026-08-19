from atm_system.models.account import Account
from atm_system.models.customer import Customer


class BankRegistry:
    """Central lookup for accounts across all registered customers."""

    def __init__(self):
        self._customers: dict[str, Customer] = {}
        self._accounts: dict[str, Account] = {}

    def register_customer(self, customer: Customer) -> None:
        self._customers[customer.customer_id] = customer
        for account in customer.accounts.values():
            self._accounts[account.account_number] = account

    def find_account(self, account_number: str) -> Account | None:
        return self._accounts.get(account_number)

    def find_account_owner(self, account_number: str) -> Customer | None:
        account = self.find_account(account_number)
        if not account:
            return None
        for customer in self._customers.values():
            if account_number in customer.accounts:
                return customer
        return None

    def get_customer(self, customer_id: str) -> Customer | None:
        return self._customers.get(customer_id)

    def all_account_numbers(self) -> list[str]:
        return list(self._accounts.keys())
