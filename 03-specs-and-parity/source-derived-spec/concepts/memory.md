# Memory

## Purpose

Captures persistent knowledge records and memory directory artifacts used to orient future sessions and agents.

## Core responsibilities

- Store durable knowledge outside a single turn or tool call.
- Organize retention and ownership rules.
- Let sessions and agents retrieve stable context quickly.

## Required fields

- `id`
- `scope`
- `owner`
- `source`
- `content_ref`
- `last_updated_at`
- `retention_policy`

## Lifecycle or execution semantics

- Memory is distinct from transcript history even when both reference the same facts.
- Scopes typically range from session-local to user- or project-level.
- Background consolidation or pruning can change memory state independently of foreground work.

## Relationships to other objects

- Referenced by Session and Agent.
- Governed by Policy retention rules.
- May be produced or updated by Task execution and skill pipelines.

## Evidence from tracked repositories

- `claude-code-source`: `src/memdir/`, `src/commands/memory/`, `src/query.ts`
- `claude-code-Kuberwastaken`: `src-rust/crates/core/src/memdir.rs`, `src-rust/crates/query/src/auto_dream.rs`
- `claude-code-instructkr`: `src/memdir/`, `src/session_store.py`, `PARITY.md`
- Research layer: `04-diffs-and-indexes/manifests/instructkr.manifest.md`

## Open parity notes

- Kuberwastaken makes memory consolidation especially legible through its `auto_dream` slice.
- instructkr keeps memory surfaces but currently has the lightest durable-memory implementation depth.
