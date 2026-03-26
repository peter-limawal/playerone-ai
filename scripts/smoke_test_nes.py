"""Minimal smoke test for the NES backend adapter."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playerone_ai.backends.nes import NES_BUTTON_ORDER, NESControllerBackend
from playerone_ai.controls import ControllerState


def main() -> None:
    print(f"NES button order: {NES_BUTTON_ORDER}")

    try:
        backend = NESControllerBackend()
    except ImportError as exc:
        print(f"nes backend not installed: {exc}")
        return

    print(f"Configured env: {backend.env_id}")
    print(
        "RIGHT+A raw action:",
        backend.controller_state_to_action(ControllerState(right=True, a=True)),
    )

    try:
        observation, info = backend.reset()
        print("reset ok")
        print("observation shape:", getattr(observation, "shape", None))
        print("info keys:", sorted(info.keys()))
        print("raw action space size:", backend.get_action_space_size())
    finally:
        backend.close()


if __name__ == "__main__":
    main()
