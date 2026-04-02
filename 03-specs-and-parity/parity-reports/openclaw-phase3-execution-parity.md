# OpenClaw Phase 3 Execution Parity

Date: 2026-04-02

## Purpose

Record how the live `C:\Users\huibozi\.openclaw` implementation compared to the approved Phase 3 memory-catalog design and written implementation plan.

This report captures execution parity, runtime-driven clarifications, and the concrete adapter choices needed to turn OpenClaw memory into one validated declaration graph spanning memory surfaces, agent mounts, memory access policy, state indexes, and generated registries.

## Direct matches to the blueprint

- `decl/memory/` is now a first-class canonical declaration root for OpenClaw memory surfaces.
- The first live catalog contains exactly nine locked surfaces:
  - `main-store`
  - `research-store`
  - `workspace-main-files`
  - `workspace-research-files`
  - `workspace-daily-files`
  - `research-learnings`
  - `daily-learnings`
  - `personal-learnings`
  - `shared-learnings`
- Every live canonical agent now declares `memory_refs[]`, and `memory_scope` is now a bounded summary field instead of a vague passthrough.
- `memory_scope` was expanded to support the locked Phase 3 shape:
  - `mixed`
  - `shared`
- `decl/rules/` now contains five explicit memory-access policies in addition to the existing routing policies:
  - `research-domain-access`
  - `main-domain-access`
  - `daily-domain-access`
  - `personal-domain-access`
  - `shared-learnings-access`
- `state/indexes/memory/index.json` now reports both:
  - `sqlite_entries`
  - `file_roots`
- Generated registries increased from `10` to `11` with the addition of `memory.registry.json`.
- Declaration validation was extended to enforce the Phase 3 cross-reference graph:
  - `agent.memory_refs[] -> memory`
  - `memory.policy_refs[] -> rules`
  - `memory.reader_refs[] -> agents`
  - `memory.writer_refs[] -> agents`
  - `memory.shared_with[] -> agents`
  - `policy.readers[] / writers[] / shared_with[] / rebuild_rights[] -> agents`

## Runtime clarifications discovered during implementation

Three live-runtime details forced concrete Phase 3 clarifications.

### 1. OpenClaw memory is file-first and sqlite-second

Observed runtime evidence:

- live file-based memory roots exist under:
  - `workspace/memory`
  - `workspace-research/memory`
  - `workspace-daily/memory`
  - `workspace-research/.learnings`
  - `workspace-daily/.learnings`
  - `workspace-personal/.learnings`
  - `shared-learnings`
- both sqlite files exist and expose a retrieval-oriented schema with tables such as:
  - `chunks`
  - `chunks_fts*`
  - `embedding_cache`
  - `files`
  - `meta`
- both sqlite stores were still empty at execution time:
  - `main.sqlite`: `files = 0`, `chunks = 0`, `embedding_cache = 0`, `meta = 0`
  - `research.sqlite`: `files = 0`, `chunks = 0`, `embedding_cache = 0`, `meta = 0`

Resolution:

- catalog file-store and sqlite-index surfaces side-by-side
- treat sqlite as the retrieval/index layer rather than the only truth source
- keep `state/indexes/memory/index.json` metadata-only and avoid reading file content bodies into canonical state

Parity implication:

- the blueprint decision to model `file-store | sqlite-index | hybrid` was necessary, not optional
- OpenClaw memory could not be truthfully represented as "sqlite only"

### 2. Memory domains do not align one-to-one with agent ids

Observed runtime evidence:

- `research` and `profit` share the research-domain learnings surface
- `personal` and `freya` share the personal learnings surface
- `shared-learnings` is a real root-level cross-agent surface
- live workspace docs describe a `UNIFIED-MEMORY-HUB` and shared learning entrypoints rather than a single memory root per agent

Resolution:

- make `memory_refs[]` the fact source on agents
- keep `memory_scope` only as a summary field
- introduce `mixed` for agents that mount both workspace-local and shared memory surfaces

Parity implication:

- the locked Phase 3 choice to prefer `memory_refs[]` over `memory_scope` was validated by the live runtime
- any attempt to model OpenClaw memory as one-surface-per-agent would have hidden real sharing boundaries

### 3. Memory policy needed a new policy family instead of reusing routing policy

Observed runtime evidence:

- existing canonical policies were routing-only:
  - `dm-open`
  - `group-restricted`
  - `gateway-auth`
- none of them expressed:
  - who can read a memory surface
  - who can write a memory surface
  - who can trigger index rebuilds
  - which surfaces are explicitly shared

Resolution:

- add five dedicated memory-access policies
- attach them explicitly through `memory.policy_refs[]`
- keep routing policy and memory policy as parallel families under the same canonical `rules/` root

Parity implication:

- Phase 3 was a real semantic extension, not a restatement of Phase 2 rules
- `rules/` now carries two policy families:
  - routing policy
  - memory access policy

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase3_memory.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Observed result:

- `5` Phase 3 memory tests: `PASS`
- `openclaw-decl-health.json`: `pass`
- `openclaw-state-health.json`: `pass`
- `openclaw-full-validation.json`: `pass`
- `exit_code`: `0`

Additional observed outputs:

- generated snapshot: `C:\Users\huibozi\.openclaw\generated\snapshots\decl-20260402T060939Z.json`
- generated registries: `11`
- registry summary:
  - `agents = 6`
  - `skills = 2`
  - `commands = 1`
  - `bindings = 3`
  - `channels = 3`
  - `gateway = 1`
  - `plugins = 3`
  - `cron = 1`
  - `rules = 8`
  - `mcp = 3`
  - `memory = 9`
- normalized state observations remained stable:
  - `sessions = 17`
  - `cron_runs = 7`
  - `credentials_files = 3`
  - `devices_files = 3`
  - `memory_databases = 2`
  - `memory_file_roots = 7`

## Intentionally deferred surfaces

These remained deferred by design during Phase 3:

- no rewrite-back into `openclaw.json`
- no mutation of `memory/*.sqlite`
- no file-content ingestion out of `workspace*/memory/*` or `workspace*/.learnings/*`
- no cron-driven indexing or retention automation yet
- no semantic parsing of the file-memory documents themselves
- no attempt to collapse OpenClaw memory sharing into a cross-runtime-generic sub-surface model

## Assessment

OpenClaw Phase 3 achieved implementation parity with the locked memory-catalog design.

The main execution-time adjustments were runtime clarifications, not architectural reversals:

- file memory and sqlite index memory must coexist in the canonical model
- memory attachment truth lives on `agent.memory_refs[]`, not on a single scope field
- memory access required a new explicit policy family

The result is a validated memory surface where `decl/memory`, `agent.memory_refs[]`, memory-access policy, state memory indexes, and `memory.registry.json` now operate as one referential declaration graph.
