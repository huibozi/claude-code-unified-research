# Session

## Purpose

Represents one active conversation or execution context with its own model, cwd, memory references, and transcript.

## Core responsibilities

- Track per-run state such as current model, mode, cwd, and status.
- Bind an agent identity to a concrete conversation transcript.
- Snapshot permission and memory context for deterministic resumption.

## Required fields

- `id`
- `runtime_id`
- `agent_id`
- `cwd`
- `mode`
- `model`
- `permission_snapshot`
- `memory_refs`
- `transcript_ref`
- `status`

## Lifecycle or execution semantics

- A session is created inside one runtime and normally owned by one active agent.
- Session status changes over time: active, paused, completed, or failed.
- Resuming work means restoring transcript, permissions, and memory references together.

## Relationships to other objects

- Belongs to Runtime.
- References one Agent, zero or more Memory records, and one transcript location.
- Provides context to Task execution and policy checks.

## Evidence from tracked repositories

- `claude-code-source`: `src/query.ts`, `src/QueryEngine.ts`, `src/assistant/sessionHistory.ts`
- `claude-code-Kuberwastaken`: `spec/01_core_entry_query.md`, `src-rust/crates/query/src/lib.rs`, `src-rust/crates/cli/src/main.rs`
- `claude-code-instructkr`: `src/query.py`, `src/query_engine.py`, `rust/crates/runtime/src/session.rs`
- Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`

## Open parity notes

- instructkr and Kuberwastaken both model conversation state, but they do not expose every TS transport and resume behavior.
- The TypeScript baseline remains the clearest reference for session lifecycle breadth.
