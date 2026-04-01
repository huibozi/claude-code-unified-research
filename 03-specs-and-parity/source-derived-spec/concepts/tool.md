# Tool

## Purpose

Represents a model-callable capability with typed I/O, side-effect rules, and concurrency and permission metadata.

## Core responsibilities

- Expose capability metadata to the model and runtime.
- Define input and output contracts.
- Describe permission and side-effect boundaries for orchestration.

## Required fields

- `name`
- `source`
- `description`
- `input_schema`
- `output_schema`
- `permission_requirements`
- `is_concurrency_safe`
- `side_effect_level`

## Lifecycle or execution semantics

- Tools are registered centrally and filtered by runtime context.
- Tool execution must be auditable and permission-aware.
- Concurrency safety matters because tool orchestration can fan out parallel work.

## Relationships to other objects

- Owned by Runtime registries and consumed by Agent and Session.
- Guarded by Policy and often backed by Connector integrations.
- Composed by Skill definitions.

## Evidence from tracked repositories

- `claude-code-source`: `src/Tool.ts`, `src/tools.ts`, `src/services/tools/toolOrchestration.ts`, `src/tools/`
- `claude-code-Kuberwastaken`: `spec/03_tools.md`, `src-rust/crates/tools/src/lib.rs`, `src-rust/crates/tools/src/mcp_resources.rs`
- `claude-code-instructkr`: `src/Tool.py`, `src/tools.py`, `rust/crates/tools/src/lib.rs`, `PARITY.md`
- Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`

## Open parity notes

- The source baseline remains the only place with the full TS tool surface.
- Both derivative repos make tool registries explicit, which helps downstream runtime design.
