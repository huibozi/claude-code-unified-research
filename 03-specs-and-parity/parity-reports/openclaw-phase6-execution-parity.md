# OpenClaw Phase 6 Execution Parity

Date: 2026-04-03

## Purpose

Record how the live `C:\Users\huibozi\.openclaw` implementation compared to the approved Phase 6 shared-context / joint-session-lite design and written implementation plan.

This report captures execution parity, runtime-driven clarifications, and the concrete adapter decisions required to turn template-only handoff context declarations into real, auditable shared-context handoff runs.

## Direct matches to the blueprint

- `decl/handoffs/*/handoff.json` remained template-only and did not become a runtime fact store.
- `context_transfer` remained declaration-only in canonical handoff policy files:
  - `memory_refs[]`
  - `include_session_ref`
  - `include_snapshot_ref`
  - `prompt_prefix`
  - `include_source_session_summary`
  - `tool_state_ref`
- realized runtime context now lives in handoff events instead of declarations:
  - `context_refs.session_ref`
  - `context_refs.snapshot_ref`
  - `context_refs.source_session_summary_ref`
  - `context_hash`
- `extensions/handoff-bridge/lib/summarizer.js` now creates deterministic source-session summaries under:
  - `C:\Users\huibozi\.openclaw\state\sessions\summaries\`
- `context_hash` is now computed from the realized runtime context payload and persisted in accepted handoff events.
- `memory` declarations now expose `shared_write_policy` while keeping `writer_refs[]` as the outer write boundary.
- the target handoff session transcript now proves `prompt_prefix` is actually carried into the first user prompt.

## Runtime clarifications discovered during implementation

Phase 6 surfaced four live-runtime clarifications that materially shaped the implementation.

### 1. Declaration-layer `context_transfer` and runtime context payload must stay split

Observed runtime evidence:

- Phase 5 already proved that values such as:
  - `session_ref`
  - `snapshot_ref`
  - `source_session_summary_ref`
  - `context_hash`
  only exist once a specific handoff run is being executed
- writing these values back into:
  - `decl/handoffs/*/handoff.json`
  would have mixed runtime evidence into canonical declarations

Resolution:

- `handoff.json` stays template-only and declares what context categories may be carried
- runtime events under:
  - `state/handoff-events/events.jsonl`
  record what was actually carried

Parity implication:

- the Phase 6 design intent was preserved
- the declaration/runtime split is now an explicit adapter rule, not just a stylistic preference

### 2. `source_session_summary_ref` must come from an explicit source session, never a guessed recent session

Observed runtime evidence:

- some indexed sessions in:
  - `state/sessions/index.json`
  point at deleted or stale runtime files
- manual handoff triggers do not always provide a safe current-session source automatically

Resolution:

- Phase 6 summary generation now uses a strict source priority:
  1. explicit `source_session_ref`
  2. current hook context session when clearly present
  3. otherwise no summary
- the bridge does not guess "latest session for this agent"

Parity implication:

- the Phase 6 summary model remained deterministic
- avoiding implicit session guessing prevented silent context drift

### 3. `state/sessions/index.json` still does not index `agent/sessions/handoff-*.jsonl`

Observed runtime evidence:

- accepted Phase 6 handoff runs write live transcripts under:
  - `C:\Users\huibozi\.openclaw\agents\<target>\agent\sessions\handoff-*.jsonl`
- `state/sessions/index.json` still indexes the pre-existing normalized session set and summary files, but not those handoff transcript files

Resolution:

- Phase 6 acceptance used the live transcript path directly when verifying `prompt_prefix`
- no attempt was made to force this transcript family into the existing normalized session index during Phase 6

Parity implication:

- this is a known follow-up hardening opportunity
- it does not block Phase 6 acceptance because the live transcript evidence exists and is auditable

### 4. `validate_full_openclaw.py` now returns `2` for expected historical warnings, not because Phase 6 failed

Observed runtime evidence:

- fresh validation produced:
  - `exit_code = 2`
  - `status = warn`
- all warnings came from older accepted Phase 5 handoff events that predate `context_hash`

Resolution:

- keep those warnings visible
- treat them as expected migration/history warnings rather than Phase 6 execution failures

Parity implication:

- Phase 6 validation is honest about history
- current Phase 6 behavior still meets its acceptance bar because no new Phase 6 accepted event is missing `context_hash`

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase6_shared_context.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
openclaw plugins inspect handoff-bridge --json
```

Observed result:

- Node plugin tests: `11/11 pass`
- Phase 6 Python tests: `4/4 pass`
- `openclaw-full-validation.json`: `warn`
- `validate_full_openclaw.py` exit code: `2`
- plugin inspect reports:
  - `status = loaded`
  - `gatewayMethods = ["handoff.trigger"]`
  - `services = ["handoff-bridge-runtime"]`
  - typed hooks:
    - `message_received`
    - `inbound_claim`

Additional observed outputs:

- `state/sessions/summaries/` now contains `2` deterministic summary files
- current normalized state observations:
  - `sessions = 17`
  - `session_summaries = 2`
  - `cron_runs = 7`
  - `handoff_events = 6`
  - `credentials_files = 3`
  - `devices_files = 3`
  - `memory_databases = 2`
  - `memory_file_roots = 7`
- current declaration observations:
  - `bindings = 3`
  - `channels = 3`
  - `rules = 9`
  - `connectors = 3`
  - `memory = 9`
  - `handoffs = 3`
- current memory policy examples confirm the locked boundary:
  - `research-learnings` uses `shared_write_policy = both`
  - `shared-learnings` uses `shared_write_policy = read_only`
- latest accepted handoff event preserves non-empty:
  - `run_id`
  - `session_ref`
  - `decl_generation`
  - `context_hash`
  - `context_refs.source_session_summary_ref`
- the live target transcript:
  - `C:\Users\huibozi\.openclaw\agents\research\agent\sessions\handoff-daily-to-research-2026-04-02T17-12-32-303Z.jsonl`
  shows the Phase 6 `prompt_prefix` in the first user prompt

## Intentionally deferred surfaces

These remained deferred by design during Phase 6:

- no full shared live session runtime
- no concurrent multi-agent transcript merge
- no automatic indexing yet for `agent/sessions/handoff-*.jsonl` into `state/sessions/index.json`
- no promotion of handoff to a unified core concept
- no mutation of `decl/handoffs/`
- no mutation of `memory/*.sqlite`

## Known residual risk

- `validate_full_openclaw.py` still reports expected historical warnings for older Phase 5 accepted events missing `context_hash`
- `plugins.allow` still does not explicitly pin trust for `handoff-bridge`
- `state/sessions/index.json` still omits live `handoff-*.jsonl` transcript files

None of these residual items blocked Phase 6 acceptance.

## Assessment

OpenClaw Phase 6 achieved implementation parity with the locked shared-context / joint-session-lite design.

The biggest adjustments were runtime adapter clarifications rather than architecture changes:

- declaration templates and realized runtime context had to stay separate
- summary generation had to require an explicit source session
- target transcript verification had to read the live handoff transcript family directly
- expected historical warnings had to remain visible without being misread as Phase 6 failure

The result is a validated shared-context layer where handoff declarations, deterministic summaries, runtime context hashing, memory write-policy declarations, live target transcripts, and full validation now form one auditable continuation surface.
