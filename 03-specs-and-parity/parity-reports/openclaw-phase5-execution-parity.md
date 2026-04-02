# OpenClaw Phase 5 Execution Parity

Date: 2026-04-02

## Purpose

Record how the live `C:\Users\huibozi\.openclaw` implementation compared to the approved Phase 5 handoff execution runtime design and written implementation plan.

This report captures execution parity, runtime-driven clarifications, and the concrete adapter decisions required to turn canonical handoff declarations into real, auditable execution through a native OpenClaw plugin bridge.

## Direct matches to the blueprint

- `decl/handoffs/` remained the read-only fact source for live handoff policies.
- A native plugin bridge now exists under:
  - `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\`
- The plugin now loads as a native OpenClaw plugin with:
  - one service: `handoff-bridge-runtime`
  - one gateway method: `handoff.trigger`
  - two typed hooks:
    - `message_received`
    - `inbound_claim`
- The execution bridge now uses `api.runtime.agent.runEmbeddedPiAgent(...)` as the handoff run primitive.
- `state/handoff-events/events.jsonl` now exists as the append-only live audit stream.
- `state/handoff-events/index.json` now acts as the validator-facing summary surface rebuilt from the event log.
- The Phase 4 handoff status semantics are now exercised by real runtime events:
  - `accepted`
  - `escalated`
- Declaration validation and state validation now cover the live event layer:
  - accepted events must preserve non-empty `run_id`
  - accepted events must preserve non-empty `session_ref`
  - every event must preserve `trigger_ref`
  - every event must preserve `decl_generation`

## Runtime clarifications discovered during implementation

Phase 5 surfaced four live-runtime clarifications that materially shaped the implementation.

### 1. Binding-trigger execution cannot rely on a `bindingId` event field

Observed runtime evidence:

- public SDK hook types for:
  - `message_received`
  - `inbound_claim`
  do not guarantee a `bindingId`
- the live canonical binding surface already contains enough structure in:
  - `decl/bindings/*/binding.json`

Resolution:

- the bridge now evaluates canonical binding declarations itself
- matching is performed against:
  - `channel`
  - optional `account`
  - `context`
  - `pattern`
  - `pattern_mode`
- Phase 5 therefore dispatches handoff from canonical routing declarations instead of trusting a runtime-only binding identifier

Parity implication:

- the blueprint intent was preserved
- the actual dispatch path had to become more declaration-driven than originally assumed

### 2. `runEmbeddedPiAgent(...)` needs full target-agent identity, not only prompt/session inputs

Observed runtime evidence:

- a first live manual handoff attempt escalated with target-run startup failure because the embedded runner fell back to the wrong auth/model surface
- the plugin SDK type surface for `RunEmbeddedPiAgentParams` accepts:
  - `agentId`
  - `agentDir`
  - `provider`
  - `model`

Resolution:

- the executor now passes the full target-agent identity bundle
- provider/model are derived from canonical target-agent declarations
- physical agent directory resolution honors adapter notes where logical id and physical dir differ

Parity implication:

- the Phase 5 execution primitive was correct
- but the live runtime required a richer target envelope than the initial minimal wrapper

### 3. Recorder state paths must normalize through `api.runtime.state.resolveStateDir()`

Observed runtime evidence:

- the runtime helper returned the OpenClaw root, not an already-suffixed `...\state` directory
- an early accepted event therefore landed under:
  - `C:\Users\huibozi\.openclaw\handoff-events\`
  instead of:
  - `C:\Users\huibozi\.openclaw\state\handoff-events\`

Resolution:

- the recorder now normalizes the runtime root into canonical `state/handoff-events`
- legacy misplaced event files are treated as a migration case and folded into the canonical state surface
- `rebuild_state_indexes_openclaw.py` now rebuilds `state/handoff-events/index.json` from `events.jsonl` instead of resetting it to an empty placeholder

Parity implication:

- the bridge remained within the Phase 5 state-only safety boundary
- but state path normalization had to become an explicit runtime adapter rule

### 4. Local plugin trust remains an operator concern, not a Phase 5 blocker

Observed runtime evidence:

- `openclaw plugins inspect handoff-bridge --json` reports the plugin as loaded
- inspect also reports a diagnostic:
  - local extension loaded without install/load-path provenance

Resolution:

- keep the plugin live and verified
- record the trust diagnostic as an operator follow-up rather than a Phase 5 blocker

Parity implication:

- this is a residual operational hardening item
- it does not invalidate the execution/runtime acceptance criteria

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase5_handoff_runtime.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
openclaw plugins inspect handoff-bridge --json
```

Observed result:

- Node plugin tests: `10/10 pass`
- Phase 5 Python runtime test: `PASS`
- `openclaw-full-validation.json`: `pass`
- `openclaw-state-health.json`: `pass`
- `validate_full_openclaw.py` exit code: `0`
- plugin inspect reports:
  - `status = loaded`
  - `gatewayMethods = ["handoff.trigger"]`
  - `services = ["handoff-bridge-runtime"]`
  - typed hooks:
    - `message_received`
    - `inbound_claim`

Additional observed outputs:

- live handoff event log now exists:
  - `state/handoff-events/events.jsonl`
- normalized handoff summary now preserves live execution fields:
  - `run_id`
  - `session_ref`
  - `decl_generation`
- live accepted handoff evidence exists for:
  - `research-to-profit`
- current normalized state observations:
  - `sessions = 17`
  - `cron_runs = 7`
  - `handoff_events = 3`
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

## Intentionally deferred surfaces

These remained deferred by design during Phase 5:

- no automatic cron-ref live dispatch yet through a dedicated public cron hook
- no shared live joint-session runtime
- no promotion of handoff to a unified core concept
- no mutation of `decl/handoffs/`
- no mutation of `openclaw.json`
- no mutation of live session transcripts
- no mutation of `memory/*.sqlite`

## Known residual risk

- `plugins.allow` still does not explicitly pin trust for `handoff-bridge`
- plugin inspect reports this as a local trust/provenance warning
- this is an operational hardening follow-up
- it does not block or invalidate Phase 5 acceptance

## Assessment

OpenClaw Phase 5 achieved implementation parity with the locked handoff execution runtime design.

The biggest adjustments were runtime adapter clarifications rather than architecture changes:

- handoff dispatch had to become canonical-match driven instead of relying on a runtime `bindingId`
- embedded agent execution had to carry complete target-agent identity
- recorder state paths had to be normalized through the runtime state root
- local plugin trust remains a separate operator hardening concern

The result is a validated execution layer where `decl/handoffs`, plugin bridge runtime, `runEmbeddedPiAgent(...)`, `state/handoff-events/events.jsonl`, `state/handoff-events/index.json`, and full validation now operate as one auditable execution surface.
