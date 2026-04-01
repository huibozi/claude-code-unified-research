# Codex Phase 1 Decl-State Mapping Blueprint

Date: 2026-04-01

## Goal

Map the live Codex runtime at `C:\Users\huibozi\.codex` onto the same declaration-state-generated model already proven out in `~/.claude`, without breaking Codex's current runtime behavior.

Phase 1 is intentionally conservative. It does not try to replace Codex's native runtime. It adds a canonical declaration layer, a normalized state view, and disposable generated outputs around the existing runtime surfaces.

## Scope

This blueprint covers:

1. the current structural differences between `~/.claude` and `~/.codex`
2. the locked Phase 1 decisions for config format, SQLite handling, and `superpowers/`
3. the target `decl/`, `state/`, and `generated/` layout for `~/.codex`
4. the first migration slice that can be implemented with low runtime risk

This blueprint does not yet cover:

- full memory modeling for Codex
- deep semantic parsing of all archived session transcripts
- replacing Codex's native SQLite-backed runtime
- `.openclaw` mapping work

## Evidence Summary

Current live `~/.claude` after Phase 3:

- has canonical `decl/`, `state/`, and `generated/`
- keeps top-level compatibility paths alive
- uses JSON declarations plus validation scripts
- emits registries, reports, snapshots, and migration summaries

Current live `~/.codex`:

- has `config.toml`
- has `rules/default.rules`
- has `skills/.system/*/SKILL.md`
- has `sessions/` plus `session_index.jsonl`
- has runtime SQLite files:
  - `state_5.sqlite`
  - `logs_1.sqlite`
- has `memories/`, but it is currently empty
- has a large `superpowers/` tree that is installed as a separate package/workflow payload
- does not have `agents/`
- does not have `decl/`, `state/`, or `generated/`

## Comparison Table

| Dimension | `~/.claude` after Phase 3 | `~/.codex` current state | Phase 1 implication |
|---|---|---|---|
| Canonical declaration root | `decl/` | none | add one |
| Canonical state root | `state/` | none | add one |
| Canonical generated root | `generated/` | none | add one |
| Runtime config | `.claude.json`, `settings.json`, `settings.local.json` | `config.toml` | preserve native Codex config |
| Agents | `decl/agents/*/agent.json` plus legacy mirror | none | seed a canonical default agent |
| Skills | `decl/skills/*/skill.json + skill.md` plus compatibility mirror | `skills/.system/*/SKILL.md` | import a managed subset into canonical JSON+Markdown |
| Rules | `decl/rules/*/policy.json + policy.md` plus compatibility mirror | `rules/default.rules` | wrap current rule surface into canonical policy objects |
| Commands | `decl/commands/*/command.json` plus compatibility mirror | no separate command declaration layer | keep command declarations optional or empty in Phase 1 |
| MCP / connectors | `decl/mcp/*/connector.json` | no equivalent declaration surface confirmed | leave empty unless explicit connectors are discovered |
| Memory | not covered in current `.claude` work | `memories/` exists but empty | prepare, do not migrate in Phase 1 |
| Session archive | normalized `state/sessions` plus legacy runtime copies | `sessions/` JSONL rollouts plus `session_index.jsonl` | derive a normalized state view without replacing runtime files |
| Runtime DB | none | `state_5.sqlite`, `logs_1.sqlite` | treat as native runtime state, do not mutate |
| Generated indices | `generated/registries`, `reports`, `snapshots` | none | add them |
| Validation flow | `validate_decl.py`, `validate_state.py`, `validate_full.py` | none | add a Codex-specific validator set |
| Vendor/tool tree | no direct equivalent | `superpowers/` package/workflow tree | keep separate from decl-state |

## Locked Decisions

### 1. Config format

Decision: keep Codex runtime config in TOML, but make the new declaration layer JSON.

Locked choice:

- `config.toml` stays the native Codex runtime config
- new `decl/` units use JSON, just like the proven `~/.claude` design

Reasoning:

- this keeps cross-runtime declaration schemas aligned
- it avoids forcing TOML into every downstream runtime
- it lets Codex keep its native runtime shape while still joining the unified spec

Interpretation:

- `config.toml` in Codex plays the same role as `settings.json` or `.claude.json` in Claude Code
- it is a runtime adapter/config surface, not the new canonical declaration layer

### 2. SQLite state files

Decision: do not touch Codex's SQLite runtime state in Phase 1.

Locked choice:

- `state_5.sqlite` remains untouched
- `logs_1.sqlite` remains untouched
- any normalized `state/` outputs are additive filesystem views only

Reasoning:

- the SQLite files clearly back live runtime behavior
- they already contain internal tables for threads, jobs, logs, stage outputs, and spawn edges
- mutating them in the first migration slice adds high risk with little architectural upside

### 3. `superpowers/`

Decision: keep `superpowers/` separate from decl-state.

Locked choice:

- do not move `superpowers/` under `state/`
- do not treat `superpowers/` itself as canonical `decl/`
- selectively import chosen skills from it into canonical declarations when needed

Reasoning:

- it is an installed package/workflow tree, not a runtime state bucket
- it has its own `README.md`, `package.json`, marketplace/plugin assets, and `.git`
- it behaves like a vendor/tool payload, not like user-authored declaration or session state

## Design Principles

- preserve Codex runtime behavior first
- add canonical structure around the runtime, not through it
- normalize only the surfaces that are stable enough to model cleanly
- keep JSON declaration objects cross-runtime consistent with `~/.claude`
- treat SQLite, logs, and installed tool trees as native runtime assets unless there is a strong reason to migrate them

## Target Layout For `~/.codex`

Phase 1 adds three new roots:

```text
.codex/
  decl/
    agents/
    skills/
    rules/
    commands/
    mcp/
  state/
    sessions/
    indexes/
      sqlite/
  generated/
    registries/
    reports/
    snapshots/
```

Semantics:

- `decl/` is the new canonical human-edited layer
- `state/` is a normalized view over native Codex runtime state
- `generated/` contains disposable outputs
- `state/indexes/sqlite/` stores metadata views only; it does not store the live `.sqlite` files themselves

Existing Codex runtime surfaces remain in place:

- `config.toml`
- `rules/default.rules`
- `skills/`
- `sessions/`
- `session_index.jsonl`
- `state_5.sqlite`
- `logs_1.sqlite`
- `superpowers/`

## Phase 1 Object Mapping

### Agent mapping

Codex has no native `agents/` declaration tree today, but it does have enough runtime config to seed a canonical default agent.

Proposed seed:

- `decl/agents/codex-default/agent.json`

Seed sources:

- `config.toml:model`
- `config.toml:model_reasoning_effort`
- `config.toml:features.multi_agent`
- `config.toml:windows.sandbox`

Adapter rules:

- map `model_reasoning_effort` into core `compute_profile`
- keep Codex-specific fields in an adapter note or renderer, not in the core schema
- do not map `windows.sandbox = elevated` directly into core `isolation`; that belongs in adapter/runtime policy handling
- keep core `isolation` as `none` for cross-runtime neutrality, but record the runtime difference in `_adapter_notes`

Suggested first canonical payload:

```json
{
  "id": "codex-default",
  "description": "Default Codex runtime agent derived from config.toml.",
  "model": "gpt-5.4",
  "compute_profile": "high",
  "tools": [],
  "skills": [],
  "permission_mode": "inherit",
  "memory_scope": "session",
  "isolation": "none",
  "max_turns": 0,
  "required_mcp_servers": [],
  "_adapter_notes": {
    "runtime_sandbox": "elevated",
    "note": "Codex runtime currently uses elevated Windows sandboxing. Core isolation remains none in the shared schema."
  }
}
```

This is not claiming Codex literally has that internal object today. It is a canonical cross-runtime projection of current Codex runtime settings.

### Skill mapping

Current Codex skills are Markdown packages rooted under:

- `skills/.system/*/SKILL.md`

Phase 1 should not try to canonicalize everything. It should import a managed subset into:

- `decl/skills/<id>/skill.json`
- `decl/skills/<id>/skill.md`

Recommended first cohort:

- `openai-docs`
- `skill-creator`
- any additional local managed skills already known to be important in this workspace

Rules:

- `skill.json` stores structured metadata
- `skill.md` stores the human-facing body
- existing `skills/` remains the runtime compatibility corpus
- no attempt is made in Phase 1 to rewrite Codex's native skill loader
- import only skills with a clear `when_to_use` style purpose or equivalent behavioral description
- do not import skills that are only installation or setup instructions
- do not import skills that depend on undeclared external services until those dependencies are modeled in canonical declarations

### Rule mapping

Current Codex rule surface is thin:

- `rules/default.rules`

Phase 1 should wrap this into a canonical policy declaration:

- `decl/rules/default/policy.json`
- `decl/rules/default/policy.md`

Interpretation:

- `default.rules` remains the runtime-facing rules corpus
- `decl/rules` becomes the structured mirror/canonical source for future policy work

### Command mapping

Codex does not currently expose a clear command-declaration tree equivalent to Claude Code's `commands/`.

Phase 1 stance:

- create `decl/commands/` as an empty but ready canonical root
- do not invent command declarations from session history
- only populate it once command semantics are discovered from stable runtime sources

### Connector mapping

No explicit connector declaration layer has been confirmed in `~/.codex`.

Phase 1 stance:

- create `decl/mcp/` as an empty canonical root
- populate only when Codex exposes a stable connector or MCP configuration surface worth modeling

### Memory mapping

`memories/` exists but is empty. That is useful, but not enough to justify a migration in Phase 1.

Phase 1 stance:

- leave `memories/` untouched
- note it as a future integration point for the unified `Memory` object
- do not force a memory schema before Codex actually uses the directory

## State Strategy

### Sessions

Current Codex session state already has two useful surfaces:

- `sessions/YYYY/MM/DD/*.jsonl`
- `session_index.jsonl`

Phase 1 should not duplicate every rollout transcript into a second archive tree.

Instead, it should derive a normalized session view:

- `state/sessions/index.json`

Derived fields can include:

- `session_id`
- `thread_name`
- `updated_at`
- `source_path`
- `cwd` when recoverable from session meta
- `originator`
- `cli_version`
- `model_provider`
- `model`

This is closer to an index and metadata view than to a raw archive copy.

### SQLite

Phase 1 should add lightweight metadata views only, for example:

- `state/indexes/sqlite/index.json`

Possible fields:

- database filename
- file size
- modified time
- discovered table names
- selected table schemas

This gives the unified runtime a filesystem-readable state inventory without altering native SQLite storage.

### Logs and reports

`generated/reports/` should capture migration and health output, not replace runtime logs.

Phase 1 reports should include at minimum:

- `codex-bootstrap-inventory.json`
- `codex-decl-health.json`
- `codex-state-health.json`
- `codex-session-inventory.json`

## Generated Layer

Phase 1 should reproduce the same disposable generated layer shape already working in `~/.claude`:

- `generated/registries/`
- `generated/reports/`
- `generated/snapshots/`

Registry groups:

- `agents.registry.json`
- `skills.registry.json`
- `rules.registry.json`
- `commands.registry.json`
- `mcp.registry.json`

Snapshot rules:

- declaration snapshots only
- keep the newest `5`
- generated outputs remain outside version control where appropriate

## Validation Model

Phase 1 should add a Codex-specific validation flow that mirrors the Claude pattern, but is narrower.

Recommended commands:

- `validate_decl_codex.py`
- `validate_state_codex.py`
- `validate_full_codex.py`

### `validate_decl_codex.py`

Checks:

- canonical JSON declarations parse
- ids are unique
- required fields are present
- managed skill imports are structurally sound
- seeded default agent is valid

### `validate_state_codex.py`

Checks:

- session index parses
- SQLite metadata index parses
- state references to declaration ids are valid where present
- warnings are allowed for incomplete historical traceability

Phase 1 intentionally does not deep-parse every session transcript and every archived artifact.

### `validate_full_codex.py`

Checks:

1. validate declarations
2. rebuild registries
3. rebuild state indexes from native Codex surfaces
4. validate normalized state
5. build declaration snapshot
6. backfill registry `decl_generation`
7. summarize result with exit codes:
   - `0 = pass`
   - `1 = error`
   - `2 = warn`

## Compatibility Rules

Phase 1 should preserve the following invariants:

- Codex continues to read `config.toml`
- Codex continues to use `sessions/` and its SQLite databases unchanged
- Codex continues to use native `skills/`
- `superpowers/` remains where it is
- all new declaration/state/generated outputs are additive

That means Phase 1 is a mapping layer, not a runtime replacement.

## Recommended Phase 1 Work Order

1. bootstrap `decl/`, `state/`, and `generated/` under `~/.codex`
2. write Codex-specific shared helpers and validation entrypoints
3. import a seeded default agent from `config.toml`
4. import the first managed skill cohort from `skills/.system`
5. import `rules/default.rules` into canonical rule declarations
6. build registries
7. derive `state/sessions/index.json` from `session_index.jsonl` and session JSONL metadata
8. derive `state/indexes/sqlite/index.json` from the native SQLite files
9. build declaration snapshots and emit reports and validation summaries

## Success Criteria

Codex Phase 1 is successful when:

1. `~/.codex` has canonical `decl/`, `state/`, and `generated/` roots
2. Codex runtime behavior is unchanged
3. a canonical default agent exists
4. a managed subset of skills exists in structured JSON+Markdown form
5. the thin native rule surface is wrapped into canonical policy objects
6. registries and declaration snapshots can be generated repeatably
7. normalized session and SQLite indexes exist without mutating native storage
8. validation emits `pass / warn / error` with stable exit codes

## Recommendation

Proceed with Codex Phase 1 as:

- JSON canonical declaration layer
- TOML runtime config preserved
- SQLite untouched
- `superpowers/` treated as a separate installed workflow tree
- state normalization limited to additive indexes and inventories

This gives the unified runtime effort a clean foothold in Codex without overreaching into unstable or high-risk runtime surfaces.
