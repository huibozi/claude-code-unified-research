# Command

## Purpose

Represents a user-triggered named entrypoint such as slash commands, setup commands, or structured CLI actions.

## Core responsibilities

- Give stable names and aliases to user-invokable actions.
- Describe enablement conditions and input contracts.
- Point to the implementation surface that handles the command.

## Required fields

- `name`
- `aliases`
- `source`
- `kind`
- `description`
- `input_contract`
- `handler_ref`
- `enabled_when`

## Lifecycle or execution semantics

- Commands are resolved before tool calling and often reconfigure runtime state.
- A command may be interactive, noninteractive, setup-oriented, or administrative.
- The same semantic command can have different handler implementations across runtimes.

## Relationships to other objects

- Registered by Runtime registries.
- Often mutates Session state or dispatches into Tool and Task execution.
- May depend on Connector or Policy availability.

## Evidence from tracked repositories

- `claude-code-source`: `src/commands/`, `src/commands/review`, `src/commands/memory`, `src/commands/config`
- `claude-code-Kuberwastaken`: `spec/02_commands.md`, `src-rust/crates/commands/src/lib.rs`, `src-rust/crates/commands/src/named_commands.rs`
- `claude-code-instructkr`: `src/commands.py`, `src/reference_data/commands_snapshot.json`, `rust/crates/commands/src/lib.rs`
- Research layer: `04-diffs-and-indexes/manifests/source-baseline.manifest.md`

## Open parity notes

- TypeScript has the broadest command surface by far.
- Both rewrites compress command breadth but preserve the need for a registry and stable command semantics.
