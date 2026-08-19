"""Non-blocking animation scheduling built on Tk's after() method."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from .config import ANIMATIONS_ENABLED, FRAME_DELAY
from .easing import ease_out

UpdateCallback = Callable[[float], Any]
DoneCallback = Callable[[], Any]


class AnimationManager:
    """Runs small animations without blocking the Tk event loop."""

    def __init__(self, widget):
        self.widget = widget
        self._jobs: set[str] = set()

    def animate(
        self,
        duration: int,
        update_callback: UpdateCallback,
        easing: Callable[[float], float] = ease_out,
        on_complete: DoneCallback | None = None,
    ) -> str | None:
        if not ANIMATIONS_ENABLED or duration <= 0:
            update_callback(1.0)
            if on_complete:
                on_complete()
            return None

        started = time.perf_counter()
        job_id = f"animation-{id(update_callback)}-{started}"

        def frame() -> None:
            if job_id not in self._jobs or not self.widget.winfo_exists():
                self._jobs.discard(job_id)
                return
            progress = min(1.0, (time.perf_counter() - started) * 1000 / duration)
            update_callback(easing(progress))
            if progress >= 1.0:
                self._jobs.discard(job_id)
                if on_complete:
                    on_complete()
                return
            self.widget.after(FRAME_DELAY, frame)

        self._jobs.add(job_id)
        frame()
        return job_id

    def cancel_all(self) -> None:
        """Invalidate scheduled frames before a screen is rebuilt."""
        self._jobs.clear()
