# playerone-ai

`playerone-ai` is the runtime layer for letting AI agents play video games through a clean, reusable interface.

This repository is not the benchmark suite. It is the library and reference implementation that:

- connects game environments to agent runtimes
- connects agent runtimes to underlying LLM backends
- provides the control loop for one agent playing one game
- emits structured logs and episode summaries for downstream evaluation

The evaluation and model-comparison layer lives in `playerone-arena`.

## Purpose

The goal of `playerone-ai` is to make game-playing agents composable.

It should be possible to plug together:

- one game environment
- one agent runtime
- one underlying model backend
- optional learning or memory tools

without coupling those pieces to benchmark logic, leaderboards, or experiment orchestration.

## Repository Boundary

`playerone-ai` owns:

- environment abstractions
- game-specific adapters
- agent interfaces and runtime loops
- model backend adapters
- perception and state formatting
- structured logging for runs

`playerone-ai` does not own:

- cross-model benchmarks
- repeated trial orchestration
- result aggregation
- scoreboards or leaderboards
- evaluation dashboards or reports

Those belong in `playerone-arena`.

## Relationship to playerone-arena

The intended split is:

- `playerone-ai`: "make one agent play one game"
- `playerone-arena`: "compare many models and agent configurations using playerone-ai"

`playerone-arena` should depend on `playerone-ai`, not the other way around.

## Early Direction

The first concrete direction is to support a local agent playing a single game end to end on one machine.

Current assumptions:

- local execution only
- Python 3.11+
- one game integration first
- one model backend first
- extensible interfaces so more games and models can be added later

## Architecture

The current package is organized around these responsibilities:

- `playerone.envs`: emulator-backed environments
- `playerone.agent`: agent runtime and policy loop
- `playerone.llm`: model backend adapters
- `playerone.perception`: observation-to-text or state shaping helpers
- `playerone.utils`: logging and support utilities

This structure will continue to evolve toward a more library-first interface as the abstractions settle.

## Current Status

This repo is still in the setup stage.

There is early prototype code for:

- a retro environment wrapper
- a simple LLM-driven agent loop
- a local model client interface
- JSONL episode logging

That code is a starting point, not the final architecture.

## Development Principle

The core requirement for this repo is separation of concerns.

Game execution, agent behavior, model inference, and evaluation must remain separable so `playerone-ai` stays reusable as the execution engine underneath `playerone-arena`.
