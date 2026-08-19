# ATM GUI Animations

The animation code lives under `gui/animations/` and only talks to the GUI. The banking and database layers do not depend on it.

## How frames work

Tkinter's `after(milliseconds, callback)` asks the event loop to call a function later. `AnimationManager` uses this to update one frame about every 20 milliseconds. It never calls `time.sleep()`, so typing and button clicks remain responsive.

Each animation measures elapsed time, converts it to a value from 0 to 1, applies an easing function, and calls the update callback. The manager tracks jobs so a rebuilt screen can invalidate old callbacks.

## Easing

- `linear(t)` moves at a constant rate.
- `ease_in(t)` starts slowly and accelerates.
- `ease_out(t)` starts quickly and decelerates into place. It is used for panel and logo entrances.
- `ease_in_out(t)` eases at both ends. It is used for handoff timing and is useful for balanced transitions.

## Customization

Change durations and frame timing in `gui/animations/config.py`. The main values are `BOOT_DURATION`, `SCREEN_TRANSITION_DURATION`, `SESSION_TRANSITION_DURATION`, and `FRAME_DELAY`.

Set `ANIMATIONS_ENABLED = False` while debugging or running on a slower computer. The manager immediately applies the final state and calls completion callbacks.

The placeholder logo is drawn by `gui/animations/logo.py`, so replacing that class with an image-backed logo is the single place to add an asset. Put future image files under `assets/logo/` and keep theme-specific colors in the existing palette in `gui/persistent_app.py`.

To add an animation, create a small update function that accepts a progress value, then call `AnimationManager.animate(duration, update, easing, on_complete)`.
