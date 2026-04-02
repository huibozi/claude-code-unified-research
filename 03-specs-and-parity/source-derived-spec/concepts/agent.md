# Agent

## Purpose

Describes an execution identity with model choice, normalized compute profile, tool scope, skill scope, permissions, and isolation settings.

## Core responsibilities

- Define what model and normalized compute profile to use.
- Constrain allowed tools, skills, and required connectors.
- Control permission mode, memory scope, isolation, and turn limits.
- Preserve adapter notes when the logical agent identity does not line up one-to-one with runtime storage layout.

## Required fields

- `id`
- `agent_type`
- `source`
- `model`
- `compute_profile`
- `tools`
- `skills`
- `permission_mode`
- `memory_scope`
- `isolation`
- `max_turns`
- `hooks`
- `required_connectors`

## Optional adapter or compatibility fields

- `name`
- `disallowed_tools`
- `adapter_notes`

These optional fields capture runtime-specific facts that should not be flattened into the core identity:

- logical id versus physical runtime directory
- discovery provenance such as declared versus directory-discovered
- runtime-specific storage or workspace locators

## Lifecycle or execution semantics

- Agents may be user-facing, background, remote, or child-worker identities.
- An agent definition should be declarative enough to recreate a session elsewhere.
- Permission and isolation rules are part of the agent contract, not an afterthought.
- The canonical `id` is a logical execution identity. It may differ from the physical directory or runtime-owned storage path used by one downstream implementation.
- Downstream importers may need hybrid discovery, combining explicit agent lists with directory-backed runtime surfaces.

## Relationships to other objects

- Used by Session and Task.
- Consumes Tool, Skill, Connector, Memory, and Policy objects.
- Spawns or coordinates other agents through AgentTool-style facilities.
- Session should reference the logical agent id, not a physical runtime directory.

## Evidence from tracked repositories

- `claude-code-source`: `src/tools/AgentTool/loadAgentsDir.ts`, `src/query.ts`, `src/tasks/LocalAgentTask/LocalAgentTask.tsx`
- `claude-code-Kuberwastaken`: `spec/05_components_agents_permissions_design.md`, `src-rust/crates/query/src/agent_tool.rs`
- `claude-code-instructkr`: `src/tasks.py`, `src/coordinator/__init__.py`, `rust/crates/runtime/src/conversation.rs`
- Research layer: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`

## Open parity notes

- Kuberwastaken retains stronger agent semantics than instructkr.
- instructkr exposes coordinator and task surfaces, but not full parity with the TS agent configuration pipeline.
- Live downstream `.codex` and `.openclaw` work confirms that `compute_profile` is a better cross-runtime field than runtime-specific effort labels.
- Live downstream OpenClaw work also confirms that agent definitions need adapter notes for physical locators and discovery provenance.
