"""Main dashboard — account overview and transaction menu."""

import customtkinter as ctk

from gui.utils import format_currency, account_type_label
from gui.screens.dialogs import (
    DepositDialog,
    WithdrawDialog,
    TransferDialog,
    ChangePinDialog,
    MiniStatementDialog,
)


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, atm, customer, on_logout, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.atm = atm
        self.customer = customer
        self.on_logout = on_logout
        self.selected_account = None

        self._build_ui()
        self._select_first_account()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=12, height=72)
        header.pack(fill="x", padx=24, pady=(24, 12))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"Welcome, {self.customer.name}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left", padx=20, pady=16)

        ctk.CTkLabel(
            header,
            text=f"ATM: {self.atm.location}  |  Cash Available: {format_currency(self.atm.get_total_cash())}",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            header,
            text="Logout",
            width=100,
            fg_color="#c0392b",
            hover_color="#a93226",
            command=self.on_logout,
        ).pack(side="right", padx=20, pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=24, pady=12)

        left = ctk.CTkFrame(body, corner_radius=12, width=320)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        ctk.CTkLabel(
            left,
            text="Your Accounts",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        self.account_buttons_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.account_buttons_frame.pack(fill="x", padx=12, pady=4)

        self.balance_card = ctk.CTkFrame(left, corner_radius=10, fg_color=("#dbeafe", "#1e3a5f"))
        self.balance_card.pack(fill="x", padx=16, pady=16)

        self.balance_label = ctk.CTkLabel(
            self.balance_card,
            text="Rs. 0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.balance_label.pack(pady=(16, 4))

        self.account_info_label = ctk.CTkLabel(
            self.balance_card,
            text="Select an account",
            font=ctk.CTkFont(size=12),
            text_color="gray80",
        )
        self.account_info_label.pack(pady=(0, 16))

        right = ctk.CTkFrame(body, corner_radius=12)
        right.pack(side="left", expand=True, fill="both")

        ctk.CTkLabel(
            right,
            text="Transactions",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 12))

        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        menu_items = [
            ("💰  Deposit", self._open_deposit, "#27ae60"),
            ("💵  Withdraw", self._open_withdraw, "#2980b9"),
            ("🔄  Transfer", self._open_transfer, "#8e44ad"),
            ("🔐  Change PIN", self._open_change_pin, "#d35400"),
            ("📄  Mini Statement", self._open_statement, "#16a085"),
        ]

        for i, (label, command, color) in enumerate(menu_items):
            row, col = divmod(i, 2)
            btn = ctk.CTkButton(
                actions,
                text=label,
                height=64,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color=color,
                command=command,
            )
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            actions.grid_columnconfigure(col, weight=1)
            actions.grid_rowconfigure(row, weight=1)

        self._build_account_buttons()

    def _build_account_buttons(self) -> None:
        for widget in self.account_buttons_frame.winfo_children():
            widget.destroy()

        for acc_num, account in self.customer.accounts.items():
            btn = ctk.CTkButton(
                self.account_buttons_frame,
                text=f"{acc_num} — {account_type_label(account)}",
                height=40,
                anchor="w",
                fg_color="transparent",
                border_width=2,
                text_color=("gray10", "gray90"),
                command=lambda a=account: self._select_account(a),
            )
            btn.pack(fill="x", pady=4)

    def _select_first_account(self) -> None:
        accounts = list(self.customer.accounts.values())
        if accounts:
            self._select_account(accounts[0])

    def _select_account(self, account) -> None:
        self.selected_account = account
        self.balance_label.configure(text=format_currency(account.get_balance()))
        self.account_info_label.configure(
            text=f"{account_type_label(account)}  •  #{account.account_number}"
        )
        self._highlight_selected_account(account.account_number)

    def _highlight_selected_account(self, selected_num: str) -> None:
        for widget in self.account_buttons_frame.winfo_children():
            is_selected = selected_num in widget.cget("text")
            widget.configure(
                fg_color=("#3b82f6", "#2563eb") if is_selected else "transparent",
                text_color=("white", "white") if is_selected else ("gray10", "gray90"),
            )

    def refresh_balances(self) -> None:
        if self.selected_account:
            self._select_account(self.selected_account)
        self._build_account_buttons()
        if self.selected_account:
            self._highlight_selected_account(self.selected_account.account_number)

    def _open_deposit(self) -> None:
        if not self.selected_account:
            return
        DepositDialog(self.winfo_toplevel(), self.atm, self.selected_account, self.refresh_balances)

    def _open_withdraw(self) -> None:
        if not self.selected_account:
            return
        WithdrawDialog(self.winfo_toplevel(), self.atm, self.selected_account, self.refresh_balances)

    def _open_transfer(self) -> None:
        if not self.selected_account:
            return
        TransferDialog(
            self.winfo_toplevel(),
            self.atm,
            self.customer,
            self.selected_account,
            self.refresh_balances,
        )

    def _open_change_pin(self) -> None:
        if not self.selected_account:
            return
        ChangePinDialog(
            self.winfo_toplevel(),
            self.customer,
            self.selected_account,
            self.refresh_balances,
        )

    def _open_statement(self) -> None:
        if not self.selected_account:
            return
        MiniStatementDialog(self.winfo_toplevel(), self.atm, self.selected_account)
