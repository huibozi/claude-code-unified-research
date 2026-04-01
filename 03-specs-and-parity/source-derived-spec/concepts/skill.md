# Skill

## Purpose

Defines a reusable high-level behavior package with its own prompts, tool allowances, routing hints, and path conditions.

## Core responsibilities

- Package higher-level behavior beyond a single tool.
- Describe when the skill should be selected and what tools it may call.
- Allow model overrides, execution context changes, and path-based activation.

## Required fields

- `name`
- `source`
- `description`
- `when_to_use`
- `allowed_tools`
- `argument_hint`
- `model_override`
- `execution_context`
- `path_conditions`
- `hooks`

## Lifecycle or execution semantics

- Skills sit between commands and tools: they shape strategy rather than just exposing primitive actions.
- A runtime can ship bundled skills and also load local or connector-provided skills.
- Path conditions allow skills to become context-aware without becoming hard-coded into the runtime.

## Relationships to other objects

- Consumed by Agent definitions and suggested within Session execution.
- Restricted by Tool and Policy constraints.
- May be discovered from local directories or external connectors.

## Evidence from tracked repositories

- `claude-code-source`: `src/skills/loadSkillsDir.ts`, `src/skills/bundledSkills.ts`, `src/commands/skills/`
- `claude-code-Kuberwastaken`: `src-rust/crates/tools/src/skill_tool.rs`, `src-rust/crates/tools/src/bundled_skills.rs`
- `claude-code-instructkr`: `src/skills/`, `src/reference_data/tools_snapshot.json`, `PARITY.md`
- Research layer: `04-diffs-and-indexes/manifests/kuberwastaken.manifest.md`

## Open parity notes

- The TS baseline has the most advanced skill loading and path-activation behavior.
- Both rewrites preserve the concept of skills but not the full registry and lifecycle depth.
