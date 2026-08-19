"""Boot splash sequence for the persistent ATM application."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import Canvas

from .config import BOOT_DURATION
from .easing import ease_in_out
from .logo import LogoReveal
from .manager import AnimationManager


class BootScreen(ctk.CTkFrame):
    def __init__(self, master, palette: dict[str, str], on_complete):
        super().__init__(master, fg_color=palette["BG"])
        self.palette = palette
        self.on_complete = on_complete
        self.manager = AnimationManager(self)
        self.canvas = Canvas(self, bg=palette["BG"], highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", self._draw_background)
        self._draw_background()
        self.after(40, self._start)

    def _draw_background(self, _event=None):
        self.canvas.delete("background")
        width, height = max(1, self.winfo_width()), max(1, self.winfo_height())
        self.canvas.create_rectangle(0, 0, width, height, fill=self.palette["BG"], outline="", tags="background")

    def _start(self):
        logo = LogoReveal(self.canvas, self.manager, self.palette["CYAN"], self.palette["TEXT"], self.palette["BG"])
        logo.reveal(duration=1100, on_complete=self._show_copy)

    def _show_copy(self):
        width, height = self.winfo_width() / 2, self.winfo_height() / 2
        self.canvas.create_text(width, height + 70, text="ATM SYSTEM", fill=self.palette["TEXT"], font=("Segoe UI", 18, "bold"), tags="copy")
        self.canvas.create_text(width, height + 98, text="SECURE PERSONAL BANKING", fill=self.palette["MUTED"], font=("Segoe UI", 10, "bold"), tags="copy")
        self._loading_step(0)

    def _loading_step(self, step: int):
        self.canvas.delete("loader")
        width, height = self.winfo_width() / 2, self.winfo_height() / 2
        dots = " ".join("." if index != step % 3 else "o" for index in range(3))
        self.canvas.create_text(width, height + 142, text=dots, fill=self.palette["CYAN"], font=("Consolas", 16, "bold"), tags="loader")
        if step < 9:
            self.after(115, lambda: self._loading_step(step + 1))
        else:
            self.manager.animate(220, lambda _progress: None, ease_in_out, self.on_complete)

    def stop(self):
        self.manager.cancel_all()
