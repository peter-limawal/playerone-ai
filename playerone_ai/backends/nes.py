"""NES backend adapter built on top of gym-super-mario-bros / nes-py."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from playerone_ai.controls import ControllerState

try:
    import gym_super_mario_bros
except ImportError as exc:  # pragma: no cover - optional dependency
    gym_super_mario_bros = None
    _IMPORT_ERROR_REASON = str(exc)
else:
    _IMPORT_ERROR_REASON = None


NES_BUTTON_ORDER = (
    "right",
    "left",
    "down",
    "up",
    "start",
    "select",
    "b",
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


class NESControllerBackend:
    """Thin adapter around the raw Super Mario Bros. NES environment."""

    def __init__(self, env_id: str = "SuperMarioBros-v0") -> None:
        self.env_id = env_id
        self._env: Any | None = None

        if gym_super_mario_bros is None:
            raise ImportError(
                "gym-super-mario-bros is required for NESControllerBackend. "
                "Install it with `pip install -e .[nes]`. "
                f"Import failure detail: {_IMPORT_ERROR_REASON}"
            )

    def reset(self) -> tuple[np.ndarray, dict[str, Any]]:
        """Create the environment if needed and reset the episode."""
        if self._env is None:
            self._env = gym_super_mario_bros.make(self.env_id)

        reset_out = self._env.reset()
        if isinstance(reset_out, tuple):
            observation, info = reset_out
        else:
            observation, info = reset_out, {}
        return observation, dict(info)

    def step(self, controller_state: ControllerState) -> StepResult:
        """Advance the environment by one step using the given controller state."""
        env = self._require_env()
        action = self.controller_state_to_action(controller_state)
        step_out = env.step(action)

        if len(step_out) == 5:
            observation, reward, terminated, truncated, info = step_out
        else:
            observation, reward, done, info = step_out
            terminated = bool(done)
            truncated = False

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

    def controller_state_to_action(self, controller_state: ControllerState) -> int:
        """Convert ControllerState into the raw 8-bit NES action integer."""
        bit_lookup = {
            "right": controller_state.right,
            "left": controller_state.left,
            "down": controller_state.down,
            "up": controller_state.up,
            "start": controller_state.start,
            "select": controller_state.select,
            "b": controller_state.b,
            "a": controller_state.a,
        }
        action = 0
        for bit_index, button in enumerate(reversed(NES_BUTTON_ORDER)):
            if bit_lookup[button]:
                action |= 1 << bit_index
        return action

    def get_action_space_size(self) -> int:
        """Return the size of the raw controller action space."""
        env = self._require_env()
        return int(env.action_space.n)

    def _require_env(self) -> Any:
        if self._env is None:
            raise RuntimeError("Backend is not initialized. Call reset() first.")
        return self._env
