# Policy

## Purpose

Captures allow, deny, ask, danger-filter, and audit rules that shape what the runtime may do.

## Core responsibilities

- Centralize permission decisions and danger filters.
- Provide explicit audit requirements for risky actions.
- Separate policy expression from tool implementation.
- Allow adapter-aware routing or binding rules when a runtime uses policy-adjacent match-and-dispatch declarations.

## Required fields

- `id`
- `description`
- `scope`
- `priority`
- `allow_rules`
- `deny_rules`
- `ask_rules`
- `danger_filters`
- `audit_requirements`

## Optional adapter or compatibility fields

- `routing_rules`
- `adapter_notes`

## Lifecycle or execution semantics

- Policy applies at runtime, session, and agent levels.
- Not every denial should be static; some actions route through an ask-policy path.
- Audit requirements should survive even when execution is automated.
- Some runtimes carry routing or binding rules next to policy-like concerns such as priority, scope, and dispatch constraints.
- When a runtime exposes binding-like routing declarations, `routing_rules` may carry a structured `match` object with stable cross-runtime fields such as `channel`, `account`, `pattern`, `pattern_mode`, and `context`.
- Current stable routing actions are modeled as a discriminated `action` object. The only normalized action variant currently promoted into the shared spec is `type = forward_to_agent` with `agent_id`.
- Policy may also express stable access-control semantics for shared resources through:
  - `readers`
  - `writers`
  - `shared_with`
- These access-control fields are broad enough to cover memory surfaces and similar shared runtime resources without forcing a runtime-specific policy subtype into the core model.
- `rebuild_rights` is intentionally not promoted into the core policy schema yet. It remains an adapter extension until more than one runtime proves that lifecycle-control vocabulary is shared.
- Structured retention belongs on `Memory`, not on `Policy`, even when policy constrains who may interact with a retained surface.

## Relationships to other objects

- Consumed by Runtime, Session, Agent, Tool, and Connector flows.
- Interacts with Task scheduling and Memory retention.
- Provides the governance boundary for dangerous operations.
- May also host routing extensions that connect connector or event matches to target agents or command surfaces.
- May be referenced from routing-capable adapter surfaces through `policy_refs[]` without requiring those surfaces to become new core object types.
- May be referenced from memory-capable adapter surfaces through `policy_refs[]` when a runtime exposes first-class memory surface declarations.

## Evidence from tracked repositories

- `claude-code-source`: `src/utils/permissions/permissionSetup.ts`, `src/services/tools/toolOrchestration.ts`, `src/commands/permissions/`
- `claude-code-Kuberwastaken`: `spec/05_components_agents_permissions_design.md`, `src-rust/crates/core/src/lib.rs`
- `claude-code-instructkr`: `src/permissions.py`, `rust/crates/runtime/src/permissions.rs`, `PARITY.md`
- Research layer: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`

## Open parity notes

- The source baseline shows the widest policy and permission surface.
- Derivative repositories preserve the concept but not the full TS policy ecosystem.
- Live downstream OpenClaw work confirms that runtime-specific bindings can be carried as `Policy`-adjacent routing extensions without expanding the core object set.
- Live downstream OpenClaw Phase 2 work further confirms that `pattern_mode = literal | glob | regex` and discriminated routing `action` payloads are stable enough to promote into the shared routing-extension semantics.
- Live downstream OpenClaw Phase 3 work further confirms that `readers`, `writers`, and `shared_with` are stable access-control semantics, while `rebuild_rights` still behaves like an adapter-owned lifecycle extension.
