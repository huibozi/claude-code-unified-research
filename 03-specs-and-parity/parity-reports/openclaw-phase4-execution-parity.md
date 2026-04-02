# OpenClaw Phase 4 Execution Parity

Date: 2026-04-02

## Purpose

Record how the live `C:\Users\huibozi\.openclaw` implementation compared to the approved Phase 4 handoff / delegation design and written implementation plan.

This report captures execution parity, runtime-driven clarifications, and the concrete adapter choices needed to turn agent-to-agent handoff into one validated declaration graph spanning handoff policy declarations, binding actions, agent acceptance metadata, state event indexing, and generated registries.

## Direct matches to the blueprint

- `decl/handoffs/` is now a first-class canonical declaration root for OpenClaw handoff policy declarations.
- The first live handoff declaration set contains exactly three locked policies:
  - `daily-to-research`
  - `scheduled-daily-to-research`
  - `research-to-profit`
- `binding.action` now supports the locked Phase 4 shape:
  - `forward_to_agent`
  - `handoff`
- `binding-daily-001` now routes through a canonical handoff policy instead of direct target routing:
  - `action.type = handoff`
  - `action.handoff_policy_id = daily-to-research`
- Every live canonical agent now declares `accepts_handoff_from[]`, including agents with an empty acceptance set.
- `decl/rules/` now contains the additional policy:
  - `handoff-guardrails`
- `state/handoff-events/index.json` now exists as the locked metadata-only Phase 4 event surface.
- Generated registries increased from `11` to `12` with the addition of `handoffs.registry.json`.
- Declaration validation was extended to enforce the Phase 4 cross-reference graph:
  - `binding.action.handoff_policy_id -> handoffs`
  - `handoff.initiator_agent -> agents`
  - `handoff.target_agents[] -> agents`
  - `handoff.trigger.binding_ref -> bindings`
  - `handoff.trigger.cron_ref -> cron jobs`
  - `handoff.context_transfer.memory_refs[] -> memory`
  - `agent.accepts_handoff_from[] -> agents`

## Runtime clarifications discovered during implementation

Three live-runtime details forced concrete Phase 4 clarifications.

### 1. OpenClaw command trigger support is schema-only for now

Observed runtime evidence:

- `decl/commands/` still exposes a single settings surface:
  - `_settings.json`
- there are no individually addressable command declaration objects yet

Resolution:

- keep `command_ref` in the handoff schema
- do not seed any live Phase 4 handoff policy that pretends a concrete command object exists
- constrain the first live policy set to:
  - `binding_ref`
  - `cron_ref`
  - `manual`

Parity implication:

- the blueprint decision to keep `command_ref` in schema but out of the first live seed set was necessary
- Phase 4 stayed truthful to the runtime instead of inventing fake command ids

### 2. The handoff layer rides on top of Phase 2 routing, not beside it

Observed runtime evidence:

- `binding-daily-001` was the natural live entrypoint for the first handoff policy
- `binding-freya-002` and `binding-research-003` still remained direct routing bindings
- `research` already exposed the right memory surfaces and was the first realistic acceptor:
  - `research-store`
  - `workspace-research-files`
  - `research-learnings`
  - `shared-learnings`

Resolution:

- keep the first handoff action attached to one existing binding instead of inventing a separate parallel routing lane
- use `daily-to-research` as the first canonical handoff because it already sits on the highest-value live ingress path
- keep other bindings in `forward_to_agent` mode

Parity implication:

- Phase 4 extended the existing routing surface instead of replacing it
- handoff became a targeted escalation mechanism, not a general rewrite of every binding

### 3. Phase 4 exposed a real importer ordering dependency

Observed runtime evidence:

- `import_decl_openclaw.py` rewrites channel declarations from `openclaw.json`
- that rewrite resets channel-level `connector_refs[]`
- `validate_decl_openclaw.py` still requires live messaging channels such as `telegram` and `feishu` to have non-empty `connector_refs[]`

Resolution:

- keep `import_mcp_openclaw.py` in the operational refresh chain after `import_decl_openclaw.py`
- document that Phase 4 maintenance is not only:
  - `import_handoffs_openclaw.py`
  - `validate_full_openclaw.py`
- but also the Phase 2 connector repair step:
  - `import_mcp_openclaw.py`

Parity implication:

- the handoff implementation itself was correct
- the live canonical refresh sequence needed one explicit adapter note so Phase 2 and Phase 4 stay consistent together

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase4_handoffs.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Observed result:

- `7` Phase 4 handoff tests: `PASS`
- `openclaw-full-validation.json`: `pass`
- `openclaw-state-health.json`: `pass`
- `exit_code`: `0`

Additional observed outputs:

- generated snapshot/decl generation is active and backfilled through the registry layer
- generated registries: `12`
- handoff registry entries: `3`
- normalized handoff event index:
  - exists
  - `entries = []`
  - `schema_version = 1`
- declaration observations:
  - `bindings = 3`
  - `channels = 3`
  - `rules = 9`
  - `connectors = 3`
  - `memory = 9`
  - `handoffs = 3`
- normalized state observations remained stable:
  - `sessions = 17`
  - `cron_runs = 7`
  - `handoff_events = 0`
  - `credentials_files = 3`
  - `devices_files = 3`
  - `memory_databases = 2`
  - `memory_file_roots = 7`

## Intentionally deferred surfaces

These remained deferred by design during Phase 4:

- no shared live session execution model
- no multi-agent joint-session runtime
- no live `command_ref` seed policies until command declarations become addressable objects
- no write-back into `openclaw.json`
- no mutation of `memory/*.sqlite`
- no mutation of live workspace files or session transcripts
- no event log expansion beyond `state/handoff-events/index.json`

## Assessment

OpenClaw Phase 4 achieved implementation parity with the locked handoff / delegation design.

The main execution-time adjustments were runtime clarifications, not architectural reversals:

- command-trigger support belongs in schema before it belongs in the live seed set
- handoff works best as an escalation layer on top of existing bindings
- canonical refresh order must preserve Phase 2 connector refs after Phase 4 declaration rewrites

The result is a validated handoff surface where `decl/handoffs`, `binding.action = handoff`, `agent.accepts_handoff_from[]`, `handoff-guardrails`, `state/handoff-events/index.json`, and `handoffs.registry.json` now operate as one referential declaration graph.
