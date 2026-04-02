# OpenClaw Phase 2 Execution Parity

Date: 2026-04-02

## Purpose

Record how the live `C:\Users\huibozi\.openclaw` implementation compared to the approved Phase 2 routing-surface blueprint and the written implementation plan.

This report captures execution parity, runtime-driven clarifications, and the concrete adapter choices needed to make `bindings / channels / gateway / rules / mcp` operate as one validated routing surface.

## Direct matches to the blueprint

- `binding.match` was upgraded from opaque runtime passthrough to a structured declaration with:
  - `channel`
  - `account`
  - `pattern`
  - `pattern_mode`
  - `context`
- `binding.action` was upgraded to the locked Phase 2 discriminated form:
  - `type = forward_to_agent`
  - `agent_id`
- `channel.json` was upgraded to support:
  - `accounts`
  - `groups`
  - `connector_refs`
  - `policy_refs`
  - retained `_adapter_config`
- `gateway.json` was upgraded to support:
  - `policy_refs`
  - `routing_rules[]`
  - direct `binding_refs` targets instead of any `binding_group` abstraction
- `decl/rules/` is no longer an empty canonical root. It now contains routing-adjacent policies:
  - `dm-open`
  - `group-restricted`
  - `gateway-auth`
- `decl/mcp/` is no longer an empty canonical root. It now contains live provider connectors:
  - `telegram-bot-personal`
  - `feishu-app`
  - `minimax-portal`
- Declaration validation was extended to enforce the Phase 2 cross-reference graph:
  - `binding.match.channel -> channels`
  - `binding.action.agent_id -> agents`
  - `gateway.routing_rules[*].target.binding_refs[] -> bindings`
  - `channel.connector_refs[] -> mcp`
  - `channel.policy_refs[] -> rules`
  - `channel.accounts.*.policy_refs[] -> rules`
  - `channel.groups.*.policy_refs[] -> rules`
  - `gateway.policy_refs[] -> rules`

## Runtime clarifications discovered during implementation

Three live-runtime details forced concrete Phase 2 clarifications.

### 1. A binding can target a routing surface that is not declared in `openclaw.json:channels`

Observed runtime evidence:

- `binding-research-003` targets channel `tailscale`
- `openclaw.json:channels` only declares:
  - `telegram`
  - `feishu`

Resolution:

- synthesize canonical `decl/channels/tailscale/channel.json`
- mark it as `kind = internal`
- keep it additive rather than rewriting the runtime config

Parity implication:

- the blueprint goal of validating `binding.match.channel` remained correct
- the runtime required one adapter-owned internal channel declaration to make the cross-reference graph complete

### 2. Provider connectors come from more than one live config surface

Observed runtime evidence:

- `telegram` and `feishu` connectors are discoverable from `channels.*`
- the live MiniMax provider is discoverable from `models.providers.minimax-portal`

Resolution:

- derive channel-backed connectors from channel auth surfaces
- derive provider connector `minimax-portal` from `models.providers`
- keep all of them under canonical `decl/mcp/*/connector.json`

Parity implication:

- the blueprint decision to fill `mcp/` in Phase 2 stayed correct
- the importer had to treat both channel auth and model provider config as connector evidence

### 3. Policy refs are not stored explicitly in the native runtime config

Observed runtime evidence:

- `openclaw.json` and imported channel payloads express routing behavior implicitly through:
  - `dmPolicy`
  - `groupPolicy`
  - `requireMention`
  - gateway auth settings
- native payloads do not provide first-class `policy_refs`

Resolution:

- add a dedicated `import_rules_openclaw.py`
- derive explicit canonical policies from the live routing semantics
- attach resulting `policy_refs` back onto canonical channel and gateway declarations

Parity implication:

- rules had to be materialized as a canonical interpretation layer
- this preserved the blueprint goal of explicit policy references without mutating the native runtime config

## Verification evidence

Fresh execution evidence from the live runtime:

```powershell
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase2_routing.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Observed result:

- `5` Phase 2 routing tests: `PASS`
- `openclaw-decl-health.json`: `pass`
- `openclaw-state-health.json`: `pass`
- `openclaw-full-validation.json`: `pass`
- `exit_code`: `0`

Additional observed outputs:

- rollback checkpoint: `C:\Users\huibozi\.openclaw\backups\decl-state\phase2-20260402T130058Z`
- generated snapshot: `C:\Users\huibozi\.openclaw\generated\snapshots\decl-20260402T051020Z.json`
- generated registries: `10`
- registry summary:
  - `bindings = 3`
  - `channels = 3`
  - `rules = 3`
  - `mcp = 3`
- normalized state observations remained stable:
  - `sessions = 17`
  - `cron_runs = 7`
  - `credentials_files = 3`
  - `devices_files = 3`
  - `memory_databases = 2`

## Intentionally deferred surfaces

These remained deferred by design during Phase 2:

- no rewrite-back into `openclaw.json`
- no mutation of `credentials/`, `devices/`, or `memory/*.sqlite`
- no transcript copying out of `agents/*/sessions/*.jsonl`
- no deeper semantic import of memory records from `memory/*.sqlite`
- no attempt to normalize every runtime-specific provider field out of `_adapter_config`

## Assessment

OpenClaw Phase 2 achieved implementation parity with the locked routing-surface design.

The main execution-time adjustments were adapter clarifications, not architectural reversals:

- synthetic internal channels for binding-only routing surfaces
- connector discovery across both channel and model-provider config
- explicit canonical policies derived from implicit runtime routing semantics

The result is a validated routing surface where `bindings`, `channels`, `gateway`, `rules`, and `mcp` now form one referential declaration graph.
