# atm.py
from exceptions import InsufficientATMFundsError, InvalidAmountError
from transactions import WithdrawalTransaction, DepositTransaction, TransferTransaction

class ATM:
    def __init__(self, location: str):
        self.location = location
        # ATM's internal cash inventory
        self.cash_inventory = {
            5000: 10,
            1000: 20,
            500: 20
        }
        self.daily_withdrawal_limit = 100000

    def get_total_cash(self) -> float:
        return sum(denom * count for denom, count in self.cash_inventory.items())

    def _can_dispense(self, amount: float) -> bool:
        """Greedy algorithm to check if the ATM can dispense the requested amount with available notes."""
        if amount % 500 != 0:
            raise InvalidAmountError("Amount must be a multiple of 500.")
            
        remaining_amount = amount
        # Temporary dictionary to track notes to dispense without modifying actual inventory yet
        notes_to_dispense = {5000: 0, 1000: 0, 500: 0}

        # Sort denominations highest to lowest
        for denom in sorted(self.cash_inventory.keys(), reverse=True):
            if remaining_amount == 0:
                break
                
            # How many notes of this denomination do we need?
            notes_needed = int(remaining_amount // denom)
            # How many can we actually give?
            notes_available = self.cash_inventory[denom]
            notes_to_give = min(notes_needed, notes_available)

            notes_to_dispense[denom] = notes_to_give
            remaining_amount -= notes_to_give * denom

        if remaining_amount > 0:
            raise InsufficientATMFundsError()
            
        return notes_to_dispense

    def process_withdrawal(self, account, amount: float):
        # 1. Check if ATM has the physical cash notes available
        notes_to_dispense = self._can_dispense(amount)
        
        # 2. Let the Account object validate rules (balances, overdrafts, limits)
        account.withdraw(amount)
        
        # 3. Deduct from ATM physical inventory
        for denom, count in notes_to_dispense.items():
            self.cash_inventory[denom] -= count
            
        # 4. Log the transaction
        txn = WithdrawalTransaction(account, amount)
        account.transaction_history.append(txn)
        return txn

    def process_deposit(self, account, amount: float):
        account.deposit(amount)
        txn = DepositTransaction(account, amount)
        account.transaction_history.append(txn)
        return txn

    def process_transfer(self, sender_account, receiver_account, amount: float):
        # Withdraw from sender (this handles balance checks)
        sender_account.withdraw(amount)
        # Deposit to receiver
        receiver_account.deposit(amount)
        
        # Log transaction for sender
        txn = TransferTransaction(sender_account, amount, receiver_account)
        sender_account.transaction_history.append(txn)
        return txn

    def get_mini_statement(self, account) -> str:
        # The assignment asks for the last 5 transactions
        recent_txns = account.transaction_history[-5:]
        
        statement = f"========== MINI STATEMENT ==========\n"
        statement += f"Account: {account.account_number}\n"
        statement += f"{'Date':<10} {'Type':<12} {'Amount'}\n"
        statement += "-" * 36 + "\n"
        
        # Displaying transactions in reverse order (newest first)
        for txn in reversed(recent_txns):
            statement += f"{txn.format_for_statement()}\n"
            
        statement += f"Current Balance: Rs. {account.get_balance():,.2f}\n"
        return statement