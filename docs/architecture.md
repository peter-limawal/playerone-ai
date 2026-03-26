# playerone-ai Architecture

## Purpose

`playerone-ai` is the runtime and abstraction layer for letting one AI agent play one video game through a reusable interface.

This repository is responsible for executing gameplay, exposing observations, accepting agent decisions, applying game inputs, and emitting structured run data.

This repository is not responsible for cross-model evaluation, repeated benchmark orchestration, or leaderboard logic. Those concerns belong in `playerone-arena`.

## v0 Direction

The current v0 direction is:

- game: `Super Mario Bros.`
- emulator/runtime candidate: `stable-retro`
- execution model: local only
- primary observation mode: screen-first
- primary control mode: controller-state based

The exact runtime backend can change if implementation constraints force a better choice, but the working direction is NES-era Mario through a locally automated emulator.

## System Overview

`playerone-ai` is currently designed around four major parts:

1. Game Runtime
2. Observation / Perception Layer
3. Agent Runtime
4. Control / Interaction Layer

These parts should remain separable so the runtime can support different games, models, and future evaluation layers without rewriting the whole stack.

## 1. Game Runtime

The game runtime is responsible for running the game itself.

Responsibilities:

- boot the game or emulator
- load the ROM or game state
- reset the episode
- advance the game frame by frame
- capture rendered frames
- expose episode lifecycle information such as reset, termination, and runtime status

Non-responsibilities:

- choosing actions
- formatting prompts for models
- benchmark aggregation
- model-specific inference logic

The game runtime should expose the game as a continuously advancing system. It should not assume anything about how the agent thinks, only how the game is stepped and observed.

## 2. Observation / Perception Layer

The observation layer is responsible for deciding what the agent gets to see at each decision point.

Responsibilities:

- capture screen observations from the runtime
- assemble an observation packet for the agent
- include temporal context so the agent can infer motion and state change
- optionally include runtime metadata when appropriate

Non-responsibilities:

- deciding what action to take
- directly applying controller input

The default observation strategy is screen-first. The agent should primarily act from what it sees on screen rather than hidden emulator memory.

For v0, the observation packet is expected to include:

- the current frame
- a short recent frame history
- the current controller state
- recent interaction context if needed

Structured emulator metadata may be attached later, but it should not be the default source of truth for gameplay.

## 3. Agent Runtime

The agent runtime is responsible for turning observations into gameplay decisions.

Responsibilities:

- receive an observation packet
- reason about the next control state
- optionally determine when it wants to observe the game again
- maintain internal memory or learned notes if the agent supports it
- return decisions in a stable schema

Non-responsibilities:

- stepping the emulator directly
- translating generic button states into backend-specific emulator calls
- benchmark comparison across models

The key design idea is that the agent should not only decide what buttons to hold, but may also decide when it wants its next observation.

This allows the runtime to model a more human-like loop:

- observe the game
- choose a controller state
- let the game continue
- observe again when enough may have changed

## 4. Control / Interaction Layer

The control layer is responsible for translating agent decisions into actual game inputs.

Responsibilities:

- define the public controller schema
- validate or pass through controller states
- translate controller-state changes into emulator-specific input operations
- preserve held-button behavior over time

Non-responsibilities:

- deciding which buttons should be pressed
- interpreting game outcomes

The public control surface should be based on controller state, not imperative event calls.

That means the agent should conceptually express:

- which buttons are currently held

rather than issuing low-level commands like:

- press button A
- release button A

Internally, the emulator adapter may still convert controller-state changes into press and release events, but those are implementation details of the control layer.

## Controller-State Model

The input model should reflect how retro controllers are effectively sampled by games.

At any moment, the important question is:

- which buttons are down right now

not:

- which button event fired first

This means simultaneous inputs such as `RIGHT + A` should be represented as one controller state with multiple active buttons.

The interface should be generic enough to support multiple platforms later, while the first concrete implementation can map directly to the NES controller layout used by `Super Mario Bros.`.

## Decision Model

The current preferred decision contract is:

- next controller state
- requested number of frames until the next observation

This lets the agent influence both:

- control
- attention

The runtime should still retain authority over safety and stability, including enforcement of timing bounds if needed.

## Core Contracts

The exact code-level schemas are not finalized yet, but the architecture expects stable contracts equivalent to:

- `ObservationPacket`
- `ControllerState`
- `AgentDecision`
- `EpisodeResult`

Their intended meanings are:

- `ObservationPacket`: what the agent sees at a decision point
- `ControllerState`: which buttons are currently held
- `AgentDecision`: the next controller state and the requested next observation interval
- `EpisodeResult`: structured summary of what happened during a run

## Logging and Run Outputs

Even though evaluation belongs in `playerone-arena`, `playerone-ai` must still emit structured outputs that other systems can consume.

At minimum, the runtime should eventually produce:

- per-decision observations or references to them
- controller decisions
- timing information
- episode summary data
- failure or termination information

This output contract is important because `playerone-arena` will depend on it later for standardized evaluation.

## Relationship to playerone-arena

The intended split between the two repositories is:

- `playerone-ai`: execute gameplay
- `playerone-arena`: evaluate and compare gameplay runs

`playerone-ai` should be usable independently for local play and runtime development. `playerone-arena` should consume its abstractions and outputs without forcing benchmark concerns back into the runtime layer.

## Open Questions

The following questions are still intentionally open:

- what exact observation packet format is best for Mario-like games
- how many prior frames should be included by default
- what minimum and maximum observation intervals the runtime should enforce
- how much optional emulator metadata should be exposed in addition to screen observations
- how closely the first controller schema should match the exact NES layout in code

These questions should be resolved as implementation begins, but they should not block agreement on the high-level runtime boundaries.
