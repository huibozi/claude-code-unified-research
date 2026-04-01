# Connector

## Purpose

Represents external integrations such as MCP servers, bridges, remote runtimes, channels, and webhooks.

## Core responsibilities

- Describe transport, authentication mode, capabilities, and resource contracts.
- Normalize external systems into a runtime-usable integration shape.
- Provide health state that the runtime can inspect before use.

## Required fields

- `id`
- `kind`
- `transport`
- `capabilities`
- `auth_mode`
- `resource_contracts`
- `health_state`

## Lifecycle or execution semantics

- Connectors may expose tools, resources, commands, or notifications.
- Connector health is dynamic and should be observable.
- Runtime and session layers may filter connectors based on policy and environment.

## Relationships to other objects

- Registered by Runtime and required by Agent definitions.
- Often back Tool execution and remote Task flows.
- Constrained by Policy and surfaced to Session status.

## Evidence from tracked repositories

- `claude-code-source`: `src/services/mcp/client.ts`, `src/bridge/bridgeMain.ts`, `src/remote/`
- `claude-code-Kuberwastaken`: `spec/09_bridge_cli_remote.md`, `src-rust/crates/mcp/src/lib.rs`, `src-rust/crates/bridge/src/lib.rs`
- `claude-code-instructkr`: `src/remote_runtime.py`, `rust/crates/runtime/src/mcp.rs`, `rust/crates/runtime/src/remote.rs`
- Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`

## Open parity notes

- The source baseline remains the richest reference for MCP client lifecycle and bridge integration.
- Both rewrites prove that connectors can be normalized as a first-class runtime object.
