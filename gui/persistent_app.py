"""Persistent CustomTkinter application backed by BankService."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import Canvas, messagebox

from banking import BankService
from database import Database


BG = "#050912"
SURFACE = "#0b1424"
SURFACE_RAISED = "#101d31"
SURFACE_SOFT = "#13243b"
BORDER = "#1d3554"
TEXT = "#edf6ff"
MUTED = "#8195ad"
CYAN = "#35d7ff"
CYAN_HOVER = "#69e4ff"
BLUE = "#2574ff"
BLUE_HOVER = "#4388ff"
RED = "#ff5572"
GREEN = "#32e6a1"

DARK_THEME = {
    "BG": "#050912",
    "SURFACE": "#0b1424",
    "SURFACE_RAISED": "#101d31",
    "SURFACE_SOFT": "#13243b",
    "BORDER": "#1d3554",
    "TEXT": "#edf6ff",
    "MUTED": "#8195ad",
    "CYAN": "#35d7ff",
    "CYAN_HOVER": "#69e4ff",
    "BLUE": "#2574ff",
    "BLUE_HOVER": "#4388ff",
}

LIGHT_THEME = {
    "BG": "#f4f9ff",
    "SURFACE": "#ffffff",
    "SURFACE_RAISED": "#eef7ff",
    "SURFACE_SOFT": "#e1f2ff",
    "BORDER": "#b9dcf4",
    "TEXT": "#03111f",
    "MUTED": "#36566d",
    "CYAN": "#079fe8",
    "CYAN_HOVER": "#36baf2",
    "BLUE": "#1769ff",
    "BLUE_HOVER": "#4388ff",
}


def apply_theme_palette(theme):
    """Update the shared palette used when the active screen is rebuilt."""
    global BG, SURFACE, SURFACE_RAISED, SURFACE_SOFT, BORDER, TEXT, MUTED
    global CYAN, CYAN_HOVER, BLUE, BLUE_HOVER
    BG = theme["BG"]
    SURFACE = theme["SURFACE"]
    SURFACE_RAISED = theme["SURFACE_RAISED"]
    SURFACE_SOFT = theme["SURFACE_SOFT"]
    BORDER = theme["BORDER"]
    TEXT = theme["TEXT"]
    MUTED = theme["MUTED"]
    CYAN = theme["CYAN"]
    CYAN_HOVER = theme["CYAN_HOVER"]
    BLUE = theme["BLUE"]
    BLUE_HOVER = theme["BLUE_HOVER"]


class InteractiveCard(ctk.CTkFrame):
    """Decorative perspective card that tilts toward the pointer."""

    def __init__(self, master, holder_name, account_number, **kwargs):
        super().__init__(master, fg_color="transparent", height=174, **kwargs)
        self.pack_propagate(False)
        self.holder_name = holder_name.upper()[:24]
        self.account_number = account_number
        self.card_canvas = Canvas(
            self,
            width=316,
            height=160,
            bg=SURFACE,
            highlightthickness=0,
        )
        self.card_canvas.pack(expand=True, fill="both")
        self.card_canvas.bind("<Enter>", self._on_enter)
        self.card_canvas.bind("<Leave>", self._on_leave)
        self.card_canvas.bind("<Motion>", self._on_motion)
        self._tilt_x = 0.0
        self._tilt_y = 0.0
        self._hovered = False
        self._render_card()

    def _on_enter(self, _event):
        self._hovered = True

    def _on_leave(self, _event):
        self._hovered = False
        self._tilt_x = 0.0
        self._tilt_y = 0.0
        self._render_card()

    def _on_motion(self, event):
        if not self._hovered:
            return
        self._tilt_x = max(-1.0, min(1.0, (event.x - 158) / 158))
        self._tilt_y = max(-1.0, min(1.0, (event.y - 80) / 80))
        self._render_card()

    def _render_card(self):
        canvas = self.card_canvas
        canvas.delete("all")
        is_light = BG == LIGHT_THEME["BG"]
        card_fill = "#ffffff" if is_light else "#0d2642"
        card_band = "#d9f0ff" if is_light else "#123d68"
        card_line = "#8fcbed" if is_light else "#1d5c88"
        card_text = "#06223a" if is_light else TEXT
        chip_primary = "#079fe8" if is_light else "#35d7ff"
        chip_secondary = "#1769ff" if is_light else "#2574ff"
        skew_x = self._tilt_x * 13
        skew_y = self._tilt_y * 5
        left = 12 + skew_x
        top = 8 + skew_y
        right = 304 + skew_x
        bottom = 148 + skew_y
        card = [(left + 8, top), (right, top + 4), (right - 8, bottom), (left, bottom - 4)]
        canvas.create_polygon(card, fill=card_fill, outline=CYAN, width=2)
        canvas.create_polygon(
            [(left + 8, top), (right, top + 4), (right - 8, top + 40), (left, top + 36)],
            fill=card_band,
            outline="",
        )
        canvas.create_line(left + 8, bottom - 38, right - 10, bottom - 42, fill=card_line, width=1)
        canvas.create_oval(right - 50, top + 20, right - 22, top + 48, fill=chip_primary, outline="")
        canvas.create_oval(right - 42, top + 26, right - 18, top + 50, fill=chip_secondary, outline="")
        canvas.create_text(left + 20, top + 19, text="ATM BANK", anchor="w", fill=card_text, font=("Segoe UI", 10, "bold"))
        canvas.create_text(left + 22, top + 73, text="••••  ••••  ••••  " + self.account_number[-4:], anchor="w", fill=card_text, font=("Consolas", 14, "bold"))
        canvas.create_text(left + 22, bottom - 19, text=self.holder_name, anchor="w", fill=card_text, font=("Segoe UI", 9, "bold"))
        canvas.create_text(right - 16, bottom - 19, text="DEBIT", anchor="e", fill=CYAN, font=("Segoe UI", 8, "bold"))


class PersistentATMApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ATM Bank")
        self.geometry("1180x760")
        self.minsize(900, 650)
        self.theme_mode = "dark"
        apply_theme_palette(DARK_THEME)
        ctk.set_appearance_mode(self.theme_mode)
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color=BG)
        self.bank = BankService(Database())
        self.account_number = ""
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.login_frame.pack(expand=True, fill="both")
        self._build_login(first_run=not self.bank.database.has_accounts())
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _close(self):
        self.bank.database.close()
        self.destroy()

    def _theme_button_text(self):
        return "LIGHT MODE" if self.theme_mode == "dark" else "DARK MODE"

    def _toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        apply_theme_palette(LIGHT_THEME if self.theme_mode == "light" else DARK_THEME)
        ctk.set_appearance_mode(self.theme_mode)
        self.configure(fg_color=BG)
        if self.account_number:
            row = self.bank.database.get_account(self.account_number)
            if row:
                self._build_dashboard(row)
                return
        self._build_login(first_run=not self.bank.database.has_accounts())

    def _clear(self):
        if getattr(self, "tip_card", None) is not None:
            self.tip_card.destroy()
            self.tip_card = None
        for widget in self.winfo_children():
            widget.pack_forget()

    def _show_tip(self, title, message):
        """Show a dismissible banking-safety tip in the lower-right corner."""
        if getattr(self, "tip_card", None) is not None:
            self.tip_card.destroy()

        self.tip_card = ctk.CTkFrame(
            self,
            width=330,
            height=118,
            corner_radius=14,
            fg_color=SURFACE,
            border_width=1,
            border_color=CYAN,
        )
        self.tip_card.place(relx=0.98, rely=0.96, anchor="se")
        self.tip_card.pack_propagate(False)

        heading = ctk.CTkFrame(self.tip_card, fg_color="transparent")
        heading.pack(fill="x", padx=16, pady=(13, 0))
        self._label(heading, "BANKING TIP", size=10, weight="bold", color=CYAN).pack(side="left")
        close_button = ctk.CTkButton(
            heading,
            text="×",
            width=24,
            height=24,
            corner_radius=12,
            fg_color="transparent",
            hover_color=SURFACE_SOFT,
            text_color=MUTED,
            font=ctk.CTkFont(size=18),
            command=self._dismiss_tip,
        )
        close_button.pack(side="right")
        self._label(self.tip_card, title, size=14, weight="bold").pack(anchor="w", padx=16, pady=(6, 1))
        self._label(self.tip_card, message, size=11, color=MUTED, wraplength=285, justify="left").pack(anchor="w", padx=16)

    def _dismiss_tip(self):
        if getattr(self, "tip_card", None) is not None:
            self.tip_card.destroy()
            self.tip_card = None

    def _label(self, master, text, size=13, weight="normal", color=None, **kwargs):
        if color is None:
            color = TEXT
        return ctk.CTkLabel(
            master,
            text=text,
            text_color=color,
            font=ctk.CTkFont(family="Segoe UI", size=size, weight=weight),
            **kwargs,
        )

    def _entry(self, master, placeholder, width=360, show=None):
        return ctk.CTkEntry(
            master,
            width=width,
            height=46,
            corner_radius=9,
            border_width=1,
            border_color=BORDER,
            fg_color=SURFACE_RAISED,
            text_color=TEXT,
            placeholder_text=placeholder,
            placeholder_text_color=MUTED,
            show=show,
        )

    def _button(self, master, text, command, width=170, primary=True, **kwargs):
        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            width=width,
            height=44,
            corner_radius=9,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=CYAN if primary else "transparent",
            hover_color=CYAN_HOVER if primary else SURFACE_SOFT,
            text_color="#03121f" if primary else TEXT,
            border_width=1 if not primary else 0,
            border_color=BORDER,
            **kwargs,
        )

    def _build_login(self, first_run=False):
        self._clear()
        frame = self.login_frame
        frame.pack(expand=True, fill="both")
        panel = ctk.CTkFrame(frame, width=500, height=610, corner_radius=20, fg_color=SURFACE, border_width=1, border_color=BORDER)
        panel.place(relx=0.5, rely=0.5, anchor="center")
        panel.pack_propagate(False)
        self._label(panel, text="ATM BANK", size=34, weight="bold", color=CYAN).pack(pady=(42, 2))
        self._label(panel, text="PERSONAL BANKING / SECURE ACCESS", size=11, weight="bold", color=MUTED).pack(pady=(0, 30))
        if first_run:
            self._label(panel, text="Welcome to your new bank", size=19, weight="bold").pack(pady=(0, 4))
            self._label(panel, text="Create an account to get started.", color=MUTED).pack(pady=(0, 16))
            self._button(panel, "CREATE YOUR FIRST ACCOUNT", self._create_account_dialog, width=360).pack(pady=(0, 26))
            self._label(panel, text="Already have an account? Sign in below", color=MUTED).pack(pady=(0, 10))
        else:
            self._label(panel, text="Sign in to continue", size=19, weight="bold").pack(pady=(0, 16))
        self.login_account = self._entry(panel, "Account number", width=360)
        self.login_account.pack(pady=8)
        self.login_pin = self._entry(panel, "4-digit PIN", width=360, show="*")
        self.login_pin.pack(pady=8)
        self._button(panel, "SIGN IN", self._login, width=360).pack(pady=(18, 8))
        if not first_run:
            self._button(panel, "CREATE NEW ACCOUNT", self._create_account_dialog, width=360, primary=False).pack(pady=(0, 36))
        self._button(panel, self._theme_button_text(), self._toggle_theme, width=150, primary=False).pack(pady=(0, 18))
        self._show_tip("Protect your PIN", "Never share your PIN with anyone, even if they claim to be from the bank.")

    def _login(self):
        try:
            row = self.bank.authenticate(self.login_account.get(), self.login_pin.get())
            self.account_number = row["account_number"]
            self._build_dashboard(row)
        except Exception as exc:
            messagebox.showerror("Sign in failed", str(exc))

    def _create_account_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("ATM BANK / Create account")
        dialog.geometry("500x640")
        dialog.minsize(420, 500)
        dialog.configure(fg_color=BG)
        dialog.transient(self)
        dialog.grab_set()
        body = ctk.CTkScrollableFrame(
            dialog,
            corner_radius=16,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            scrollbar_button_color=BLUE,
            scrollbar_button_hover_color=BLUE_HOVER,
        )
        body.pack(expand=True, fill="both", padx=18, pady=18)
        self._label(body, text="Create your account", size=25, weight="bold", color=CYAN).pack(pady=(24, 3))
        self._label(body, text="A few details, then you are ready to bank.", color=MUTED).pack(pady=(0, 22))
        fields = {}
        for label, key in [("Full name", "name"), ("Phone", "phone"), ("Email", "email"), ("Address", "address")]:
            self._label(body, text=label.upper(), size=10, weight="bold", color=MUTED).pack(anchor="w", padx=48)
            fields[key] = self._entry(body, label, width=390)
            fields[key].pack(pady=(3, 8))
        self._label(body, text="ACCOUNT TYPE", size=10, weight="bold", color=MUTED).pack(anchor="w", padx=48, pady=(8, 3))
        account_type = ctk.CTkOptionMenu(
            body,
            values=["Savings", "Current"],
            width=390,
            height=42,
            corner_radius=9,
            fg_color=SURFACE_SOFT,
            button_color=BLUE,
            button_hover_color=BLUE_HOVER,
            text_color=TEXT,
            dropdown_fg_color=SURFACE,
            dropdown_hover_color=SURFACE_SOFT,
            dropdown_text_color=TEXT,
        )
        account_type.pack(pady=7)
        amount = self._entry(body, "Initial deposit (Rs.)", width=390)
        amount.pack(pady=7)
        pin = self._entry(body, "4-digit PIN", width=390, show="*")
        pin.pack(pady=7)
        confirm = self._entry(body, "Confirm PIN", width=390, show="*")
        confirm.pack(pady=7)

        def submit():
            try:
                account = self.bank.create_account(
                    fields["name"].get(), fields["phone"].get(), fields["email"].get(), fields["address"].get(),
                    account_type.get(), float(amount.get()), pin.get(), confirm.get()
                )
                messagebox.showinfo("Account created", f"Account Created Successfully\n\nAccount Number: {account}")
                dialog.destroy()
                self.login_account.delete(0, "end")
                self.login_account.insert(0, account)
            except Exception as exc:
                messagebox.showerror("Could not create account", str(exc))

        self._button(body, "CREATE ACCOUNT", submit, width=390).pack(pady=22)

    def _build_dashboard(self, row):
        self._clear()
        root = ctk.CTkFrame(self, fg_color=BG)
        root.pack(expand=True, fill="both", padx=34, pady=26)
        header = ctk.CTkFrame(root, fg_color="transparent")
        header.pack(fill="x")
        self._label(header, text="OVERVIEW", size=11, weight="bold", color=CYAN).pack(anchor="w")
        self.greeting = self._label(header, text=f"Good day, {row['name']}", size=28, weight="bold")
        self.greeting.pack(side="left")
        self._button(header, self._theme_button_text(), self._toggle_theme, width=150, primary=False).pack(side="right", padx=(0, 10))
        self._button(header, "LOG OUT", self._build_login, width=110, primary=False).pack(side="right")

        content = ctk.CTkFrame(root, fg_color="transparent")
        content.pack(expand=True, fill="both", pady=(24, 0))
        left = ctk.CTkFrame(content, width=360, corner_radius=16, fg_color=SURFACE, border_width=1, border_color=BORDER)
        left.pack(side="left", fill="y", padx=(0, 18))
        left.pack_propagate(False)
        InteractiveCard(left, row["name"], row["account_number"]).pack(fill="x", padx=18, pady=(18, 2))
        self._label(left, text="AVAILABLE BALANCE", size=11, weight="bold", color=MUTED).pack(anchor="w", padx=26, pady=(12, 6))
        self.balance = self._label(left, text="", size=34, weight="bold", color=CYAN)
        self.balance.pack(anchor="w", padx=26)
        self.details = self._label(left, text="", size=12, color=MUTED, justify="left")
        self.details.pack(anchor="w", padx=26, pady=(6, 16))
        self._label(left, text="QUICK ACTIONS", size=11, weight="bold", color=MUTED).pack(anchor="w", padx=26, pady=(4, 8))
        action_grid = ctk.CTkFrame(left, fg_color="transparent")
        action_grid.pack(fill="x", padx=22)
        action_items = [("DEPOSIT", lambda: self._amount_dialog("Deposit", self.bank.deposit)), ("WITHDRAW", lambda: self._amount_dialog("Withdraw", self.bank.withdraw)), ("TRANSFER", self._transfer_dialog), ("PROFILE", self._profile_dialog), ("CHANGE PIN", self._pin_dialog), ("CLOSE ACCOUNT", self._close_account)]
        for index, (label, command) in enumerate(action_items):
            button = self._button(action_grid, label, command, width=145, primary=index < 3)
            button.grid(row=index // 2, column=index % 2, padx=4, pady=3, sticky="ew")
        for row_index in range(3):
            action_grid.grid_rowconfigure(row_index, weight=1, minsize=42)
        action_grid.grid_columnconfigure(0, weight=1)
        action_grid.grid_columnconfigure(1, weight=1)

        right = ctk.CTkFrame(content, corner_radius=16, fg_color=SURFACE, border_width=1, border_color=BORDER)
        right.pack(side="left", expand=True, fill="both")
        self._label(right, text="TRANSACTION ACTIVITY", size=11, weight="bold", color=CYAN).pack(anchor="w", padx=26, pady=(26, 4))
        self._label(right, text="Recent account movements", size=18, weight="bold").pack(anchor="w", padx=26, pady=(0, 14))
        self.history = ctk.CTkTextbox(right, height=260, corner_radius=10, border_width=1, border_color=BORDER, fg_color=SURFACE_RAISED, text_color=TEXT, font=ctk.CTkFont(family="Consolas", size=12))
        self.history.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self._refresh_dashboard()
        self._show_tip("Stay alert", "Check the account number and amount carefully before confirming a transfer.")

    def _refresh_dashboard(self):
        row = self.bank.database.get_account(self.account_number)
        self.balance.configure(text=f"Rs. {row['balance']:,.2f}")
        self.details.configure(text=f"{row['account_type']}  |  {row['account_number']}  |  Status: {row['status']}")
        self.history.configure(state="normal")
        self.history.delete("1.0", "end")
        for txn in self.bank.transactions(self.account_number):
            self.history.insert("end", f"{txn['timestamp']}  {txn['transaction_type']:<12} Rs. {txn['amount']:>10,.2f}  {txn['description']}\n")
        self.history.configure(state="disabled")

    def _dialog(self, title, subtitle, width=460, height=330):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"ATM BANK / {title}")
        dialog.geometry(f"{width}x{height}")
        dialog.minsize(width, height)
        dialog.configure(fg_color=BG)
        dialog.transient(self)
        dialog.grab_set()
        body = ctk.CTkFrame(dialog, corner_radius=16, fg_color=SURFACE, border_width=1, border_color=BORDER)
        body.pack(expand=True, fill="both", padx=16, pady=16)
        self._label(body, title.upper(), size=22, weight="bold", color=CYAN).pack(pady=(22, 2))
        self._label(body, subtitle, size=12, color=MUTED).pack(pady=(0, 20))
        return dialog, body

    def _dialog_buttons(self, body, submit, cancel):
        buttons = ctk.CTkFrame(body, fg_color="transparent")
        buttons.pack(fill="x", padx=34, pady=(18, 8))
        self._button(buttons, "CANCEL", cancel, width=150, primary=False).pack(side="left", expand=True, padx=(0, 6))
        self._button(buttons, "CONTINUE", submit, width=150).pack(side="left", expand=True, padx=(6, 0))

    def _error_label(self, body):
        label = self._label(body, text="", size=11, color=RED, wraplength=360)
        label.pack(pady=(4, 0))
        return label

    def _amount_dialog(self, title, operation):
        dialog, body = self._dialog(title, "Enter an amount to update your account.", height=360)
        self._label(body, text="AMOUNT (RS.)", size=10, weight="bold", color=MUTED).pack(anchor="w", padx=34)
        amount_entry = self._entry(body, "e.g. 5,000", width=360)
        amount_entry.pack(pady=(5, 4))
        if title == "Withdraw":
            self._label(body, "ATM withdrawals must use multiples of Rs. 500.", size=11, color=MUTED).pack(pady=(2, 0))
        error = self._error_label(body)

        def submit():
            try:
                value = float(amount_entry.get().replace(",", "").strip())
                txn = operation(self.account_number, value)
                dialog.destroy()
                messagebox.showinfo(
                    f"{title} successful",
                    f"TRANSACTION RECEIPT\n\nTransaction ID: {txn.transaction_id}\n"
                    f"Amount: Rs. {value:,.2f}\nRemaining balance: Rs. {txn.account.get_balance():,.2f}",
                )
                self._refresh_dashboard()
            except (ValueError, TypeError):
                error.configure(text="Enter a valid numeric amount.")
            except Exception as exc:
                error.configure(text=str(exc))

        self._dialog_buttons(body, submit, dialog.destroy)
        amount_entry.focus_set()
        amount_entry.bind("<Return>", lambda _event: submit())

    def _transfer_dialog(self):
        dialog, body = self._dialog("Transfer money", "Move funds securely to another account.", height=430)
        self._label(body, "DESTINATION ACCOUNT", size=10, weight="bold", color=MUTED).pack(anchor="w", padx=34)
        target_entry = self._entry(body, "Account number", width=360)
        target_entry.pack(pady=(5, 14))
        self._label(body, "AMOUNT (RS.)", size=10, weight="bold", color=MUTED).pack(anchor="w", padx=34)
        amount_entry = self._entry(body, "e.g. 10,000", width=360)
        amount_entry.pack(pady=(5, 4))
        error = self._error_label(body)

        def submit():
            try:
                target = target_entry.get().strip()
                amount = float(amount_entry.get().replace(",", "").strip())
                self.bank.transfer(self.account_number, target, amount)
                dialog.destroy()
                messagebox.showinfo("Transfer successful", f"TRANSFER COMPLETE\n\nRs. {amount:,.2f} sent to account {target}.")
                self._refresh_dashboard()
            except (ValueError, TypeError):
                error.configure(text="Enter a valid account number and amount.")
            except Exception as exc:
                error.configure(text=str(exc))

        self._dialog_buttons(body, submit, dialog.destroy)
        target_entry.focus_set()
        target_entry.bind("<Return>", lambda _event: amount_entry.focus_set())

    def _profile_dialog(self):
        row = self.bank.database.get_account(self.account_number)
        dialog, body = self._dialog("Edit profile", "Keep your personal information up to date.", height=590)
        entries = {}
        for label, key in [("FULL NAME", "name"), ("PHONE", "phone"), ("EMAIL", "email"), ("ADDRESS", "address")]:
            self._label(body, label, size=10, weight="bold", color=MUTED).pack(anchor="w", padx=34, pady=(4, 0))
            entry = self._entry(body, label.title(), width=360)
            entry.insert(0, row[key])
            entry.pack(pady=(4, 5))
            entries[key] = entry
        error = self._error_label(body)

        def submit():
            try:
                values = {key: entry.get() for key, entry in entries.items()}
                self.bank.update_profile(self.account_number, **values)
                dialog.destroy()
                self._refresh_dashboard()
                self.greeting.configure(text=f"Good day, {values['name']}")
            except Exception as exc:
                error.configure(text=str(exc))

        self._dialog_buttons(body, submit, dialog.destroy)
        entries["name"].focus_set()

    def _pin_dialog(self):
        dialog, body = self._dialog("Change PIN", "Use a new four-digit PIN to protect your account.", height=500)
        entries = {}
        for label, key in [("CURRENT PIN", "old"), ("NEW PIN", "new"), ("CONFIRM NEW PIN", "confirm")]:
            self._label(body, label, size=10, weight="bold", color=MUTED).pack(anchor="w", padx=34, pady=(5, 0))
            entry = self._entry(body, "4 digits", width=360, show="*")
            entry.pack(pady=(4, 7))
            entries[key] = entry
        error = self._error_label(body)

        def submit():
            try:
                self.bank.change_pin(self.account_number, entries["old"].get(), entries["new"].get(), entries["confirm"].get())
                dialog.destroy()
                messagebox.showinfo("PIN updated", "Your PIN was changed successfully.")
            except Exception as exc:
                error.configure(text=str(exc))

        self._dialog_buttons(body, submit, dialog.destroy)
        entries["old"].focus_set()

    def _close_account(self):
        dialog, body = self._dialog("Close account", "This action is permanent. Your balance must be zero.", height=360)
        self._label(body, "ENTER PIN TO CONFIRM", size=10, weight="bold", color=MUTED).pack(anchor="w", padx=34)
        pin_entry = self._entry(body, "Current PIN", width=360, show="*")
        pin_entry.pack(pady=(5, 4))
        error = self._error_label(body)

        def submit():
            try:
                self.bank.close_account(self.account_number, pin_entry.get())
                dialog.destroy()
                messagebox.showinfo("Account closed", "Your account has been closed successfully.")
                self._build_login()
            except Exception as exc:
                error.configure(text=str(exc))

        self._dialog_buttons(body, submit, dialog.destroy)
        pin_entry.focus_set()
        pin_entry.bind("<Return>", lambda _event: submit())


def run_persistent_gui():
    app = PersistentATMApp()
    app.mainloop()
