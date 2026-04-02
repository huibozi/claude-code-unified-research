# OpenClaw Phase 1 Execution Parity

Date: 2026-04-02

## Purpose

Record how the live `C:\Users\huibozi\.openclaw` implementation compared to the approved Phase 1 blueprint decisions and the written implementation plan.

This report does not restate the design. It captures where the executed runtime matched the intended mapping, where runtime evidence forced a clarification, and which surfaces remain intentionally deferred.

## Direct matches to the blueprint

- `decl/`, `state/`, and `generated/` were added as canonical additive roots under `C:\Users\huibozi\.openclaw`.
- `openclaw.json` remained the native runtime config surface and compatibility input. It was not replaced by canonical declarations.
- Canonical declaration roots were created for:
  - `agents`
  - `skills`
  - `commands`
  - `bindings`
  - `channels`
  - `gateway`
  - `plugins`
  - `cron`
  - `rules`
  - `mcp`
- `rules/` and `mcp/` were created as canonical empty roots and still participate in registry generation.
- `state/` was limited to normalized views and metadata-only outputs:
  - `state/sessions/index.json`
  - `state/cron-runs/index.json`
  - `state/indexes/credentials/index.json`
  - `state/indexes/devices/index.json`
  - `state/indexes/memory/index.json`
- `credentials/`, `devices/`, and `memory/*.sqlite` remained in place and were indexed only as metadata.
- `skills/opennews` and `skills/opentwitter` were imported into canonical `decl/skills/*` while the original package-style skill directories remained untouched.
- `validate_full_openclaw.py` followed the locked order:
  1. validate declarations
  2. rebuild registries
  3. rebuild state indexes
  4. validate state
  5. build snapshot
  6. backfill `decl_generation`

## Runtime clarifications discovered during implementation

Three live-runtime details required concrete clarification:

### 1. `openclaw.json` is JSONC-like, not strict JSON

- The live file contains at least one trailing comma in the `bindings` array block.
- A strict `json.loads()` or `JSON.parse()` assumption fails against the runtime file.

Resolution:

- add one shared `read_jsonc()` helper
- strip trailing commas before JSON parsing
- route all runtime config reads through that helper

Parity implication:

- the architectural decision stayed correct
- the implementation had to lock in tolerant parsing as a real adapter requirement, not a hypothetical convenience

### 2. `agents.list[]` is incomplete relative to the live agent directories

Observed runtime evidence:

- `openclaw.json:agents.list[]` exposes only four logical ids:
  - `research`
  - `daily`
  - `freya`
  - `profit`
- the live runtime directory contains six agent roots:
  - `daily`
  - `freya`
  - `main`
  - `personal`
  - `profit`
  - `research`

Resolution:

- make the agent importer hybrid
- import listed agents from `agents.list[]`
- then scan `agents/*/agent/models.json` and add missing directory-backed agents as `directory-discovered`

Parity implication:

- the blueprint target of six canonical agents remained correct
- the importer could not rely on `agents.list[]` as the sole source of truth

### 3. Logical agent ids do not always match physical agent directories

Observed runtime evidence:

- logical agent `freya` is configured with `agentDir = C:\Users\huibozi\.openclaw\agents\personal\agent`
- the live runtime also still has a physical `agents\freya\` session root

Resolution:

- preserve `physical_agent_dir` in `_adapter_notes`
- avoid assuming canonical `id == on-disk directory name`

Parity implication:

- OpenClaw requires a stronger adapter layer than `.codex` for agent identity and storage layout

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Observed result:

- `openclaw-decl-health.json`: `pass`
- `openclaw-state-health.json`: `pass`
- `openclaw-full-validation.json`: `pass`
- `exit_code`: `0`

Additional observed outputs:

- bootstrap backup: `C:\Users\huibozi\.openclaw\backups\decl-state\bootstrap-20260402T011948Z`
- generated snapshot: `C:\Users\huibozi\.openclaw\generated\snapshots\decl-20260401T172545Z.json`
- generated registries: `10`
- normalized session count: `17`
- normalized cron run count: `7`
- indexed credentials files: `3`
- indexed devices files: `3`
- indexed memory databases: `2`

## Intentionally deferred surfaces

These remain deferred exactly as the blueprint specified:

- no canonical rewrite-back into `openclaw.json`
- no workspace migration for `workspace*`
- no deep transcript parsing of agent session JSONL bodies
- no secret extraction or semantic parsing from `credentials/` or `devices/`
- no mutation of `memory/*.sqlite`
- no restructuring of the global npm-installed OpenClaw package

## Assessment

OpenClaw Phase 1 achieved implementation parity with the locked design decisions.

The executed runtime matched the intended additive architecture. The main implementation-time adjustments were not architectural reversals; they were adapter clarifications driven by live runtime evidence:

- tolerant parsing for `openclaw.json`
- hybrid agent discovery
- explicit separation between logical agent ids and physical agent directories
