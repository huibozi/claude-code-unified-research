# Connector

## Purpose

Represents external integrations such as MCP servers, bridges, remote runtimes, channels, and webhooks.

## Core responsibilities

- Describe transport, authentication mode, capabilities, and resource contracts.
- Normalize external systems into a runtime-usable integration shape.
- Provide health state that the runtime can inspect before use.
- Carry adapter config when channel- or plugin-backed connectors expose nested runtime-specific semantics.

## Required fields

- `id`
- `kind`
- `transport`
- `capabilities`
- `auth_mode`
- `resource_contracts`
- `health_state`

## Optional adapter or compatibility fields

- `description`
- `auth_refs`
- `adapter_config`
- `provider_plugin`
- `binding_refs`
- `adapter_notes`

## Lifecycle or execution semantics

- Connectors may expose tools, resources, commands, or notifications.
- Connector health is dynamic and should be observable.
- Runtime and session layers may filter connectors based on policy and environment.
- Channel connectors often carry nested account or group configuration that should remain in adapter-owned config fields.
- Plugin-backed capability surfaces may appear as connector-adjacent metadata rather than as standalone transport objects.
- Channel-like routing surfaces may reference connectors indirectly through `connector_refs[]` while keeping their own runtime-specific sub-surfaces in adapter-owned fields.

## Relationships to other objects

- Registered by Runtime and required by Agent definitions.
- Often back Tool execution and remote Task flows.
- Constrained by Policy and surfaced to Session status.
- May be targeted by Policy routing rules or referenced by runtime-specific binding families.
- May be referenced by adapter-owned routing surfaces through `connector_refs[]` without forcing those routing surfaces into the core object set.

## Evidence from tracked repositories

- `claude-code-source`: `src/services/mcp/client.ts`, `src/bridge/bridgeMain.ts`, `src/remote/`
- `claude-code-Kuberwastaken`: `spec/09_bridge_cli_remote.md`, `src-rust/crates/mcp/src/lib.rs`, `src-rust/crates/bridge/src/lib.rs`
- `claude-code-instructkr`: `src/remote_runtime.py`, `rust/crates/runtime/src/mcp.rs`, `rust/crates/runtime/src/remote.rs`
- Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`

## Open parity notes

- The source baseline remains the richest reference for MCP client lifecycle and bridge integration.
- Both rewrites prove that connectors can be normalized as a first-class runtime object.
- Live downstream OpenClaw work confirms that channels are a strong `Connector` subtype and that plugin/provider linkage needs adapter-aware connector metadata.
- Live downstream OpenClaw Phase 2 work confirms that explicit connector reference edges are a stable shared pattern even when the owning channel-like surfaces remain adapter-specific.
