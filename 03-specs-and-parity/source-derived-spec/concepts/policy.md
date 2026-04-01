# Policy

## Purpose

Captures allow, deny, ask, danger-filter, and audit rules that shape what the runtime may do.

## Core responsibilities

- Centralize permission decisions and danger filters.
- Provide explicit audit requirements for risky actions.
- Separate policy expression from tool implementation.

## Required fields

- `id`
- `scope`
- `allow_rules`
- `deny_rules`
- `ask_rules`
- `danger_filters`
- `audit_requirements`

## Lifecycle or execution semantics

- Policy applies at runtime, session, and agent levels.
- Not every denial should be static; some actions route through an ask-policy path.
- Audit requirements should survive even when execution is automated.

## Relationships to other objects

- Consumed by Runtime, Session, Agent, Tool, and Connector flows.
- Interacts with Task scheduling and Memory retention.
- Provides the governance boundary for dangerous operations.

## Evidence from tracked repositories

- `claude-code-source`: `src/utils/permissions/permissionSetup.ts`, `src/services/tools/toolOrchestration.ts`, `src/commands/permissions/`
- `claude-code-Kuberwastaken`: `spec/05_components_agents_permissions_design.md`, `src-rust/crates/core/src/lib.rs`
- `claude-code-instructkr`: `src/permissions.py`, `rust/crates/runtime/src/permissions.rs`, `PARITY.md`
- Research layer: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`

## Open parity notes

- The source baseline shows the widest policy and permission surface.
- Derivative repositories preserve the concept but not the full TS policy ecosystem.
