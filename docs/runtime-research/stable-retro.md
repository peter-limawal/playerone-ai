# stable-retro Evaluation

## Purpose

This note evaluates whether `stable-retro` is a good first runtime backend for `playerone-ai` v0.

The current `playerone-ai` direction is:

- game: `Super Mario Bros.`
- platform: `NES`
- runtime requirement: local Python integration
- observation requirement: screen-first
- control requirement: controller-state based input

## Conclusion

`stable-retro` is a good fit for the first backend.

It supports the main requirements we care about:

- `SuperMarioBros-Nes-v0` is available as a supported game
- image observations are the default mode
- raw controller-style button arrays are supported through `MultiBinary` action spaces
- the runtime exposes a standard Python environment API with `reset()` and `step()`

The main limitation is that `stable-retro` advances the emulator one step per `env.step(action)`. That means our higher-level "agent chooses when to look again" model will need to be implemented as a wrapper on top of `stable-retro`, not by relying on native library support for asynchronous or agent-controlled attention scheduling.

## What stable-retro Supports Well

### 1. Super Mario Bros. support

The official supported-games list includes `SuperMarioBros-Nes-v0`.

Source:

- https://stable-retro.farama.org/supported_games/

### 2. Screen-first observations

The Python API exposes image observations by default through `obs_type=retro.Observations.IMAGE`. RAM observations are also available, but image observations are the default.

Source:

- https://stable-retro.farama.org/python/

### 3. Controller-style action spaces

`stable-retro` supports multiple action-space modes. The most relevant one for `playerone-ai` is:

- `Actions.ALL`: `MultiBinary` action space with no filtered actions

This is the closest match to a controller-state model because it allows a button-state array rather than forcing a discrete semantic action.

Source:

- https://stable-retro.farama.org/python/
- https://stable-retro.farama.org/main/_modules/retro/enums/

### 4. Per-step button masks

Internally, `RetroEnv.step()` converts the input action into a per-button array and applies it through `self.em.set_button_mask(...)` before stepping the emulator.

This is important because it confirms that the library fundamentally thinks in terms of current button masks, not only high-level discrete actions.

Source:

- https://stable-retro.farama.org/_modules/stable_retro/retro_env/

### 5. Structured info and replay support

If a game integration defines variables in `data.json`, those values appear in the `info` dict after each step. The library can also record `.bk2` replay files containing button presses.

These are useful for later debugging and evaluation, even if `playerone-ai` stays screen-first by default.

Sources:

- https://stable-retro.farama.org/python/
- https://stable-retro.farama.org/main/integration/

## What stable-retro Does Not Solve For Us

### 1. Agent-controlled attention scheduling

`stable-retro` does not provide a concept like:

- ask the agent when it wants to observe the game next

Instead, the environment API is a conventional loop:

- `reset()`
- `step(action)`

Each call to `step(action)` applies a button mask and advances the game.

Implication:

- if `playerone-ai` wants the agent to say "look again in N frames", we must build that scheduling logic in our own runner
- the runner will need to keep applying the held controller state across repeated environment steps until the next observation point

### 2. Observation packet assembly

`stable-retro` gives us raw image observations, but it does not assemble the kind of observation packet we want for LLM-driven play.

`playerone-ai` will still need to build:

- current frame
- recent frame history
- current controller state
- recent interaction context

### 3. Benchmark/runtime separation

`stable-retro` is just the environment backend. It does not define the agent runtime, controller abstraction, logging format, or result contract we want for `playerone-ai`.

That is expected and acceptable, but it means our wrapper layer is still essential.

## Fit Against playerone-ai Requirements

### Requirement: first game should be Super Mario Bros.

Result:

- supported

### Requirement: observation should be screen-first

Result:

- supported directly

### Requirement: control should be controller-state based

Result:

- supported best through `Actions.ALL` / `MultiBinary`

### Requirement: support simultaneous button presses

Result:

- supported by the MultiBinary/button-mask model

### Requirement: allow agent to choose when to look next

Result:

- not native
- must be implemented in `playerone-ai`

## Recommended Integration Strategy

`playerone-ai` should treat `stable-retro` as the low-level game runtime backend only.

That suggests a v0 layering like:

1. `stable-retro` env
2. `playerone-ai` runtime wrapper
3. observation-packet builder
4. agent runtime
5. controller-state scheduler

Concretely:

- `stable-retro` runs the emulator and returns image observations
- `playerone-ai` stores frame history across steps
- the agent returns:
  - controller state
  - requested next-look interval
- the runner repeatedly applies that controller state for the requested number of steps
- after that interval, the runner builds the next observation packet and asks the agent again

## Recommendation

Use `stable-retro` as the first runtime backend for `playerone-ai`.

Reasons:

- it supports `Super Mario Bros.`
- it has the right image-observation default
- it supports controller-like multi-button actions
- it is actively maintained
- it gives us enough low-level control to build our own higher-level runtime abstractions on top

## Local Validation Notes

The first local validation attempt on this machine exposed an implementation risk on Apple Silicon macOS:

- the published `stable-retro` wheel installed for Python 3.12 loaded an `x86_64` native extension, which failed to import under an `arm64` Python interpreter
- a follow-up source build attempt for `stable-retro==0.9.9` also failed during CMake configuration because the build expected a missing `tests/` directory

Implication:

- `stable-retro` is still the leading backend candidate in principle
- but it is not currently plug-and-play on this machine
- before deeper runtime work continues, we may need one of:
  - a compatible wheel or source-build fix from `stable-retro`
  - an x86_64 Python environment under Rosetta
  - a Docker or Linux-based runtime path
  - a fallback emulator/runtime choice if local compatibility remains blocked

This is a local environment constraint, not a rejection of the overall `stable-retro` architecture fit.

## What Other Users Appear To Do

The upstream project and related community resources point to three practical usage patterns:

### 1. Standard local install

The official README recommends:

- `pip3 install stable-retro`
- or `pip3 install git+https://github.com/Farama-Foundation/stable-retro.git`
- or `pip3 install -e .` from a local clone for development

This appears to be the default path on platforms where the native build works cleanly.

### 2. Apple Silicon source build

The official macOS installation guide has a dedicated Apple Silicon section and recommends:

- Python 3.10
- Homebrew dependencies such as `pkg-config`, `lua@5.3`, `libzip`, `qt@5`, and `capnp`
- setting `SDKROOT`
- building from source with `pip install -e .`

This indicates that Apple Silicon users are expected to rely on a more manual build path than the standard wheel install.

### 3. Docker on Apple Silicon

The official macOS installation guide also points Apple Silicon users to a Docker-based alternative.

The linked `stable-retro-docker` project describes using:

- Docker on macOS
- `--platform linux/amd64`
- optional XQuartz display forwarding for GUI support

This is the clearest example of how people work around local macOS / Apple Silicon compatibility issues in practice.

## Current Recommendation For This Repo

For `playerone-ai`, the most practical near-term validation path on this machine is:

1. keep `stable-retro` as the leading backend candidate
2. stop treating the native macOS wheel as the primary setup path
3. validate the backend through a Docker-based Linux environment first

This does not lock the project into Docker forever. It is simply the most reliable way to continue validating the runtime abstraction while avoiding local native build issues on Apple Silicon.

## Sources

- Stable-Retro Python API: https://stable-retro.farama.org/python/
- Stable-Retro supported games: https://stable-retro.farama.org/supported_games/
- Stable-Retro action enums: https://stable-retro.farama.org/main/_modules/retro/enums/
- Stable-Retro `RetroEnv.step()` implementation: https://stable-retro.farama.org/_modules/stable_retro/retro_env/
- Stable-Retro integration docs: https://stable-retro.farama.org/main/integration/
- Stable-Retro README: https://github.com/Farama-Foundation/stable-retro
- Stable-Retro macOS installation guide: https://github.com/Farama-Foundation/stable-retro/blob/master/docs/macos_installation.md
- Apple Silicon Docker example: https://github.com/arvganesh/stable-retro-docker
