# nes-py Evaluation

## Purpose

This note records the evaluation of `nes-py` and `gym-super-mario-bros` as the first working `Super Mario Bros.` runtime backend for `playerone-ai`.

## Conclusion

`nes-py` is currently the best practical v0 backend for this repository.

Reasons:

- it installs successfully on this machine
- `SuperMarioBros-v0` can be created locally
- it returns screen observations directly
- the unwrapped environment exposes the full raw NES controller space as `Discrete(256)`
- it supports the exact first game we want to target

## What Works

### 1. Local installation

The following packages installed successfully in the repo virtualenv:

- `nes-py`
- `gym-super-mario-bros`

The environment required `numpy<2` because the older Gym stack used by this backend is not compatible with NumPy 2.x.

### 2. Environment creation

The backend can create:

- `SuperMarioBros-v0`

and reset it successfully.

### 3. Observation shape

The environment returns screen observations with shape:

- `(240, 256, 3)`

This is a good fit for the current screen-first observation model.

### 4. Raw controller-space access

The unwrapped environment exposes:

- `Discrete(256)`

This corresponds to the full 8-button NES controller bitmap space.

That means `playerone-ai` does not need to rely on the convenience movement wrappers like:

- `RIGHT_ONLY`
- `SIMPLE_MOVEMENT`
- `COMPLEX_MOVEMENT`

Those wrappers are optional layers on top of the raw controller space.

## Why This Fits playerone-ai

`playerone-ai` wants:

- raw controller-state input
- screen-first observations
- one working local backend before further abstraction

`nes-py` gives us all three today.

That makes it a stronger v0 backend choice than `stable-retro`, which remains attractive architecturally but is currently blocked by build and compatibility issues in this environment.

## Important Limitations

This backend also has real constraints:

- it depends on the older `gym` stack rather than `gymnasium`
- it currently emits compatibility warnings in modern Python environments
- some API behavior is older-style, such as `reset()` returning only an observation instead of `(obs, info)`

These are manageable for v0, but they should be kept behind `playerone-ai` interfaces so the rest of the system does not depend on Gym-specific behavior.

## NES Controller Encoding

The validated button layout is:

- `right`
- `left`
- `down`
- `up`
- `start`
- `select`
- `b`
- `a`

The raw action space is effectively the 8-bit bitmap over those buttons.

For example:

- `RIGHT + A` maps to the integer value `129`

This is a good match for the controller-state model already defined in `playerone-ai`.

## Recommendation

Use `nes-py` / `gym-super-mario-bros` as the first concrete backend for `playerone-ai`.

Keep `stable-retro` as a research or future backend candidate, not the current implementation foundation.
