# Runtime

## Purpose

Defines the top-level execution environment that owns registries, state, policy, and connector wiring.

## Core responsibilities

- Boot the system and hold immutable identity such as name and version.
- Expose registries for commands, tools, skills, and agents.
- Bind state storage, policy storage, and connector registration into one runtime context.

## Required fields

- `id`
- `name`
- `version`
- `registries`
- `state_store`
- `policy_store`
- `connector_registry`
- `feature_flags`

## Lifecycle or execution semantics

- A runtime exists before any session begins.
- Feature flags and connector availability shape the capabilities exposed to sessions and agents.
- Downstream implementations may host more than one runtime, but every session must point at exactly one runtime.

## Relationships to other objects

- Parents Session through `runtime_id`.
- Owns the registries consumed by Command, Tool, Skill, Agent, and Connector.
- Delegates policy decisions to Policy and memory access to Memory stores.

## Evidence from tracked repositories

- `claude-code-source`: `src/main.tsx`, `src/entrypoints/cli.tsx`, `src/tools.ts`
- `claude-code-Kuberwastaken`: `spec/00_overview.md`, `spec/13_rust_codebase.md`, `src-rust/crates/cli/src/main.rs`
- `claude-code-instructkr`: `src/main.py`, `src/runtime.py`, `rust/crates/rusty-claude-cli/src/main.rs`
- Research layer: `04-diffs-and-indexes/manifests/source-baseline.manifest.md`, `03-specs-and-parity/module-matrices/repository-capability-matrix.md`

## Open parity notes

- Kuberwastaken compresses runtime semantics into crate boundaries and spec topics rather than a giant app shell.
- instructkr preserves a runtime surface but does not yet match full TypeScript breadth.
