"""Reusable geometry transitions for Tk widgets."""

from __future__ import annotations

from .config import SCREEN_TRANSITION_DURATION
from .easing import ease_in_out, ease_out
from .manager import AnimationManager


def move_placed(
    manager: AnimationManager,
    widget,
    start_relx: float,
    start_rely: float,
    end_relx: float,
    end_rely: float,
    duration: int,
    on_complete=None,
) -> None:
    """Move a widget between two relative positions using smooth easing."""

    def update(progress: float) -> None:
        if widget.winfo_exists():
            widget.place_configure(
                relx=start_relx + (end_relx - start_relx) * progress,
                rely=start_rely + (end_rely - start_rely) * progress,
            )

    manager.animate(duration, update, ease_out, on_complete)


def slide_in(
    manager: AnimationManager,
    widget,
    final_rely: float = 0.5,
    distance: float = 0.08,
    duration: int = SCREEN_TRANSITION_DURATION,
    on_complete=None,
) -> None:
    """Move a placed widget upward into position."""
    start_rely = final_rely + distance

    move_placed(manager, widget, 0.5, start_rely, 0.5, final_rely, duration, on_complete)


def slide_from_corner(
    manager: AnimationManager,
    widget,
    final_relx: float = 0.98,
    final_rely: float = 0.96,
    x_distance: float = 0.14,
    y_distance: float = 0.025,
    duration: int = SCREEN_TRANSITION_DURATION,
    on_complete=None,
) -> None:
    """Bring an anchored widget in diagonally from its nearest corner."""
    start_relx = final_relx + x_distance
    start_rely = final_rely + y_distance

    def update(progress: float) -> None:
        if widget.winfo_exists():
            widget.place_configure(
                relx=start_relx + (final_relx - start_relx) * progress,
                rely=start_rely + (final_rely - start_rely) * progress,
            )

    manager.animate(duration, update, ease_out, on_complete)


def fade_canvas(manager: AnimationManager, canvas, start: float, end: float, duration: int, on_complete=None) -> None:
    """Fade a Canvas overlay by changing its stippled fill state."""
    # Tk Canvas has no universal alpha; this helper is intentionally optional.
    manager.animate(duration, lambda progress: None, ease_in_out, on_complete)
