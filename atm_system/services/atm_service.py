from datetime import date

from atm_system.config import (
    ATM_DAILY_WITHDRAWAL_LIMIT,
    DEFAULT_CASH_INVENTORY,
    FULL_STATEMENT_SIZE,
    MINI_STATEMENT_SIZE,
    WITHDRAWAL_NOTE_STEP,
)
from atm_system.exceptions import (
    BillPaymentError,
    DailyLimitExceededError,
    FixedDepositLockError,
    InsufficientATMFundsError,
    InvalidAccountError,
    InvalidAmountError,
)
from atm_system.models.account import FixedDepositAccount
from atm_system.models.transaction import (
    BillPaymentTransaction,
    DepositTransaction,
    ReceivedTransferTransaction,
    TransferTransaction,
    WithdrawalTransaction,
)
from atm_system.services.audit_log import AuditLog, TransactionResult
from atm_system.services.bank_registry import BankRegistry


class ATMService:
    BILLERS = {
        "K-Electric": {"prefix": "KE", "min": 500, "max": 50_000},
        "SSGC Gas": {"prefix": "SG", "min": 500, "max": 30_000},
        "PTCL Internet": {"prefix": "PT", "min": 1_000, "max": 20_000},
    }

    def __init__(self, atm_id: str, location: str, registry: BankRegistry, audit_log: AuditLog | None = None):
        self.atm_id = atm_id
        self.location = location
        self.registry = registry
        self.audit_log = audit_log or AuditLog()
        self.cash_inventory = dict(DEFAULT_CASH_INVENTORY)
        self.daily_withdrawal_limit = ATM_DAILY_WITHDRAWAL_LIMIT
        self._daily_withdrawn: dict[str, float] = {}
        self._last_reset = date.today()

    def get_total_cash(self) -> float:
        return sum(denom * count for denom, count in self.cash_inventory.items())

    def get_remaining_daily_limit(self, customer_id: str) -> float:
        self._reset_daily_limits_if_needed()
        used = self._daily_withdrawn.get(customer_id, 0)
        return max(0, self.daily_withdrawal_limit - used)

    def _reset_daily_limits_if_needed(self) -> None:
        today = date.today()
        if today != self._last_reset:
            self._daily_withdrawn.clear()
            self._last_reset = today

    def _track_withdrawal(self, customer_id: str, amount: float) -> None:
        self._reset_daily_limits_if_needed()
        used = self._daily_withdrawn.get(customer_id, 0) + amount
        if used > self.daily_withdrawal_limit:
            raise DailyLimitExceededError(
                f"Daily limit is Rs. {self.daily_withdrawal_limit:,.0f}. "
                f"Remaining today: Rs. {self.get_remaining_daily_limit(customer_id):,.0f}."
            )
        self._daily_withdrawn[customer_id] = used

    def _can_dispense(self, amount: float) -> dict[int, int]:
        if amount % WITHDRAWAL_NOTE_STEP != 0:
            raise InvalidAmountError(f"Amount must be a multiple of Rs. {WITHDRAWAL_NOTE_STEP}.")

        remaining = amount
        notes = {denom: 0 for denom in self.cash_inventory}

        for denom in sorted(self.cash_inventory.keys(), reverse=True):
            if remaining == 0:
                break
            needed = int(remaining // denom)
            give = min(needed, self.cash_inventory[denom])
            notes[denom] = give
            remaining -= give * denom

        if remaining > 0:
            raise InsufficientATMFundsError()

        return notes

    def _dispense_notes(self, notes: dict[int, int]) -> None:
        for denom, count in notes.items():
            self.cash_inventory[denom] -= count

    def process_deposit(self, account, amount: float, customer_id: str | None = None) -> TransactionResult:
        account.deposit(amount)
        txn = DepositTransaction(account, amount)
        account.transaction_history.append(txn)
        self.audit_log.record("DEPOSIT", f"{txn.transaction_id} Rs.{amount:,.0f} -> {account.account_number}", customer_id)
        return TransactionResult(txn, "Deposit successful.", account.get_balance())

    def process_withdrawal(
        self, account, amount: float, customer_id: str, confirm_fd_penalty: bool = False
    ) -> TransactionResult:
        self._track_withdrawal(customer_id, amount)

        if isinstance(account, FixedDepositAccount) and not account.is_matured():
            if not confirm_fd_penalty:
                raise FixedDepositLockError(
                    f"FD matures {account.maturity_date.strftime('%d-%b-%Y')}. "
                    "Confirm early withdrawal to apply 2% penalty."
                )
            penalty = amount * account.early_withdrawal_penalty
            account.force_early_withdrawal(amount)
            notes = self._can_dispense(amount)
            self._dispense_notes(notes)
            txn = WithdrawalTransaction(account, amount + penalty, notes)
            account.transaction_history.append(txn)
            msg = f"Early FD withdrawal. Penalty: Rs. {penalty:,.0f}."
        else:
            notes = self._can_dispense(amount)
            account.withdraw(amount)
            self._dispense_notes(notes)
            txn = WithdrawalTransaction(account, amount, notes)
            account.transaction_history.append(txn)
            msg = "Please collect your cash."

        self.audit_log.record(
            "WITHDRAWAL",
            f"{txn.transaction_id} Rs.{amount:,.0f} from {account.account_number}",
            customer_id,
        )
        return TransactionResult(txn, msg, account.get_balance(), notes)

    def process_transfer(
        self, sender, receiver, amount: float, customer_id: str | None = None
    ) -> TransactionResult:
        if sender.account_number == receiver.account_number:
            raise InvalidAccountError("Cannot transfer to the same account.")

        sender.withdraw(amount)
        receiver.deposit(amount)

        out_txn = TransferTransaction(sender, amount, receiver, receiver.holder_name)
        in_txn = ReceivedTransferTransaction(receiver, amount, sender.account_number, sender.holder_name)

        sender.transaction_history.append(out_txn)
        receiver.transaction_history.append(in_txn)

        self.audit_log.record(
            "TRANSFER",
            f"{out_txn.transaction_id} Rs.{amount:,.0f} {sender.account_number} -> {receiver.account_number}",
            customer_id,
        )
        return TransactionResult(out_txn, "Transfer completed.", sender.get_balance())

    def process_bill_payment(
        self, account, biller: str, consumer_id: str, amount: float, customer_id: str | None = None
    ) -> TransactionResult:
        if biller not in self.BILLERS:
            raise BillPaymentError("Unknown biller.")

        rules = self.BILLERS[biller]
        if not consumer_id.startswith(rules["prefix"]):
            raise BillPaymentError(f"Consumer ID must start with '{rules['prefix']}'.")
        if amount < rules["min"] or amount > rules["max"]:
            raise BillPaymentError(f"Amount must be between Rs. {rules['min']:,} and Rs. {rules['max']:,}.")

        account.withdraw(amount)
        txn = BillPaymentTransaction(account, amount, biller, consumer_id)
        account.transaction_history.append(txn)

        self.audit_log.record(
            "BILL_PAY",
            f"{txn.transaction_id} {biller} Rs.{amount:,.0f} ({consumer_id})",
            customer_id,
        )
        return TransactionResult(txn, f"Bill paid to {biller}.", account.get_balance())

    def get_statement(self, account, full: bool = False) -> str:
        limit = FULL_STATEMENT_SIZE if full else MINI_STATEMENT_SIZE
        recent = account.transaction_history[-limit:]

        title = "FULL STATEMENT" if full else "MINI STATEMENT"
        lines = [
            "=" * 44,
            title,
            "=" * 44,
            f"Account : {account.account_number} ({account.account_type()})",
            f"Holder  : {account.holder_name}",
            f"{'Date':<10} {'Type':<12} {'Amount / Detail'}",
            "-" * 44,
        ]

        for txn in reversed(recent):
            lines.append(txn.format_for_statement())

        lines.append("-" * 44)
        lines.append(f"Current Balance: Rs. {account.get_balance():,.2f}")
        return "\n".join(lines)

    def cash_inventory_report(self) -> str:
        lines = ["ATM Cash Inventory", "-" * 28]
        for denom in sorted(self.cash_inventory.keys(), reverse=True):
            count = self.cash_inventory[denom]
            lines.append(f"Rs. {denom:>5} x {count:<3} = Rs. {denom * count:>10,}")
        lines.append("-" * 28)
        lines.append(f"Total Available: Rs. {self.get_total_cash():,.0f}")
        return "\n".join(lines)

    def format_receipt(self, result: TransactionResult) -> str:
        txn = result.transaction
        lines = [
            "=" * 40,
            "TRANSACTION RECEIPT",
            "=" * 40,
            f"ID      : {txn.transaction_id}",
            f"Type    : {txn.transaction_type()}",
            f"Amount  : Rs. {txn.amount:,.2f}",
            f"Time    : {txn.date_time.strftime('%d-%b-%Y %H:%M:%S')}",
            f"Account : {txn.account.account_number}",
            f"Status  : {txn.status}",
        ]
        if result.notes_dispensed:
            lines.append("-" * 40)
            lines.append("Notes Dispensed:")
            for denom, count in sorted(result.notes_dispensed.items(), reverse=True):
                if count:
                    lines.append(f"  Rs. {denom} x {count}")
        lines.append("-" * 40)
        lines.append(f"Balance : Rs. {result.new_balance:,.2f}")
        lines.append(result.message)
        lines.append("=" * 40)
        return "\n".join(lines)
