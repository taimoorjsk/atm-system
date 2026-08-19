"""Beginner-friendly easing functions for values in the 0..1 range."""

from __future__ import annotations


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def linear(t: float) -> float:
    return _clamp(t)


def ease_in(t: float) -> float:
    """Start slowly, then accelerate."""
    t = _clamp(t)
    return t * t


def ease_out(t: float) -> float:
    """Start quickly, then decelerate into the final value."""
    t = _clamp(t)
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t: float) -> float:
    """Accelerate through the middle and decelerate at both ends."""
    t = _clamp(t)
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - ((-2.0 * t + 2.0) ** 3) / 2.0
