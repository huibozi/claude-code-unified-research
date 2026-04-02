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
- `memory_refs`
- `accepts_handoff_from`
- `adapter_notes`

These optional fields capture runtime-specific facts that should not be flattened into the core identity:

- logical id versus physical runtime directory
- discovery provenance such as declared versus directory-discovered
- runtime-specific storage or workspace locators
- explicit mounted memory surfaces when a runtime exposes memory as addressable declarations
- explicit initiator allowlists when a runtime exposes first-class handoff or delegation declarations

## Lifecycle or execution semantics

- Agents may be user-facing, background, remote, or child-worker identities.
- An agent definition should be declarative enough to recreate a session elsewhere.
- Permission and isolation rules are part of the agent contract, not an afterthought.
- The canonical `id` is a logical execution identity. It may differ from the physical directory or runtime-owned storage path used by one downstream implementation.
- Downstream importers may need hybrid discovery, combining explicit agent lists with directory-backed runtime surfaces.
- When a runtime exposes first-class memory surfaces, `memory_refs[]` is the preferred fact source for agent memory attachment.
- In that shape, `memory_scope` should be treated as a summary field rather than the only truth source.
- `memory_scope = shared` is now part of the stable cross-runtime vocabulary for agents that mount shared durable memory without owning a private project-local store.
- When a runtime exposes handoff or delegation declarations, `accepts_handoff_from[]` is the preferred fact source for which initiators a target agent may accept work from.

## Relationships to other objects

- Used by Session and Task.
- Consumes Tool, Skill, Connector, Memory, and Policy objects.
- Spawns or coordinates other agents through AgentTool-style facilities.
- Session should reference the logical agent id, not a physical runtime directory.
- Agent may reference shared `Memory` objects through `memory_refs[]` instead of relying only on one coarse `memory_scope` label.
- Agent may also reference allowed handoff initiators through `accepts_handoff_from[]` when a runtime exposes a first-class coordination family.

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
- Live downstream OpenClaw Phase 3 work further confirms that `memory_refs[]` should be modeled explicitly and that `memory_scope` needs a stable `shared` variant.
- Live downstream OpenClaw Phase 4 work further confirms that `accepts_handoff_from[]` is a stable agent-level reference pattern when runtimes expose explicit handoff declarations.
