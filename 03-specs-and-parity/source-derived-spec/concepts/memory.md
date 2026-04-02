# Memory

## Purpose

Captures persistent knowledge records, memory surfaces, and durable memory artifacts used to orient future sessions and agents.

## Core responsibilities

- Store durable knowledge outside a single turn or tool call.
- Organize retention and ownership rules.
- Let sessions and agents retrieve stable context quickly.
- Model memory as an addressable surface when a runtime exposes multiple durable stores instead of one implicit memory bucket.

## Required fields

- `id`
- `scope`
- `owner`
- `source`
- `content_ref`
- `last_updated_at`
- `retention_policy`

## Promoted surface fields

When a runtime exposes explicit memory surfaces, the shared spec promotes these additional fields as stable cross-runtime semantics:

- `kind`
- `store_kind`
- `indexing_mode`
- `reader_refs`
- `writer_refs`
- `policy_refs`

These fields describe what sort of memory surface exists and who can interact with it, without requiring every runtime to use the same storage backend.

## Locator or adapter fields

Some runtimes also need storage locators so the canonical declaration can point at live runtime memory roots.

The shared model allows these as locator or adapter-aware fields:

- `source_roots`
- `sqlite_path`

These fields are useful for runtime-specific pathing and indexing, but they are not the semantic center of `Memory`. The semantic center remains the ownership, access, and retention model.

## Lifecycle or execution semantics

- Memory is distinct from transcript history even when both reference the same facts.
- Scopes typically range from session-local to user- or project-level.
- Background consolidation or pruning can change memory state independently of foreground work.
- Retention belongs to `Memory` itself, because expiration, compaction, or preservation are properties of the memory surface or record being governed.
- Policy may constrain who can read or write memory, but retention rules should not be modeled as if they originate from policy first.

## Relationships to other objects

- Referenced by Session and Agent.
- Governed by Policy retention rules.
- May be produced or updated by Task execution and skill pipelines.
- Agent may mount explicit memory surfaces through `memory_refs[]` when the runtime makes durable memory surfaces first-class.

## Evidence from tracked repositories

- `claude-code-source`: `src/memdir/`, `src/commands/memory/`, `src/query.ts`
- `claude-code-Kuberwastaken`: `src-rust/crates/core/src/memdir.rs`, `src-rust/crates/query/src/auto_dream.rs`
- `claude-code-instructkr`: `src/memdir/`, `src/session_store.py`, `PARITY.md`
- Research layer: `04-diffs-and-indexes/manifests/instructkr.manifest.md`
- Live downstream OpenClaw: `decl/memory/`, `state/indexes/memory/index.json`, `memory/*.sqlite`

## Open parity notes

- Kuberwastaken makes memory consolidation especially legible through its `auto_dream` slice.
- instructkr keeps memory surfaces but currently has the lightest durable-memory implementation depth.
- Live downstream OpenClaw work confirms that durable memory often needs both:
  - promoted surface semantics such as `kind`, `store_kind`, `indexing_mode`, `reader_refs`, `writer_refs`, and `policy_refs`
  - runtime locator fields such as `source_roots` and `sqlite_path`
