from atm_system.models.account import Account


class Customer:
    def __init__(self, customer_id: str, name: str, contact: str, card):
        self.customer_id = customer_id
        self.name = name
        self.contact = contact
        self.card = card
        self.accounts: dict[str, Account] = {}

    def add_account(self, account: Account) -> None:
        self.accounts[account.account_number] = account

    def get_account(self, account_number: str) -> Account | None:
        return self.accounts.get(account_number)

    def get_total_balance(self) -> float:
        return sum(account.get_balance() for account in self.accounts.values())

    def account_summary(self) -> list[dict]:
        rows = []
        for account in self.accounts.values():
            rows.append(
                {
                    "number": account.account_number,
                    "type": account.account_type(),
                    "balance": account.get_balance(),
                    "active": account.is_active(),
                }
            )
        return rows
