"""Canvas logo used by both the boot screen and session handoff."""

from __future__ import annotations

from .config import BOOT_DURATION
from .easing import ease_out
from .manager import AnimationManager


class LogoReveal:
    """Draws a small ATM mark and reveals it with scale and opacity-like color."""

    def __init__(self, canvas, manager: AnimationManager, accent: str, text_color: str, background: str):
        self.canvas = canvas
        self.manager = manager
        self.accent = accent
        self.text_color = text_color
        self.background = background

    def reveal(self, duration: int = BOOT_DURATION, on_complete=None) -> None:
        def update(progress: float) -> None:
            self.canvas.delete("logo")
            scale = 0.72 + 0.28 * progress
            center_x = self.canvas.winfo_width() / 2
            center_y = self.canvas.winfo_height() / 2 - 18
            width = 150 * scale
            height = 76 * scale
            left, right = center_x - width / 2, center_x + width / 2
            top, bottom = center_y - height / 2, center_y + height / 2
            self.canvas.create_rectangle(left, top, right, bottom, outline=self.accent, width=2, tags="logo")
            self.canvas.create_text(center_x, center_y - 8 * scale, text="ATM", fill=self.accent, font=("Segoe UI", int(24 * scale), "bold"), tags="logo")
            self.canvas.create_text(center_x, center_y + 22 * scale, text="BANK", fill=self.text_color, font=("Segoe UI", int(10 * scale), "bold"), tags="logo")

        self.manager.animate(duration, update, ease_out, on_complete)
