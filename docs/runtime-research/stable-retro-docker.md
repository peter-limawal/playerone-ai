# stable-retro Docker Validation

## Purpose

This note defines the container-based validation path for `stable-retro` on Apple Silicon macOS.

The local native installation attempt on this machine failed because:

- the published wheel loaded an incompatible `x86_64` extension under `arm64`
- the source build also failed locally

Given that upstream documentation and community examples point Apple Silicon users toward source builds or Docker, the Docker path is the most practical next validation step.

## Why Docker

Using Docker gives us:

- a Linux runtime instead of a macOS native runtime
- a reproducible environment for backend validation
- separation between `playerone-ai` runtime logic and local machine dependency quirks

This does not mean `playerone-ai` must always run in Docker. It means Docker is currently the safest validation path for the first backend on this machine.

## Repo Assets

This repo includes:

- `Dockerfile.stable-retro`

The Dockerfile is intentionally minimal. Its purpose is to:

- install Python and build tools
- install `playerone-ai` with the `stable-retro` extra
- run the smoke test script

It is not yet a full development or rendering environment.

## Proposed Validation Steps

1. Build the image:

```bash
docker build -t playerone-ai-stable-retro -f Dockerfile.stable-retro .
```

2. Run the smoke test in the container:

```bash
docker run --rm playerone-ai-stable-retro
```

3. After the smoke test passes, extend the validation to:

- create a real `StableRetroBackend`
- import the appropriate ROM into the container runtime
- test `reset()` against `SuperMarioBros-Nes`

## Notes

- if Docker is running on Apple Silicon, it may still be necessary to force a Linux `amd64` platform depending on `stable-retro` compatibility
- if rendering is needed later, GUI/display support should be handled as a separate step
- ROM import and legal acquisition remain outside the scope of this doc

## Current Goal

The current goal is not full gameplay in Docker. The goal is to prove that `playerone-ai` can load and use a compatible `stable-retro` backend in a reproducible environment before we continue building the runner and observation layers.
