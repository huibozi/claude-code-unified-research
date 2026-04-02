# OpenClaw Phase 2 Routing Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `C:\Users\huibozi\.openclaw` routing declarations from imported static JSON into a schema-validated, cross-referenced routing surface for bindings, channels, gateway, rules, and provider connectors.

**Architecture:** Keep the live runtime surfaces in place and evolve only the canonical declaration layer under `decl/`, the metadata indexes under `state/`, and the derived registries, reports, and snapshots under `generated/`. Phase 2 deepens `bindings / channels / gateway` first, then adds the minimum `rules / mcp` objects needed to make routing explicit, referential, and auditable without changing `openclaw.json`, `credentials/`, `devices/`, `memory/*.sqlite`, or distributed live session transcripts.

**Tech Stack:** PowerShell 7+, Python 3.11, `json`, `jsonschema`, JSON Schema Draft 2020-12, Markdown, live OpenClaw runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `C:\Users\huibozi\.openclaw\openclaw.json` remains the live runtime config and compatibility surface.
- `agents\*\sessions\*.jsonl` remain the live transcript source; `state\sessions\index.json` stays metadata-only.
- `credentials\*`, `devices\*`, and `memory\*.sqlite` remain in place and stay metadata-indexed only.
- `rules\` and `mcp\` currently exist only as canonical roots under `decl\`; Phase 2 fills them with the minimum routing-adjacent content required for validation.
- Validation order stays locked as `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`.
- Exit codes remain `0 = pass`, `1 = error`, `2 = warn`.

## Phase 2 Deliverables

- Structured `binding.match` and discriminated `binding.action`
- Structured `channel.accounts` and `channel.groups` lifted from `_adapter_config`
- `gateway.routing_rules[]` plus `gateway.policy_refs[]`
- At least one explicit routing-adjacent policy under `decl\rules\`
- At least one explicit provider connector under `decl\mcp\`
- Cross-reference validation for:
  - `binding.match.channel -> channels.registry`
  - `binding.action.agent_id -> agents.registry`
  - `gateway.routing_rules[*].target.binding_refs[] -> bindings.registry`
  - `channel.connector_refs[] -> mcp.registry`
  - `channel.policy_refs[]` and `channel.accounts.*.policy_refs[] -> rules.registry`
  - `gateway.policy_refs[] -> rules.registry`

## Files To Modify

**Canonical declaration data**
- Modify `C:\Users\huibozi\.openclaw\decl\bindings\*\binding.json`
- Modify `C:\Users\huibozi\.openclaw\decl\channels\*\channel.json`
- Modify `C:\Users\huibozi\.openclaw\decl\gateway\gateway.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\<id>\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\mcp\<id>\connector.json`

**Schemas**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\binding.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\channel.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\gateway.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\policy.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\connector.schema.json`

**Import and validation scripts**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_mcp_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`

**Documentation**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

## Target Shapes

**Binding**

```json
{
  "id": "binding-daily-001",
  "description": "Route Telegram personal DMs to the daily agent.",
  "match": {
    "channel": "telegram",
    "account": "personal",
    "pattern": "*",
    "pattern_mode": "glob",
    "context": "dm"
  },
  "action": {
    "type": "forward_to_agent",
    "agent_id": "daily"
  },
  "enabled": true,
  "priority": 50
}
```

**Channel**

```json
{
  "id": "telegram",
  "kind": "telegram",
  "description": "Imported from openclaw.json channels.telegram",
  "auth_ref": "OPENCLAW_TELEGRAM_PERSONAL_BOT_TOKEN",
  "capabilities": ["messaging", "routing"],
  "enabled": true,
  "connector_refs": ["telegram-bot-personal"],
  "policy_refs": ["dm-open"],
  "accounts": {
    "personal": {
      "enabled": true,
      "dm_policy": "open",
      "group_policy": "disabled",
      "allowlist": ["*"],
      "policy_refs": ["dm-open"]
    }
  },
  "_adapter_config": {
    "streaming": "partial"
  }
}
```

**Gateway**

```json
{
  "id": "gateway",
  "mode": "local",
  "bind": "loopback",
  "port": 18789,
  "auth_mode": "token",
  "allow_tailscale": true,
  "allowed_origins": ["http://localhost:18789"],
  "policy_refs": ["gateway-auth"],
  "routing_rules": [
    {
      "priority": 10,
      "condition": {
        "channel": "telegram",
        "account": "personal"
      },
      "target": {
        "type": "bindings",
        "binding_refs": ["binding-daily-001"]
      }
    }
  ]
}
```

## Task 1: Deepen Binding Schema And Import

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\binding.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\bindings\*\binding.json`

- [ ] Update `binding.schema.json` so `match` is no longer opaque and `action` is required.

```json
{
  "required": ["id", "match", "action", "enabled", "priority"],
  "properties": {
    "match": {
      "type": "object",
      "required": ["channel"],
      "properties": {
        "channel": {"type": "string"},
        "account": {"type": "string"},
        "pattern": {"type": "string"},
        "pattern_mode": {"type": "string", "enum": ["literal", "glob", "regex"]},
        "context": {"type": "string", "enum": ["dm", "group", "all"]}
      }
    },
    "action": {
      "type": "object",
      "required": ["type", "agent_id"],
      "properties": {
        "type": {"type": "string", "const": "forward_to_agent"},
        "agent_id": {"type": "string"}
      }
    }
  }
}
```

- [ ] Update `import_decl_openclaw.py` so imported bindings normalize missing fields instead of leaving them implicit.

```python
def normalize_match(raw: dict[str, object]) -> dict[str, object]:
    return {
        "channel": raw.get("channel", "unknown"),
        "account": raw.get("account"),
        "pattern": raw.get("pattern", "*"),
        "pattern_mode": raw.get("patternMode", "glob"),
        "context": raw.get("context", "all"),
    }
```

```python
{
    "id": generated_id,
    "description": "",
    "match": normalize_match(item.get("match", {})),
    "action": {"type": "forward_to_agent", "agent_id": target_agent},
    "enabled": True,
    "priority": 50,
}
```

- [ ] Re-import bindings and inspect one file.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\bindings\binding-daily-001\binding.json
```

Expected: each binding contains `match.channel`, `match.pattern_mode`, `action.type`, and `action.agent_id`.

## Task 2: Deepen Channel Schema And Import

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\channel.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\channels\*\channel.json`

- [ ] Expand `channel.schema.json` to support top-level `accounts`, `groups`, `connector_refs`, and `policy_refs`.

```json
{
  "properties": {
    "connector_refs": {"type": "array", "items": {"type": "string"}},
    "policy_refs": {"type": "array", "items": {"type": "string"}},
    "accounts": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["enabled", "dm_policy", "group_policy", "allowlist"],
        "properties": {
          "enabled": {"type": "boolean"},
          "dm_policy": {"type": "string", "enum": ["open", "restricted", "pairing", "disabled"]},
          "group_policy": {"type": "string", "enum": ["open", "restricted", "allowlist", "disabled"]},
          "allowlist": {"type": "array", "items": {"type": "string"}},
          "policy_refs": {"type": "array", "items": {"type": "string"}}
        }
      }
    },
    "groups": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "require_mention": {"type": "boolean"},
          "policy_refs": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

- [ ] Update `import_decl_openclaw.py` so Telegram accounts and Feishu groups are lifted into structured fields while `_adapter_config` keeps provider-specific remainder.

```python
channel_payload = {
    "id": channel_id,
    "kind": channel_id,
    "description": f"Imported from openclaw.json channels.{channel_id}",
    "auth_ref": env_ids[0] if len(env_ids) == 1 else None,
    "capabilities": ["messaging", "routing"],
    "enabled": item.get("enabled", True),
    "connector_refs": [],
    "policy_refs": [],
    "accounts": normalize_accounts(item),
    "groups": normalize_groups(item),
    "_adapter_config": strip_structured_channel_fields(item),
}
```

- [ ] Re-import channels and inspect both canonical files.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\channels\telegram\channel.json
Get-Content C:\Users\huibozi\.openclaw\decl\channels\feishu\channel.json
```

Expected: Telegram has `accounts.personal`; Feishu has `groups`; both keep `_adapter_config`.

## Task 3: Add Gateway Routing Rules

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\gateway.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\gateway\gateway.json`

- [ ] Expand `gateway.schema.json` with `policy_refs` and `routing_rules`.

```json
{
  "properties": {
    "policy_refs": {"type": "array", "items": {"type": "string"}},
    "routing_rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["priority", "condition", "target"],
        "properties": {
          "priority": {"type": "integer"},
          "condition": {"type": "object"},
          "target": {
            "type": "object",
            "required": ["type", "binding_refs"],
            "properties": {
              "type": {"type": "string", "const": "bindings"},
              "binding_refs": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    }
  }
}
```

- [ ] Seed one deterministic routing rule in `import_decl_openclaw.py` so Phase 2 has a real route to validate.

```python
"routing_rules": [
    {
        "priority": 10,
        "condition": {"channel": "telegram", "account": "personal"},
        "target": {"type": "bindings", "binding_refs": ["binding-daily-001"]},
    }
],
```

- [ ] Re-import gateway and inspect.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\gateway\gateway.json
```

Expected: `routing_rules` exists with at least one `binding_refs` target.

## Task 4: Materialize Routing Policies

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\policy.schema.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\dm-open\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\group-restricted\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\gateway-auth\policy.json`

- [ ] Keep the existing base policy schema, but allow routing-adjacent metadata needed by channels and gateway.

```json
{
  "properties": {
    "routing_rules": {"type": "array"},
    "adapter_notes": {"type": "object"}
  }
}
```

- [ ] Write `import_rules_openclaw.py` to derive explicit policies from live routing semantics instead of inventing abstract ones.

```python
POLICIES = [
    {
        "id": "dm-open",
        "description": "Allow direct-message routing for explicitly open channel accounts.",
        "scope": "channel-account",
        "priority": 50,
        "allow_rules": ["dm_policy=open"],
        "deny_rules": [],
        "ask_rules": [],
        "danger_filters": [],
        "audit_requirements": ["retain-routing-log"],
    },
    {
        "id": "gateway-auth",
        "description": "Require configured gateway auth for inbound control-plane traffic.",
        "scope": "gateway",
        "priority": 100,
        "allow_rules": ["gateway.auth=token"],
        "deny_rules": [],
        "ask_rules": [],
        "danger_filters": [],
        "audit_requirements": ["retain-auth-audit-log"],
    },
]
```

- [ ] Attach generated policy refs inside channels and gateway after importing policies.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\rules
Get-Content C:\Users\huibozi\.openclaw\decl\rules\gateway-auth\policy.json
```

Expected: at least one policy exists and gateway/channel payloads can reference it.

## Task 5: Materialize Provider Connectors

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_mcp_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\connector.schema.json`
- Create `C:\Users\huibozi\.openclaw\decl\mcp\telegram-bot-personal\connector.json`
- Create `C:\Users\huibozi\.openclaw\decl\mcp\feishu-app\connector.json`

- [ ] Extend `connector.schema.json` just enough for provider connectors that back channels.

```json
{
  "properties": {
    "provider_plugin": {"type": "string"},
    "binding_refs": {"type": "array", "items": {"type": "string"}},
    "adapter_notes": {"type": "object"}
  }
}
```

- [ ] Write `import_mcp_openclaw.py` to derive connectors from channel auth surfaces without copying secrets.

```python
{
    "id": "telegram-bot-personal",
    "description": "Telegram bot connector backing channel telegram/personal.",
    "kind": "http",
    "transport": "https",
    "command": "provider-managed",
    "args": [],
    "env_policy": ["OPENCLAW_TELEGRAM_PERSONAL_BOT_TOKEN"],
    "capabilities": ["message.receive", "message.send"],
    "auth_mode": "token",
    "healthcheck": {"type": "provider-managed"},
}
```

- [ ] Update channel import or post-processing so channels point at connectors.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_mcp_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\mcp
Get-Content C:\Users\huibozi\.openclaw\decl\channels\telegram\channel.json
```

Expected: at least one connector exists and `channel.connector_refs` is non-empty.

## Task 6: Add Cross-Reference Validation

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`

- [ ] Extend `validate_decl_openclaw.py` with explicit registry-backed cross checks after schema validation.

```python
channel_ids = ids_seen["channels"]
agent_ids = ids_seen["agents"]
binding_ids = ids_seen["bindings"]
rule_ids = ids_seen["rules"]
connector_ids = ids_seen["mcp"]
```

```python
if payload["match"]["channel"] not in channel_ids:
    errors.append(f"{json_path}: unknown binding match.channel {payload['match']['channel']}")
if payload["action"]["agent_id"] not in agent_ids:
    errors.append(f"{json_path}: unknown binding action.agent_id {payload['action']['agent_id']}")
```

```python
for ref in payload.get("connector_refs", []):
    if ref not in connector_ids:
        errors.append(f"{json_path}: unknown connector_ref {ref}")
```

- [ ] Keep `validate_state_openclaw.py` metadata-only, but extend its summary so routing surface counts show up in reports.

```python
observed.update({"bindings": len(load_registry_ids("bindings")), "channels": len(load_registry_ids("channels"))})
```

- [ ] Run all three validators.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Expected: exit code `0` or `2`, never `1`.

## Task 7: Rebuild Registries, Snapshot, And Guide

**Files:**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`
- Regenerate `C:\Users\huibozi\.openclaw\generated\registries\*.registry.json`
- Regenerate `C:\Users\huibozi\.openclaw\generated\reports\openclaw-*.json`
- Regenerate `C:\Users\huibozi\.openclaw\generated\snapshots\decl-*.json`

- [ ] Run the full validation pipeline after all imports and schema changes land.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_mcp_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

- [ ] Update the operator guide with one maintenance section per new declaration family.

```markdown
## Phase 2 Routing Maintenance

- `decl/bindings/*/binding.json` owns trigger-to-agent routing.
- `decl/channels/*/channel.json` owns channel accounts, groups, policy refs, and connector refs.
- `decl/gateway/gateway.json` owns inbound routing rules and gateway policy refs.
- `decl/rules/*/policy.json` owns explicit routing-adjacent policy.
- `decl/mcp/*/connector.json` owns provider connectors referenced by channels.
```

- [ ] Confirm the generated layer matches the Phase 2 acceptance bar.

```powershell
Get-ChildItem C:\Users\huibozi\.openclaw\generated\registries
Get-Content C:\Users\huibozi\.openclaw\generated\reports\openclaw-full-validation.json
```

Expected: all 10 registries exist and `rules.registry.json` plus `mcp.registry.json` are non-empty.

## Acceptance Checklist

- `validate_full_openclaw.py` exits `0` or `2`
- binding `match.channel` is schema-validated and cross-reference-validated
- binding `match.pattern_mode` passes enum validation
- binding `action.agent_id` resolves against `decl\agents\`
- channel `accounts` and `groups` pass schema validation
- channel `connector_refs` resolve against `decl\mcp\`
- gateway contains at least one `routing_rules` entry
- `decl\rules\` contains at least one policy
- `decl\mcp\` contains at least one connector
- all 10 registries exist and `rules / mcp` registries are no longer empty

## Self-Review

- Spec coverage: the plan covers every locked Phase 2 concern: structured binding match/action, structured channels, gateway routing, routing-adjacent rules, provider connectors, cross-reference validation, and operator documentation.
- Placeholder scan: no unfinished placeholder language remains.
- Type consistency: `binding.action.agent_id`, `channel.connector_refs`, `channel.policy_refs`, and `gateway.policy_refs` use the same names throughout the tasks and acceptance criteria.
