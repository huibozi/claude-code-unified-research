# Command

## Purpose

Represents a user-triggered named entrypoint such as slash commands, setup commands, or structured CLI actions.

## Core responsibilities

- Give stable names and aliases to user-invokable actions.
- Describe enablement conditions and input contracts.
- Point to the implementation surface that handles the command.
- Support adapter-aware settings surfaces when a runtime collapses command behavior into one configuration object instead of individual named commands.

## Required fields

Shared command fields:

- `source`
- `kind`
- `description`

Named-entrypoint command fields:

- `name`
- `aliases`
- `input_contract`
- `handler_ref`
- `enabled_when`

Settings-surface command fields:

- `id`
- `adapter_shape`
- `settings_payload`

## Optional adapter or compatibility fields

- `adapter_notes`

## Lifecycle or execution semantics

- Commands are resolved before tool calling and often reconfigure runtime state.
- A command may be interactive, noninteractive, setup-oriented, or administrative.
- The same semantic command can have different handler implementations across runtimes.
- Some runtimes expose command control as one singleton settings surface rather than as many named command files.

## Relationships to other objects

- Registered by Runtime registries.
- Often mutates Session state or dispatches into Tool and Task execution.
- May depend on Connector or Policy availability.
- Settings-surface commands often sit close to runtime and policy toggles rather than to user-facing slash commands.

## Evidence from tracked repositories

- `claude-code-source`: `src/commands/`, `src/commands/review`, `src/commands/memory`, `src/commands/config`
- `claude-code-Kuberwastaken`: `spec/02_commands.md`, `src-rust/crates/commands/src/lib.rs`, `src-rust/crates/commands/src/named_commands.rs`
- `claude-code-instructkr`: `src/commands.py`, `src/reference_data/commands_snapshot.json`, `rust/crates/commands/src/lib.rs`
- Research layer: `04-diffs-and-indexes/manifests/source-baseline.manifest.md`

## Open parity notes

- TypeScript has the broadest command surface by far.
- Both rewrites compress command breadth but preserve the need for a registry and stable command semantics.
- Live downstream OpenClaw work confirms that command settings surfaces should be modeled as a `Command` variant rather than forced into fake per-command files.
