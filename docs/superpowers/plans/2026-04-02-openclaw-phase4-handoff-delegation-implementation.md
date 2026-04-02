# OpenClaw Phase 4 Handoff / Delegation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add auditable handoff / delegation declarations to OpenClaw so one agent can explicitly transfer work to another with schema-validated trigger references, context-transfer rules, and state-level event indexing.

**Architecture:** Extend the existing canonical declaration layer under `C:\Users\huibozi\.openclaw\decl\` with a new `handoffs\` family, then thread handoff references through `bindings`, `agents`, `rules`, and `state\handoff-events\index.json`. Keep the live runtime surfaces (`openclaw.json`, live sessions, workspace files, sqlite stores) untouched; Phase 4 only grows the canonical declaration and metadata-index layers that already exist from Phases 1-3.

**Tech Stack:** PowerShell 7+, Python 3.11, `json`, `jsonschema`, JSON Schema Draft 2020-12, Markdown, live OpenClaw runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `C:\Users\huibozi\.openclaw\openclaw.json` remains the live runtime config and is not rewritten in Phase 4.
- `C:\Users\huibozi\.openclaw\decl\bindings\*.json` remain the routing truth source; Phase 4 only extends `action` to allow a new `handoff` variant.
- `C:\Users\huibozi\.openclaw\decl\memory\*.json` and `agent.memory_refs[]` from Phase 3 remain the fact source for context transfer.
- `C:\Users\huibozi\.openclaw\state\sessions\index.json` remains metadata-only; Phase 4 does not create shared live sessions.
- `C:\Users\huibozi\.openclaw\state\handoff-events\index.json` starts as a metadata index only; if live event volume grows later, evolve it to `events.jsonl + index.json` in a future phase.
- `C:\Users\huibozi\.openclaw\memory\*.sqlite`, `C:\Users\huibozi\.openclaw\workspace*\*`, and `C:\Users\huibozi\.openclaw\agents\*\sessions\*.jsonl` remain untouched.
- Validation order stays locked as `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`.
- Exit codes remain `0 = pass`, `1 = error`, `2 = warn`.

## Phase 4 Deliverables

- `decl\handoffs\` with three canonical OpenClaw handoff policy declarations
- `binding.schema.json` extended so `binding.action` supports:
  - `forward_to_agent`
  - `handoff`
- `agent.json` extended with `accepts_handoff_from[]`
- `decl\rules\handoff-guardrails\policy.json` to make prohibited / audited handoff paths explicit
- `state\handoff-events\index.json` with auditable event shape that includes `trigger_ref` and `decl_generation`
- `generated\registries\handoffs.registry.json`, bringing generated registry count from `11` to `12`
- Cross-reference validation for:
  - `binding.action.handoff_policy_id -> handoffs.registry`
  - `handoff.initiator_agent -> agents.registry`
  - `handoff.target_agents[] -> agents.registry`
  - `handoff.trigger.binding_ref -> bindings.registry`
  - `handoff.trigger.command_ref -> commands registry surface when present`
  - `handoff.trigger.cron_ref -> decl/cron/jobs.json`
  - `handoff.context_transfer.memory_refs[] -> memory.registry`
  - `agent.accepts_handoff_from[] -> agents.registry`

## File Map

**Canonical declaration data**
- Create `C:\Users\huibozi\.openclaw\decl\handoffs\<id>\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\bindings\binding-daily-001\binding.json`
- Modify `C:\Users\huibozi\.openclaw\decl\agents\*\agent.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\handoff-guardrails\policy.json`

**Schemas**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\handoff.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\binding.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\agent.schema.json`

**Import and validation scripts**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\bootstrap.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_handoffs_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\build_registries_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`

**Tests**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase4_handoffs.py`

**Documentation**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

## Target Shapes

**Handoff policy declaration**

```json
{
  "id": "daily-to-research",
  "description": "Escalate Feishu inbound work from daily to research.",
  "initiator_agent": "daily",
  "target_agents": ["research"],
  "trigger": {
    "type": "binding_ref",
    "binding_ref": "binding-daily-001"
  },
  "context_transfer": {
    "memory_refs": ["shared-learnings", "research-learnings"],
    "snapshot_ref": true,
    "session_ref": true
  },
  "acceptance_policy": {
    "timeout_seconds": 300,
    "on_timeout": "fail"
  },
  "audit_requirements": ["retain-handoff-event-log"]
}
```

**Binding handoff action**

```json
{
  "id": "binding-daily-001",
  "action": {
    "type": "handoff",
    "handoff_policy_id": "daily-to-research"
  }
}
```

**Agent handoff acceptance summary**

```json
{
  "id": "research",
  "accepts_handoff_from": ["daily"]
}
```
**Handoff event index entry**

```json
{
  "event_id": "handoff-20260402-001",
  "handoff_policy_id": "daily-to-research",
  "trigger_ref": "binding-daily-001",
  "decl_generation": "decl-20260402T060939Z",
  "initiator_agent": "daily",
  "target_agent": "research",
  "status": "accepted",
  "triggered_at": "2026-04-02T09:00:00Z",
  "accepted_at": "2026-04-02T09:00:05Z",
  "rejected_at": null,
  "timed_out_at": null,
  "context_refs": {
    "memory_refs": ["shared-learnings", "research-learnings"],
    "session_ref": "sess_daily_001",
    "snapshot_ref": "decl-20260402T060939Z"
  },
  "outcome_notes": "Research accepted the escalation."
}
```

## Seed Handoff Policy Set

Phase 4 seeds three policies and deliberately covers the live trigger shapes that already exist today:

- `daily-to-research`
  - `initiator_agent = daily`
  - `target_agents = [research]`
  - `trigger = binding_ref(binding-daily-001)`
- `scheduled-daily-to-research`
  - `initiator_agent = daily`
  - `target_agents = [research]`
  - `trigger = cron_ref(eae8acfe-acc9-404d-ac67-e774e15b5f12)`
- `research-to-profit`
  - `initiator_agent = research`
  - `target_agents = [profit]`
  - `trigger = manual`

`command_ref` stays in the schema in Phase 4, but no live seed policy uses it yet because `decl\commands\_settings.json` is a settings surface, not a set of individually addressable command objects.

## Task 1: Add Handoff Schema, Bootstrap Paths, And Test Scaffold

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\handoff.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\bootstrap.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase4_handoffs.py`

- [ ] Add `handoff.schema.json` with discriminated `trigger`, explicit `context_transfer`, and timeout policy.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "id",
    "description",
    "initiator_agent",
    "target_agents",
    "trigger",
    "context_transfer",
    "acceptance_policy",
    "audit_requirements"
  ],
  "properties": {
    "id": {"type": "string", "minLength": 1},
    "description": {"type": "string"},
    "initiator_agent": {"type": "string"},
    "target_agents": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string"}
    },
    "trigger": {
      "oneOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["type", "binding_ref"],
          "properties": {
            "type": {"type": "string", "const": "binding_ref"},
            "binding_ref": {"type": "string"}
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["type", "command_ref"],
          "properties": {
            "type": {"type": "string", "const": "command_ref"},
            "command_ref": {"type": "string"}
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["type", "cron_ref"],
          "properties": {
            "type": {"type": "string", "const": "cron_ref"},
            "cron_ref": {"type": "string"}
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["type"],
          "properties": {
            "type": {"type": "string", "const": "manual"}
          }
        }
      ]
    },
    "context_transfer": {
      "type": "object",
      "additionalProperties": false,
      "required": ["memory_refs", "snapshot_ref", "session_ref"],
      "properties": {
        "memory_refs": {"type": "array", "items": {"type": "string"}},
        "snapshot_ref": {"type": "boolean"},
        "session_ref": {"type": "boolean"}
      }
    },
    "acceptance_policy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["timeout_seconds", "on_timeout"],
      "properties": {
        "timeout_seconds": {"type": "integer", "minimum": 1},
        "on_timeout": {"type": "string", "enum": ["fail", "next_target", "escalate"]}
      }
    },
    "audit_requirements": {"type": "array", "items": {"type": "string"}},
    "_adapter_notes": {"type": "object"}
  }
}
```

- [ ] Extend `bootstrap.py` so a fresh Phase 4 bootstrap creates `decl\handoffs\` and `state\handoff-events\`.

```python
DECL_DIRS = [
    "agents",
    "skills",
    "commands",
    "bindings",
    "channels",
    "gateway",
    "plugins",
    "cron",
    "rules",
    "mcp",
    "memory",
    "handoffs",
]
STATE_DIRS = [
    "sessions",
    "cron-runs",
    "handoff-events",
    "indexes/memory",
    "indexes/credentials",
    "indexes/devices",
]
```
- [ ] Add a focused unittest file that validates three trigger variants and rejects malformed action payloads.

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import SCHEMAS_ROOT
from common import read_json


class Phase4HandoffSchemaTests(unittest.TestCase):
    def load_validator(self, name: str) -> Draft202012Validator:
        return Draft202012Validator(read_json(SCHEMAS_ROOT / name))

    def test_handoff_schema_accepts_binding_trigger(self) -> None:
        payload = {
            "id": "daily-to-research",
            "description": "Escalate daily work to research.",
            "initiator_agent": "daily",
            "target_agents": ["research"],
            "trigger": {"type": "binding_ref", "binding_ref": "binding-daily-001"},
            "context_transfer": {"memory_refs": ["shared-learnings"], "snapshot_ref": True, "session_ref": True},
            "acceptance_policy": {"timeout_seconds": 300, "on_timeout": "fail"},
            "audit_requirements": ["retain-handoff-event-log"],
        }
        self.load_validator("handoff.schema.json").validate(payload)

    def test_handoff_schema_accepts_cron_trigger(self) -> None:
        payload = {
            "id": "scheduled-daily-to-research",
            "description": "Escalate scheduled daily work to research.",
            "initiator_agent": "daily",
            "target_agents": ["research"],
            "trigger": {"type": "cron_ref", "cron_ref": "eae8acfe-acc9-404d-ac67-e774e15b5f12"},
            "context_transfer": {"memory_refs": ["research-learnings"], "snapshot_ref": True, "session_ref": False},
            "acceptance_policy": {"timeout_seconds": 300, "on_timeout": "next_target"},
            "audit_requirements": ["retain-handoff-event-log"],
        }
        self.load_validator("handoff.schema.json").validate(payload)

    def test_binding_schema_accepts_handoff_action(self) -> None:
        payload = {
            "id": "binding-daily-001",
            "description": "Route Feishu traffic through a handoff policy.",
            "match": {"channel": "feishu", "pattern": "*", "pattern_mode": "glob", "context": "all"},
            "action": {"type": "handoff", "handoff_policy_id": "daily-to-research"},
            "enabled": True,
            "priority": 50,
        }
        self.load_validator("binding.schema.json").validate(payload)

    def test_binding_schema_rejects_handoff_without_policy_id(self) -> None:
        payload = {
            "id": "binding-daily-001",
            "description": "Broken handoff.",
            "match": {"channel": "feishu", "pattern": "*", "pattern_mode": "glob", "context": "all"},
            "action": {"type": "handoff"},
            "enabled": True,
            "priority": 50,
        }
        with self.assertRaises(ValidationError):
            self.load_validator("binding.schema.json").validate(payload)
```

- [ ] Run the focused test file before moving on.

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase4_handoffs.py -v
```

Expected: four tests pass after the schema and bootstrap changes are in place.

## Task 2: Add Canonical Handoff Policy Imports

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_handoffs_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\decl\handoffs\daily-to-research\handoff.json`
- Create `C:\Users\huibozi\.openclaw\decl\handoffs\scheduled-daily-to-research\handoff.json`
- Create `C:\Users\huibozi\.openclaw\decl\handoffs\research-to-profit\handoff.json`

- [ ] Add an importer with one static canonical seed set and explicit live ids.

```python
from __future__ import annotations

from common import DECL_ROOT, write_json

HANDOFFS = [
    {
        "id": "daily-to-research",
        "description": "Escalate Feishu inbound work from daily to research.",
        "initiator_agent": "daily",
        "target_agents": ["research"],
        "trigger": {"type": "binding_ref", "binding_ref": "binding-daily-001"},
        "context_transfer": {
            "memory_refs": ["shared-learnings", "research-learnings"],
            "snapshot_ref": True,
            "session_ref": True,
        },
        "acceptance_policy": {"timeout_seconds": 300, "on_timeout": "fail"},
        "audit_requirements": ["retain-handoff-event-log"],
    },
    {
        "id": "scheduled-daily-to-research",
        "description": "Escalate the evening daily cron run to research when deeper analysis is needed.",
        "initiator_agent": "daily",
        "target_agents": ["research"],
        "trigger": {"type": "cron_ref", "cron_ref": "eae8acfe-acc9-404d-ac67-e774e15b5f12"},
        "context_transfer": {
            "memory_refs": ["shared-learnings", "research-learnings"],
            "snapshot_ref": True,
            "session_ref": False,
        },
        "acceptance_policy": {"timeout_seconds": 300, "on_timeout": "fail"},
        "audit_requirements": ["retain-handoff-event-log"],
    },
    {
        "id": "research-to-profit",
        "description": "Allow research to hand analysis work to profit with shared memory context.",
        "initiator_agent": "research",
        "target_agents": ["profit"],
        "trigger": {"type": "manual"},
        "context_transfer": {
            "memory_refs": ["research-store", "research-learnings", "shared-learnings"],
            "snapshot_ref": True,
            "session_ref": True,
        },
        "acceptance_policy": {"timeout_seconds": 180, "on_timeout": "escalate"},
        "audit_requirements": ["retain-handoff-event-log"],
    },
]


def main() -> None:
    for payload in HANDOFFS:
        write_json(DECL_ROOT / "handoffs" / payload["id"] / "handoff.json", payload)


if __name__ == "__main__":
    main()
```

- [ ] Run the importer and inspect the emitted canonical declarations.

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_handoffs_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\handoffs -Directory | Select-Object -ExpandProperty Name
```

Expected output:

```text
daily-to-research
research-to-profit
scheduled-daily-to-research
```
## Task 3: Extend Binding Actions To Support Handoff

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\binding.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\bindings\binding-daily-001\binding.json`

- [ ] Change `binding.schema.json` so `action` becomes a discriminated union.

```json
"action": {
  "oneOf": [
    {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "agent_id"],
      "properties": {
        "type": {"type": "string", "const": "forward_to_agent"},
        "agent_id": {"type": "string"}
      }
    },
    {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "handoff_policy_id"],
      "properties": {
        "type": {"type": "string", "const": "handoff"},
        "handoff_policy_id": {"type": "string"}
      }
    }
  ]
}
```

- [ ] Update `import_decl_openclaw.py` so `binding-daily-001` is promoted to the canonical handoff action while the other live bindings stay `forward_to_agent`.

```python
def binding_action(binding_id: str, target_agent: str) -> dict[str, Any]:
    if binding_id == "binding-daily-001":
        return {"type": "handoff", "handoff_policy_id": "daily-to-research"}
    return {"type": "forward_to_agent", "agent_id": target_agent}
```

Use it when constructing each binding payload:

```python
binding_payload = {
    "id": generated_id,
    "description": "",
    "match": normalize_match(item.get("match", {})),
    "action": binding_action(generated_id, target_agent),
    "enabled": item.get("enabled", True),
    "priority": int(item.get("priority", 50)),
}
```

- [ ] Re-run the declaration importer and confirm `binding-daily-001` now points to `daily-to-research`.

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\bindings\binding-daily-001\binding.json
```

Expected excerpt:

```json
"action": {
  "type": "handoff",
  "handoff_policy_id": "daily-to-research"
}
```

## Task 4: Add Agent Acceptance Metadata

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\agent.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\agents\*\agent.json`

- [ ] Extend `agent.schema.json` with `accepts_handoff_from[]`.

```json
"accepts_handoff_from": {
  "type": "array",
  "items": {"type": "string"}
}
```

- [ ] Add a canonical acceptance map to `import_agents_openclaw.py` and write the field for all six agents.

```python
HANDOFF_ACCEPTANCE_MAP = {
    "research": ["daily"],
    "profit": ["research"],
    "daily": [],
    "main": [],
    "personal": [],
    "freya": [],
}
```

When building each agent payload:

```python
"accepts_handoff_from": HANDOFF_ACCEPTANCE_MAP.get(agent_id, []),
```

- [ ] Re-run agent import and inspect the two non-empty acceptors.

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\agents\research\agent.json
Get-Content C:\Users\huibozi\.openclaw\decl\agents\profit\agent.json
```

Expected excerpts:

```json
"accepts_handoff_from": ["daily"]
```

```json
"accepts_handoff_from": ["research"]
```

## Task 5: Add Handoff Guardrails Policy

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\decl\rules\handoff-guardrails\policy.json`

- [ ] Extend the rules importer with one explicit handoff guardrails policy.

```python
HANDOFF_GUARDRAILS_POLICY = {
    "id": "handoff-guardrails",
    "description": "Require audit logging for live handoffs and block unsupported cross-domain delegation paths.",
    "scope": "handoff",
    "priority": 85,
    "allow_rules": ["daily-to-research", "scheduled-daily-to-research", "research-to-profit"],
    "deny_rules": ["freya->research", "personal->profit"],
    "ask_rules": [],
    "danger_filters": ["cross-domain-live-session"],
    "audit_requirements": ["retain-handoff-event-log"],
    "adapter_notes": {
        "family": "handoff-guardrails",
        "denied_paths": ["freya->research", "personal->profit"]
    }
}
```

Write it beside the existing rule imports:

```python
write_json(DECL_ROOT / "rules" / "handoff-guardrails" / "policy.json", HANDOFF_GUARDRAILS_POLICY)
```

- [ ] Re-run the rules importer and confirm the new policy exists.

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\rules -Directory | Select-Object -ExpandProperty Name
```

Expected: `handoff-guardrails` appears and rule directory count increases from `8` to `9`.
## Task 6: Validate Cross References And Build Handoff State Index

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`

- [ ] Add `handoffs` to `DECL_MAP` and `FILENAME_MAP`.

```python
DECL_MAP = {
    "agents": "agent.schema.json",
    "skills": "skill.schema.json",
    "commands": "command.schema.json",
    "bindings": "binding.schema.json",
    "channels": "channel.schema.json",
    "gateway": "gateway.schema.json",
    "plugins": "plugin.schema.json",
    "cron": "cron.schema.json",
    "rules": "policy.schema.json",
    "mcp": "connector.schema.json",
    "memory": "memory.schema.json",
    "handoffs": "handoff.schema.json",
}
```

- [ ] Extend declaration validation so handoff references are checked against live canonical ids.

```python
handoff_ids = ids_seen["handoffs"]
cron_ids = {
    job["id"]
    for _, payload in payloads_seen["cron"]
    for job in payload.get("jobs", [])
}

for json_path, payload in payloads_seen["bindings"]:
    action = payload.get("action", {})
    if action.get("type") == "handoff":
        handoff_policy_id = action.get("handoff_policy_id")
        if handoff_policy_id not in handoff_ids:
            errors.append(f"{json_path}: unknown handoff_policy_id {handoff_policy_id}")
    else:
        agent_id = action.get("agent_id")
        if agent_id and agent_id not in agent_ids:
            errors.append(f"{json_path}: unknown binding action.agent_id {agent_id}")

for json_path, payload in payloads_seen["agents"]:
    for ref in payload.get("accepts_handoff_from", []):
        if ref not in agent_ids:
            errors.append(f"{json_path}: unknown accepts_handoff_from agent {ref}")

for json_path, payload in payloads_seen["handoffs"]:
    if payload.get("initiator_agent") not in agent_ids:
        errors.append(f"{json_path}: unknown initiator_agent {payload.get('initiator_agent')}")
    for ref in payload.get("target_agents", []):
        if ref not in agent_ids:
            errors.append(f"{json_path}: unknown target_agent {ref}")
    trigger = payload.get("trigger", {})
    if trigger.get("type") == "binding_ref" and trigger.get("binding_ref") not in binding_ids:
        errors.append(f"{json_path}: unknown binding_ref {trigger.get('binding_ref')}")
    if trigger.get("type") == "cron_ref" and trigger.get("cron_ref") not in cron_ids:
        errors.append(f"{json_path}: unknown cron_ref {trigger.get('cron_ref')}")
    if trigger.get("type") == "command_ref":
        warnings.append(f"{json_path}: command_ref validation is deferred until command objects exist")
    for ref in payload.get("context_transfer", {}).get("memory_refs", []):
        if ref not in memory_ids:
            errors.append(f"{json_path}: unknown context_transfer memory_ref {ref}")
```

- [ ] Extend state index rebuilding to create a metadata-only handoff event index placeholder.

```python
write_json(
    STATE_ROOT / "handoff-events" / "index.json",
    {
        "entries": [],
        "schema_version": 1,
    },
)
```

- [ ] Extend state validation so the new index is required and any future entries must include `trigger_ref`, `decl_generation`, and structured `context_refs`.

```python
handoff_index_path = STATE_ROOT / "handoff-events" / "index.json"
for required in [session_index_path, cron_runs_index_path, credentials_index_path, devices_index_path, memory_index_path, handoff_index_path]:
    if not required.exists():
        errors.append(f"missing {required}")

if handoff_index_path.exists():
    payload = read_json(handoff_index_path)
    entries = payload.get("entries", [])
    for entry in entries:
        for field in ("event_id", "handoff_policy_id", "trigger_ref", "decl_generation", "initiator_agent", "target_agent", "status", "context_refs"):
            if field not in entry:
                errors.append(f"handoff event missing {field}: {entry}")
```

- [ ] Run declaration and state validation directly.

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
```

Expected: all three commands return `0` after the new handoff files and placeholder index are present.

## Task 7: Extend Registry, Full Validation, And Snapshot Flow

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\build_registries_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`

- [ ] Extend registry generation with the new handoff family.

```python
GROUPS = {
    "agents": "agent.json",
    "skills": "skill.json",
    "commands": "_settings.json",
    "bindings": "binding.json",
    "channels": "channel.json",
    "gateway": "gateway.json",
    "plugins": "plugin.json",
    "cron": "jobs.json",
    "rules": "policy.json",
    "mcp": "connector.json",
    "memory": "memory.json",
    "handoffs": "handoff.json",
}
```

- [ ] Increase full validation expectations from `11` registries to `12` and require `handoffs.registry.json` to be non-empty.

```python
registry_paths = sorted(REGISTRIES_ROOT.glob("*.registry.json"))
if len(registry_paths) != 12:
    errors.append(f"expected 12 registry files, found {len(registry_paths)}")
else:
    for required_non_empty in ("rules", "mcp", "memory", "handoffs"):
        registry = read_json(REGISTRIES_ROOT / f"{required_non_empty}.registry.json")
        if not registry.get("entries"):
            errors.append(f"expected non-empty {required_non_empty}.registry.json")
```

- [ ] Run full validation to regenerate registries, snapshot, and backfilled `decl_generation`.

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\generated\registries -File | Select-Object -ExpandProperty Name
```

Expected:
- `validate_full_openclaw.py` exits `0` or `2`
- `handoffs.registry.json` exists
- total registry count is `12`
## Task 8: Document The Operating Model

**Files:**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

- [ ] Add a Phase 4 section that explains the handoff declaration family, binding action variants, acceptance metadata, and state event index expectations.

```markdown
## Phase 4: Handoff / Delegation

OpenClaw now supports canonical handoff policy declarations under `decl/handoffs/`.

- `binding.action.type = forward_to_agent` keeps direct routing.
- `binding.action.type = handoff` routes through a handoff policy.
- `agent.accepts_handoff_from[]` states which initiators a target agent will accept.
- `state/handoff-events/index.json` is metadata-only in Phase 4 and records auditable handoff outcomes.

Phase 4 does not create shared live sessions. Shared memory remains attached through `memory_refs[]`, and handoff only passes references to those surfaces.
```

- [ ] Add the concrete maintenance commands operators should run after editing handoff policy declarations.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_handoffs_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

## Task 9: Final Verification Sweep

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase4_handoffs.py`
- Verify generated outputs under `C:\Users\huibozi\.openclaw\generated\reports\`

- [ ] Expand the Phase 4 test file so it covers the final live shapes, not just schema scaffolding.

```python
    def test_imported_daily_binding_uses_handoff_action(self) -> None:
        payload = read_json(Path(r"C:\Users\huibozi\.openclaw\decl\bindings\binding-daily-001\binding.json"))
        self.assertEqual(payload["action"], {"type": "handoff", "handoff_policy_id": "daily-to-research"})

    def test_imported_research_agent_accepts_daily_handoff(self) -> None:
        payload = read_json(Path(r"C:\Users\huibozi\.openclaw\decl\agents\research\agent.json"))
        self.assertEqual(payload["accepts_handoff_from"], ["daily"])

    def test_handoff_registry_is_non_empty_after_full_validation(self) -> None:
        payload = read_json(Path(r"C:\Users\huibozi\.openclaw\generated\registries\handoffs.registry.json"))
        self.assertEqual(len(payload["entries"]), 3)
```

- [ ] Run the test suite and the full validator one last time.

Run:

```powershell
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase4_handoffs.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\generated\reports\openclaw-full-validation.json
```

Expected final checks:
- `test_phase4_handoffs.py` passes
- `validate_full_openclaw.py` exits `0` or `2`, never `1`
- `decl\handoffs\` contains exactly `3` policy directories
- `state\handoff-events\index.json` exists
- `generated\registries\` contains `12` registry files
- `decl\rules\` contains `9` policy directories

## Spec Coverage Self-Review

This plan covers each locked Phase 4 requirement:

- OpenClaw-local `decl\handoffs\` family -> Tasks 1-2
- discriminated `trigger` with `binding_ref | command_ref | cron_ref | manual` -> Task 1, Task 6
- `binding.action.type = handoff` -> Task 3
- `agent.accepts_handoff_from[]` -> Task 4
- `handoff-guardrails` policy -> Task 5
- `state\handoff-events\index.json` with `trigger_ref` and `decl_generation` -> Task 6
- registry growth from `11` to `12` -> Task 7
- operator guide updates -> Task 8
- full validation and final evidence -> Task 9

No requirement from the locked blueprint is intentionally deferred except live `command_ref` usage, which is explicitly kept schema-only because the current OpenClaw command surface is still `decl\commands\_settings.json` rather than addressable command objects.

## Placeholder Scan Self-Review

Checked for the following red flags and removed them:
- `TBD`
- `TODO`
- `implement later`
- `similar to Task N`
- vague `add validation` / `handle edge cases`

Every task above names exact files, concrete code shapes, and exact commands to run.

## Type Consistency Self-Review

Confirmed the same names are used consistently throughout the plan:
- declaration family: `handoffs`
- declaration filename: `handoff.json`
- registry file: `handoffs.registry.json`
- state file: `state\handoff-events\index.json`
- binding variant: `action.type = handoff`
- handoff ref field: `handoff_policy_id`
- agent field: `accepts_handoff_from[]`
- event audit fields: `trigger_ref`, `decl_generation`

No alternate spellings are introduced for the same concept.
