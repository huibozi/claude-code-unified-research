# Codex Phase 1 Execution Parity

Date: 2026-04-02

## Purpose

Record how the live `C:\Users\huibozi\.codex` implementation compared to the approved Phase 1 blueprint and implementation plan.

This report does not restate the design. It captures where the executed runtime matched the intended mapping, where runtime evidence forced a clarification, and which surfaces remain intentionally deferred.

## Direct matches to the blueprint

- `decl/`, `state/`, and `generated/` were added as canonical additive roots under `C:\Users\huibozi\.codex`.
- `config.toml` remained the native runtime config surface. The canonical declaration layer stayed JSON-only.
- `state_5.sqlite` and `logs_1.sqlite` were left untouched. Only `state/indexes/sqlite/index.json` metadata views were added.
- `superpowers/` remained outside the decl-state model.
- `decl/agents/codex-default/agent.json` was seeded from `config.toml` with:
  - `model = gpt-5.4`
  - `compute_profile = high`
  - `isolation = none`
  - `_adapter_notes.runtime_sandbox = elevated`
- The first managed skill cohort was imported exactly as planned:
  - `openai-docs`
  - `skill-creator`
  - `skill-installer`
- `rules/default.rules` was wrapped into:
  - `decl/rules/default/policy.json`
  - `decl/rules/default/policy.md`
- `commands/` and `mcp/` canonical roots were created and intentionally left empty.
- `validate_full_codex.py` followed the locked order:
  1. validate declarations
  2. rebuild registries
  3. rebuild state indexes
  4. validate state
  5. build snapshot
  6. backfill `decl_generation`
  7. summarize

## Runtime clarification discovered during implementation

One runtime-facing detail required a real compatibility fix:

- `session_meta.payload.source` is not a single-shape field in live Codex sessions.
- Observed forms:
  - `str`, for example `"vscode"`
  - `dict`, for example a nested `subagent.thread_spawn` payload
- The first implementation of `rebuild_state_indexes_codex.py` assumed `source` was always an object and failed with:
  - `AttributeError: 'str' object has no attribute 'get'`

Resolution:

- treat `payload.source` as a union type
- only inspect `subagent.thread_spawn` when `source` is a `dict`
- preserve the raw `source` value under `_adapter_notes.source`

Parity implication:

- the blueprint remains correct at the architectural level
- the implementation report now adds one concrete adapter note: Codex session metadata requires union-safe parsing for `payload.source`

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\validate_full_codex.py
```

Observed result:

- `codex-decl-health.json`: `pass`
- `codex-state-health.json`: `pass`
- `codex-full-validation.json`: `pass`
- `exit_code`: `0`

Additional observed outputs:

- bootstrap backup: `C:\Users\huibozi\.codex\backups\decl-state\bootstrap-20260401T163358Z`
- normalized session count: `42`
- generated registries: `5`
- generated snapshots retained after first pass: `1`

## Intentionally deferred surfaces

These remain deferred exactly as the blueprint specified:

- no memory migration beyond preserving the empty `memories/` directory
- no command declaration inference from session history
- no connector declaration inference without a stable runtime source
- no deep semantic parsing of all archived rollout content
- no mutation of Codex runtime SQLite storage

## Assessment

Codex Phase 1 achieved blueprint parity.

The executed runtime matched the locked decisions and target architecture. The only implementation-time adjustment was a concrete adapter safeguard for the observed `payload.source` union shape in live session metadata.
