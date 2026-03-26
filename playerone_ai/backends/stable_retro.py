"""stable-retro backend adapter for playerone-ai."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from playerone_ai.controls import ControllerState

try:
    import stable_retro as retro
except ImportError:  # pragma: no cover - optional dependency
    retro = None


NES_BUTTON_ORDER = (
    "b",
    "select",
    "start",
    "up",
    "down",
    "left",
    "right",
    "a",
)


@dataclass(slots=True)
class StepResult:
    """One backend step result."""

    observation: np.ndarray
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, Any]


class StableRetroBackend:
    """Thin adapter around a stable-retro environment."""

    def __init__(self, game: str = "SuperMarioBros-Nes") -> None:
        self.game = game
        self._env: Any | None = None

        if retro is None:
            raise ImportError(
                "stable-retro is required for StableRetroBackend. "
                "Install it with `pip install -e .[stable-retro]`."
            )

    def reset(self) -> tuple[np.ndarray, dict[str, Any]]:
        """Create the environment if needed and reset the episode."""
        if self._env is None:
            self._env = retro.make(
                game=self.game,
                obs_type=retro.Observations.IMAGE,
                use_restricted_actions=retro.Actions.ALL,
            )
        observation, info = self._env.reset()
        return observation, dict(info)

    def step(self, controller_state: ControllerState) -> StepResult:
        """Advance the environment by one step using the given controller state."""
        env = self._require_env()
        action = self.controller_state_to_action(controller_state)
        observation, reward, terminated, truncated, info = env.step(action)
        return StepResult(
            observation=observation,
            reward=float(reward),
            terminated=bool(terminated),
            truncated=bool(truncated),
            info=dict(info),
        )

    def close(self) -> None:
        """Close the underlying environment if it exists."""
        if self._env is not None:
            self._env.close()
            self._env = None

    def controller_state_to_action(self, controller_state: ControllerState) -> np.ndarray:
        """Convert ControllerState into the NES button-mask format expected by stable-retro."""
        button_lookup = {
            "up": controller_state.up,
            "down": controller_state.down,
            "left": controller_state.left,
            "right": controller_state.right,
            "a": controller_state.a,
            "b": controller_state.b,
            "start": controller_state.start,
            "select": controller_state.select,
        }
        return np.array(
            [int(button_lookup[button]) for button in NES_BUTTON_ORDER],
            dtype=np.int8,
        )

    def _require_env(self) -> Any:
        if self._env is None:
            raise RuntimeError("Backend is not initialized. Call reset() first.")
        return self._env
