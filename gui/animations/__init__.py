"""Small, non-blocking animation helpers for the CustomTkinter GUI."""

from .config import ANIMATIONS_ENABLED
from .easing import ease_in, ease_in_out, ease_out, linear
from .manager import AnimationManager

__all__ = [
    "ANIMATIONS_ENABLED",
    "AnimationManager",
    "ease_in",
    "ease_in_out",
    "ease_out",
    "linear",
]
