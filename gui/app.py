"""Main GUI application — entry point for the ATM graphical interface."""

import customtkinter as ctk

from gui.data_setup import setup_dummy_data
from gui.screens.pin_screen import PinScreen
from gui.screens.dashboard import DashboardScreen
from gui.utils import DEVELOPER_NAME


class ATMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ATM System — Enigmatix")
        self.geometry("960x640")
        self.minsize(860, 580)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.atm, self.customer = setup_dummy_data()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both")

        self.pin_screen = PinScreen(
            self.container,
            self.customer,
            on_success=self._show_dashboard,
        )
        self.dashboard = DashboardScreen(
            self.container,
            self.atm,
            self.customer,
            on_logout=self._show_pin_screen,
        )

        self._show_pin_screen()

    def _hide_all(self) -> None:
        self.pin_screen.pack_forget()
        self.dashboard.pack_forget()

    def _show_pin_screen(self) -> None:
        self._hide_all()
        self.pin_screen.reset()
        self.pin_screen.pack(expand=True, fill="both")

    def _show_dashboard(self) -> None:
        self._hide_all()
        self.dashboard.refresh_balances()
        self.dashboard.pack(expand=True, fill="both")


def run_gui() -> None:
    app = ATMApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
