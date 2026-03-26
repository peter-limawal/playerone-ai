# playerone-ai Interfaces

## Purpose

This document defines the first concrete runtime contracts for `playerone-ai`.

These interfaces are intended to be stable enough to guide initial implementation while still leaving room for refinement as the first backend is built.

The current v0 assumptions are:

- game: `Super Mario Bros.`
- backend: `stable-retro`
- observation mode: screen-first
- control mode: controller-state based
- execution model: local only

## Design Principles

The first interface set follows these principles:

- the game backend should remain replaceable
- the agent should not talk to the backend directly
- the public input surface should reflect a controller, not semantic actions
- the agent should be able to influence when it wants to observe the game again
- run outputs should be structured enough for `playerone-arena` to consume later

## 1. ControllerState

`ControllerState` is the canonical input surface for the agent.

It represents which buttons are currently held at a decision point.

### Responsibility

`ControllerState` should:

- represent button state, not button events
- support simultaneous button presses
- stay generic enough to map to multiple platforms later
- be simple to convert into backend-specific input masks

### Intended Shape

The first version should support a standard retro controller layout:

- `up`
- `down`
- `left`
- `right`
- `a`
- `b`
- `start`
- `select`

Each field is a boolean indicating whether that button is currently held.

### Notes

- invalid or unhelpful combinations such as `left + right` are allowed at the interface level
- backend adapters may still need to normalize or reject states they cannot represent
- the first concrete implementation should map this schema to the NES controller layout needed for `Super Mario Bros.`

## 2. ObservationPacket

`ObservationPacket` is the complete input the agent receives at each decision point.

It is not a raw backend response. It is a `playerone-ai` runtime object assembled for agent use.

### Responsibility

`ObservationPacket` should:

- expose the current visible game state
- include enough temporal context for the agent to reason about motion
- include the current or recent control context
- stay backend-agnostic at the interface level

### Intended Contents

The first version should contain:

- `current_frame`
- `recent_frames`
- `current_controller_state`
- `frames_since_last_observation`
- `decision_index`

Optional fields may be added later for:

- recent decision history
- backend info fields
- episode metadata

### Notes

- screen content is the primary source of truth
- hidden emulator state should remain optional and off by default
- recent frames should be treated as temporal context, not as an implementation detail of the backend

## 3. AgentDecision

`AgentDecision` is the structured output returned by the agent at each decision point.

### Responsibility

`AgentDecision` should let the agent control:

- what buttons to hold next
- when it wants to observe the game again

### Intended Contents

The first version should contain:

- `controller_state`
- `next_look_after_frames`

### Notes

- `next_look_after_frames` expresses attention scheduling, not just button duration
- the runtime should enforce safety bounds on this value
- the controller state stays active until the runtime reaches the next observation point or overrides it for safety reasons

## 4. EpisodeResult

`EpisodeResult` is the structured summary returned after one completed run.

### Responsibility

`EpisodeResult` should capture enough run information to:

- understand what happened locally
- support future evaluation in `playerone-arena`

### Intended Contents

The first version should contain:

- `episode_id`
- `decision_count`
- `frame_count`
- `terminated`
- `truncated`
- `final_info`

Optional fields may later include:

- score
- progress metrics
- death count
- timing summary

### Notes

- the exact metric set will depend on the game and backend integration
- `EpisodeResult` is a runtime output contract, not a full benchmark report

## 5. Runner Contract

The runner is the orchestration layer that connects the backend, observation builder, agent, and control state.

### Responsibility

The runner should:

- reset the backend
- build the first observation packet
- call the agent for an `AgentDecision`
- apply the chosen controller state through the backend
- continue stepping the game while holding that controller state
- stop after the requested number of frames
- build the next observation packet
- repeat until termination or truncation

### Why the Runner Owns Scheduling

`stable-retro` only supports a conventional `step(action)` loop.

That means the runner must be the layer that implements:

- held controller state across multiple backend steps
- agent-controlled observation cadence

The backend remains a low-level game runtime. The runner creates the higher-level gameplay loop we actually want.

## 6. Backend Adapter Contract

The backend adapter is the boundary between `playerone-ai` and a concrete runtime such as `stable-retro`.

### Responsibility

The backend adapter should:

- initialize the backend environment
- convert `ControllerState` into the backend action format
- step the backend once
- return frame observations and termination status
- expose backend info in a controlled way

### Non-responsibility

The backend adapter should not:

- choose observation cadence
- decide actions
- own memory or learning logic

## 7. First Implementation Mapping

For the first concrete backend:

- `ControllerState` maps to the button-mask format required by `stable-retro`
- `ObservationPacket.current_frame` comes from the image observation returned by the environment
- `ObservationPacket.recent_frames` is assembled by `playerone-ai`, not by `stable-retro`
- `AgentDecision.next_look_after_frames` is interpreted by the runner, not by `stable-retro`

This is the core architectural consequence of choosing `stable-retro`.

## Open Questions

The following details remain intentionally open:

- how many recent frames should be included by default
- the exact minimum and maximum values allowed for `next_look_after_frames`
- whether recent decision history should be part of `ObservationPacket` from day one
- how much backend `info` should be copied into the observation packet versus reserved for logs

These questions should be resolved during the first implementation slice, but they do not change the core contract boundaries described here.
