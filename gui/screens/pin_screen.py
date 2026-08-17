"""PIN authentication screen with numeric keypad."""

import customtkinter as ctk

from exceptions import CardBlockedError, InvalidPINError
from gui.utils import show_error


class PinScreen(ctk.CTkFrame):
    MAX_PIN_LENGTH = 4

    def __init__(self, master, customer, on_success, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.customer = customer
        self.on_success = on_success
        self._pin_buffer = ""

        self._build_ui()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, corner_radius=16)
        container.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(
            container,
            text="ATM System",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(32, 4))

        ctk.CTkLabel(
            container,
            text=f"Welcome, {self.customer.name}",
            font=ctk.CTkFont(size=14),
            text_color="gray70",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            container,
            text="Enter your 4-digit PIN",
            font=ctk.CTkFont(size=16),
        ).pack(pady=(16, 12))

        self.pin_display = ctk.CTkEntry(
            container,
            width=220,
            height=48,
            show="●",
            justify="center",
            font=ctk.CTkFont(size=22),
            state="readonly",
        )
        self.pin_display.pack(pady=(0, 20))

        keypad = ctk.CTkFrame(container, fg_color="transparent")
        keypad.pack(pady=8)

        keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["Clear", "0", "Enter"],
        ]

        for row in keys:
            row_frame = ctk.CTkFrame(keypad, fg_color="transparent")
            row_frame.pack(pady=4)
            for key in row:
                ctk.CTkButton(
                    row_frame,
                    text=key,
                    width=80,
                    height=52,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    command=lambda k=key: self._on_key_press(k),
                ).pack(side="left", padx=6)

        self.status_label = ctk.CTkLabel(
            container,
            text="Default demo PIN: 1234",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        )
        self.status_label.pack(pady=(20, 32))

    def _update_display(self) -> None:
        self.pin_display.configure(state="normal")
        self.pin_display.delete(0, "end")
        self.pin_display.insert(0, "●" * len(self._pin_buffer))
        self.pin_display.configure(state="readonly")

    def _on_key_press(self, key: str) -> None:
        if key == "Clear":
            self._pin_buffer = ""
            self.status_label.configure(text="PIN cleared.", text_color="gray60")
            self._update_display()
            return

        if key == "Enter":
            self._submit_pin()
            return

        if len(self._pin_buffer) < self.MAX_PIN_LENGTH:
            self._pin_buffer += key
            self._update_display()

        if len(self._pin_buffer) == self.MAX_PIN_LENGTH:
            self._submit_pin()

    def _submit_pin(self) -> None:
        if len(self._pin_buffer) != self.MAX_PIN_LENGTH:
            self.status_label.configure(
                text="Please enter all 4 digits.",
                text_color="#e74c3c",
            )
            return

        try:
            if self.customer.card.validate_pin(self._pin_buffer):
                self.status_label.configure(
                    text="Authentication successful!",
                    text_color="#2ecc71",
                )
                self.after(300, self.on_success)
        except InvalidPINError as exc:
            self._pin_buffer = ""
            self._update_display()
            self.status_label.configure(text=str(exc), text_color="#e74c3c")
            show_error("Invalid PIN", str(exc))
        except CardBlockedError as exc:
            self._pin_buffer = ""
            self._update_display()
            self.status_label.configure(text=str(exc), text_color="#e74c3c")
            show_error("Card Blocked", str(exc))
            self.after(500, lambda: self.master.winfo_toplevel().destroy())

    def reset(self) -> None:
        self._pin_buffer = ""
        self._update_display()
        self.status_label.configure(
            text="Default demo PIN: 1234",
            text_color="gray60",
        )
