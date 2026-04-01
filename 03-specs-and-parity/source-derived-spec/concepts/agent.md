# Agent

## Purpose

Describes an execution identity with model choice, tool scope, skill scope, permissions, and isolation settings.

## Core responsibilities

- Define what model and reasoning effort to use.
- Constrain allowed tools, skills, and required connectors.
- Control permission mode, memory scope, isolation, and turn limits.

## Required fields

- `id`
- `agent_type`
- `source`
- `model`
- `effort`
- `tools`
- `skills`
- `permission_mode`
- `memory_scope`
- `isolation`
- `max_turns`
- `hooks`
- `required_connectors`

## Lifecycle or execution semantics

- Agents may be user-facing, background, remote, or child-worker identities.
- An agent definition should be declarative enough to recreate a session elsewhere.
- Permission and isolation rules are part of the agent contract, not an afterthought.

## Relationships to other objects

- Used by Session and Task.
- Consumes Tool, Skill, Connector, Memory, and Policy objects.
- Spawns or coordinates other agents through AgentTool-style facilities.

## Evidence from tracked repositories

- `claude-code-source`: `src/tools/AgentTool/loadAgentsDir.ts`, `src/query.ts`, `src/tasks/LocalAgentTask/LocalAgentTask.tsx`
- `claude-code-Kuberwastaken`: `spec/05_components_agents_permissions_design.md`, `src-rust/crates/query/src/agent_tool.rs`
- `claude-code-instructkr`: `src/tasks.py`, `src/coordinator/__init__.py`, `rust/crates/runtime/src/conversation.rs`
- Research layer: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`

## Open parity notes

- Kuberwastaken retains stronger agent semantics than instructkr.
- instructkr exposes coordinator and task surfaces, but not full parity with the TS agent configuration pipeline.
