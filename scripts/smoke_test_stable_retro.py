"""Minimal smoke test for the stable-retro backend adapter."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playerone_ai.backends.stable_retro import NES_BUTTON_ORDER, StableRetroBackend
from playerone_ai.controls import ControllerState


def main() -> None:
    print(f"NES button order: {NES_BUTTON_ORDER}")

    try:
        backend = StableRetroBackend()
    except ImportError as exc:
        print(f"stable-retro not installed: {exc}")
        return

    print(f"Configured game: {backend.game}")
    print(
        "RIGHT+A action mask:",
        backend.controller_state_to_action(ControllerState(right=True, a=True)).tolist(),
    )


if __name__ == "__main__":
    main()
