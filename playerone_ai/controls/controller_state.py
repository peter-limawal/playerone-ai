"""Controller-state abstractions for playerone-ai."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ControllerState:
    """Represents the currently held buttons on a retro-style controller."""

    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    a: bool = False
    b: bool = False
    start: bool = False
    select: bool = False

    def to_button_names(self) -> list[str]:
        """Return the pressed button names in a stable order."""
        ordered_buttons = (
            ("up", self.up),
            ("down", self.down),
            ("left", self.left),
            ("right", self.right),
            ("a", self.a),
            ("b", self.b),
            ("start", self.start),
            ("select", self.select),
        )
        return [name for name, pressed in ordered_buttons if pressed]
