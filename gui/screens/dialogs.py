"""Modal dialogs for ATM transactions."""

import customtkinter as ctk
from tkinter import messagebox

from gui.utils import (
    format_currency,
    handle_transaction_error,
    show_success,
    account_type_label,
)


class _BaseDialog(ctk.CTkToplevel):
    """Base class for transaction popups."""

    def __init__(self, master, title: str, width: int = 420, height: int = 320):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.body = ctk.CTkFrame(self, corner_radius=12)
        self.body.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            self.body,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(12, 16))

    def _center_on_parent(self) -> None:
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


class DepositDialog(_BaseDialog):
    def __init__(self, master, atm, account, on_complete):
        super().__init__(master, "Deposit Money")
        self.atm = atm
        self.account = account
        self.on_complete = on_complete

        ctk.CTkLabel(
            self.body,
            text=f"Account {account.account_number} — {account_type_label(account)}",
            text_color="gray70",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(self.body, text="Amount (Rs.)").pack(anchor="w", padx=24)
        self.amount_entry = ctk.CTkEntry(self.body, width=280, height=40, placeholder_text="e.g. 5000")
        self.amount_entry.pack(pady=(4, 16), padx=24)

        btn_row = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_row.pack(pady=12)
        ctk.CTkButton(btn_row, text="Cancel", width=120, fg_color="gray40", command=self.destroy).pack(
            side="left", padx=8
        )
        ctk.CTkButton(btn_row, text="Deposit", width=120, command=self._submit).pack(side="left", padx=8)

        self._center_on_parent()
        self.amount_entry.focus()

    def _submit(self) -> None:
        try:
            amount = float(self.amount_entry.get().strip())
            txn = self.atm.process_deposit(self.account, amount)
            show_success(
                "Deposit Successful",
                f"Transaction ID: {txn.transaction_id}\nNew Balance: {format_currency(self.account.get_balance())}",
            )
            self.on_complete()
            self.destroy()
        except Exception as exc:
            handle_transaction_error(exc)


class WithdrawDialog(_BaseDialog):
    def __init__(self, master, atm, account, on_complete):
        super().__init__(master, "Withdraw Cash", height=360)
        self.atm = atm
        self.account = account
        self.on_complete = on_complete

        ctk.CTkLabel(
            self.body,
            text=f"Account {account.account_number} — {account_type_label(account)}",
            text_color="gray70",
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            self.body,
            text="Amount must be a multiple of Rs. 500",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(self.body, text="Amount (Rs.)").pack(anchor="w", padx=24)
        self.amount_entry = ctk.CTkEntry(self.body, width=280, height=40, placeholder_text="e.g. 5000")
        self.amount_entry.pack(pady=(4, 16), padx=24)

        btn_row = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_row.pack(pady=12)
        ctk.CTkButton(btn_row, text="Cancel", width=120, fg_color="gray40", command=self.destroy).pack(
            side="left", padx=8
        )
        ctk.CTkButton(btn_row, text="Withdraw", width=120, command=self._submit).pack(side="left", padx=8)

        self._center_on_parent()
        self.amount_entry.focus()

    def _submit(self) -> None:
        try:
            amount = float(self.amount_entry.get().strip())
            txn = self.atm.process_withdrawal(self.account, amount)
            show_success(
                "Withdrawal Successful",
                f"Please collect your cash.\nTransaction ID: {txn.transaction_id}\n"
                f"Remaining Balance: {format_currency(self.account.get_balance())}",
            )
            self.on_complete()
            self.destroy()
        except Exception as exc:
            handle_transaction_error(exc)


class TransferDialog(_BaseDialog):
    def __init__(self, master, atm, customer, source_account, on_complete):
        super().__init__(master, "Transfer Money", height=400)
        self.atm = atm
        self.customer = customer
        self.source_account = source_account
        self.on_complete = on_complete

        ctk.CTkLabel(
            self.body,
            text=f"From Account {source_account.account_number}",
            text_color="gray70",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(self.body, text="Receiver Account Number").pack(anchor="w", padx=24)
        self.target_entry = ctk.CTkEntry(self.body, width=280, height=40, placeholder_text="e.g. 2001")
        self.target_entry.pack(pady=(4, 12), padx=24)

        ctk.CTkLabel(self.body, text="Amount (Rs.)").pack(anchor="w", padx=24)
        self.amount_entry = ctk.CTkEntry(self.body, width=280, height=40, placeholder_text="e.g. 2000")
        self.amount_entry.pack(pady=(4, 16), padx=24)

        btn_row = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_row.pack(pady=12)
        ctk.CTkButton(btn_row, text="Cancel", width=120, fg_color="gray40", command=self.destroy).pack(
            side="left", padx=8
        )
        ctk.CTkButton(btn_row, text="Transfer", width=120, command=self._submit).pack(side="left", padx=8)

        self._center_on_parent()
        self.target_entry.focus()

    def _submit(self) -> None:
        try:
            target_num = self.target_entry.get().strip()
            target_account = self.customer.get_account(target_num)
            if not target_account:
                messagebox.showerror("Account Not Found", "Receiver account not found.")
                return
            if target_account.account_number == self.source_account.account_number:
                messagebox.showerror("Invalid Transfer", "Cannot transfer to the same account.")
                return

            amount = float(self.amount_entry.get().strip())
            txn = self.atm.process_transfer(self.source_account, target_account, amount)
            show_success(
                "Transfer Successful",
                f"Transaction ID: {txn.transaction_id}\n"
                f"Sent {format_currency(amount)} to account {target_num}.",
            )
            self.on_complete()
            self.destroy()
        except Exception as exc:
            handle_transaction_error(exc)


class ChangePinDialog(_BaseDialog):
    def __init__(self, master, customer, account, on_complete):
        super().__init__(master, "Change PIN", height=420)
        self.customer = customer
        self.account = account
        self.on_complete = on_complete

        ctk.CTkLabel(
            self.body,
            text="PIN is synced across your card and all accounts.",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        ).pack(pady=(0, 12))

        for label, attr, placeholder in [
            ("Current PIN", "old_pin_entry", "4 digits"),
            ("New PIN", "new_pin_entry", "4 digits"),
            ("Confirm New PIN", "confirm_pin_entry", "4 digits"),
        ]:
            ctk.CTkLabel(self.body, text=label).pack(anchor="w", padx=24)
            entry = ctk.CTkEntry(self.body, width=280, height=40, show="●", placeholder_text=placeholder)
            entry.pack(pady=(4, 10), padx=24)
            setattr(self, attr, entry)

        btn_row = ctk.CTkFrame(self.body, fg_color="transparent")
        btn_row.pack(pady=12)
        ctk.CTkButton(btn_row, text="Cancel", width=120, fg_color="gray40", command=self.destroy).pack(
            side="left", padx=8
        )
        ctk.CTkButton(btn_row, text="Change PIN", width=120, command=self._submit).pack(side="left", padx=8)

        self._center_on_parent()
        self.old_pin_entry.focus()

    def _submit(self) -> None:
        old_pin = self.old_pin_entry.get().strip()
        new_pin = self.new_pin_entry.get().strip()
        confirm = self.confirm_pin_entry.get().strip()

        if len(new_pin) != 4 or not new_pin.isdigit():
            messagebox.showerror("Invalid PIN", "New PIN must be exactly 4 digits.")
            return
        if new_pin != confirm:
            messagebox.showerror("Mismatch", "New PIN and confirmation do not match.")
            return

        try:
            if self.account.change_pin(old_pin, new_pin):
                self.customer.card.change_pin(old_pin, new_pin)
                show_success("PIN Changed", "Your PIN has been updated successfully.")
                self.on_complete()
                self.destroy()
        except Exception as exc:
            handle_transaction_error(exc)


class MiniStatementDialog(_BaseDialog):
    def __init__(self, master, atm, account):
        super().__init__(master, "Mini Statement", width=480, height=420)
        self.atm = atm
        self.account = account

        ctk.CTkLabel(
            self.body,
            text=f"Account {account.account_number} — Last 5 Transactions",
            text_color="gray70",
        ).pack(pady=(0, 8))

        statement = self.atm.get_mini_statement(account)
        textbox = ctk.CTkTextbox(self.body, width=420, height=260, font=ctk.CTkFont(family="Consolas", size=13))
        textbox.pack(pady=8, padx=12)
        textbox.insert("1.0", statement)
        textbox.configure(state="disabled")

        ctk.CTkButton(self.body, text="Close", width=120, command=self.destroy).pack(pady=12)
        self._center_on_parent()
