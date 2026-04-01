# OpenClaw Phase 1 Decl-State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add canonical `decl/`, `state/`, and `generated/` layers to `C:\Users\huibozi\.openclaw` without changing the live runtime behavior that still depends on `openclaw.json`, `agents/`, `skills/`, `cron/`, `credentials/`, `devices/`, `memory/*.sqlite`, and distributed session files.

**Architecture:** Keep OpenClaw native runtime surfaces in place and treat them as adapter inputs, not migration targets. Extract declaration-shaped content into additive JSON declarations under `decl/`, build normalized metadata and index views under `state/`, and emit disposable registries, reports, and snapshots under `generated/`. Validation follows the locked order `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`, with exit codes `0 = pass`, `1 = error`, and `2 = warn`.

**Tech Stack:** PowerShell 7+, Python 3.11, `json`, `sqlite3`, Markdown, JSON Schema Draft 2020-12, live OpenClaw runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `openclaw.json` stays the live runtime config and compatibility surface.
- `agents/*/sessions/*.jsonl`, `skills/*`, `cron/jobs.json`, `cron/runs/*.jsonl`, `credentials/*`, `devices/*`, `memory/*.sqlite`, and `workspace*` stay in place.
- `credentials/`, `devices/`, and `memory/*.sqlite` are metadata-indexed only.
- `C:\Users\huibozi\.openclaw` is not a git repo, so rollback uses `backups\decl-state\`.
- Every read of `openclaw.json` must go through one shared `read_jsonc()` helper.

## Target Layout

```text
C:\Users\huibozi\.openclaw\
  decl\agents skills commands bindings channels gateway plugins cron rules mcp
  state\sessions cron-runs indexes\memory credentials devices
  generated\registries reports snapshots
  scripts\decl_state\schemas
```

## Mapping Summary

| Source | Canonical destination |
|---|---|
| `openclaw.json:agents.list[]` | `decl/agents/<id>/agent.json` |
| `openclaw.json:agents.defaults` | `decl/agents/_defaults.json` |
| `openclaw.json:commands` | `decl/commands/_settings.json` |
| `openclaw.json:bindings[]` | `decl/bindings/<id>/binding.json` |
| `openclaw.json:channels.<id>` | `decl/channels/<id>/channel.json` |
| `openclaw.json:gateway` | `decl/gateway/gateway.json` |
| `openclaw.json:plugins.entries.<id>` | `decl/plugins/<id>/plugin.json` |
| `skills/<name>/SKILL.md + package.json` | `decl/skills/<id>/skill.json + skill.md` |
| `cron/jobs.json` | `decl/cron/jobs.json` |
| `cron/runs/*.jsonl` | `state/cron-runs/index.json` |
| `agents/*/sessions/*.jsonl` | `state/sessions/index.json` |

## Schema / Registry Set

Schemas under `scripts\decl_state\schemas\`:
- `agent.schema.json`
- `skill.schema.json`
- `command.schema.json`
- `binding.schema.json`
- `channel.schema.json`
- `gateway.schema.json`
- `plugin.schema.json`
- `cron.schema.json`
- `policy.schema.json`
- `connector.schema.json`

Registries under `generated\registries\`:
- `agents.registry.json`
- `skills.registry.json`
- `commands.registry.json`
- `bindings.registry.json`
- `channels.registry.json`
- `gateway.registry.json`
- `plugins.registry.json`
- `cron.registry.json`
- `rules.registry.json`
- `mcp.registry.json`

OpenClaw-specific payload shapes:

```json
{"id":"binding-research-002","description":"","match":{"channel":"tailscale"},"target_agent":"research","enabled":true,"priority":50}
```

```json
{"id":"telegram","kind":"telegram","description":"Imported from openclaw.json channels.telegram","auth_ref":"OPENCLAW_TELEGRAM_PERSONAL_BOT_TOKEN","capabilities":["messaging"],"enabled":true,"_adapter_config":{"accounts":{"personal":{"enabled":true,"dmPolicy":"open","groupPolicy":"disabled"}}}}
```

## Task 1: Inventory And Rollback Checkpoint

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\inventory_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\generated\reports\openclaw-bootstrap-inventory.json`
- Create `C:\Users\huibozi\.openclaw\backups\decl-state\bootstrap-<timestamp>\inventory\openclaw.json`
- Create `C:\Users\huibozi\.openclaw\backups\decl-state\bootstrap-<timestamp>\inventory\openclaw.current.json`

- [ ] Write `inventory_openclaw.py` so every top-level path is labeled `runtime-config`, `decl-candidate`, `state-candidate`, `sensitive`, `workspace`, or `unknown`.

```python
CATEGORY_MAP = {"openclaw.json": "runtime-config", "agents": "decl-candidate", "credentials": "sensitive", "workspace": "workspace"}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\inventory_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\generated\reports\openclaw-bootstrap-inventory.json -TotalCount 60
```

Expected: `openclaw.json` is `runtime-config`; `credentials`, `devices`, and `memory` are `sensitive`.

- [ ] Create the additive backup checkpoint before any canonical writes:

```powershell
$stamp = Get-Date -Format 'yyyyMMddTHHmmssZ'
$root = "C:\Users\huibozi\.openclaw\backups\decl-state\bootstrap-$stamp\inventory"
New-Item -ItemType Directory -Force -Path $root | Out-Null
Copy-Item C:\Users\huibozi\.openclaw\openclaw.json "$root\openclaw.json"
Copy-Item C:\Users\huibozi\.openclaw\openclaw.current.json "$root\openclaw.current.json"
```

## Task 2: Bootstrap Roots, Helpers, And Schemas

**Files:**
- Create `decl\README.md`, `state\README.md`, `generated\README.md`, `generated\.gitignore`
- Create `scripts\decl_state\common.py`, `parsers.py`, `bootstrap.py`
- Create ten schema files under `scripts\decl_state\schemas\`

- [ ] Write `common.py` with root constants, `write_json()`, `write_text()`, `sha256_file()`, and status codes.
- [ ] Write `parsers.py` with `read_jsonc()` that strips trailing commas before `json.loads()`.

```python
def read_jsonc(path: Path):
    raw = path.read_text(encoding="utf-8-sig")
    return json.loads(strip_trailing_commas(raw))
```

- [ ] Smoke-check parsing:

```powershell
@'
from pathlib import Path
from parsers import read_jsonc
print(sorted(read_jsonc(Path(r"C:\Users\huibozi\.openclaw\openclaw.json")).keys()))
'@ | python -
```

Expected: parse succeeds and prints keys including `agents`, `bindings`, `commands`, `channels`, `gateway`, `plugins`.

- [ ] Write and run `bootstrap.py` to create the full skeleton, including empty `rules/` and `mcp/`:

```python
DECL_DIRS = ["agents","skills","commands","bindings","channels","gateway","plugins","cron","rules","mcp"]
STATE_DIRS = ["sessions","cron-runs","indexes/memory","indexes/credentials","indexes/devices"]
GENERATED_DIRS = ["registries","reports","snapshots"]
```

## Task 3: Import Agents

**Files:**
- Create `scripts\decl_state\import_agents_openclaw.py`
- Create `decl\agents\_defaults.json`
- Create `decl\agents\<id>\agent.json`

- [ ] Merge `openclaw.json:agents.defaults` and `agents.list[]` into canonical agents.
- [ ] Preserve runtime-specific file references under `_adapter_notes`.

```python
{"id": agent_id, "model": record.get("model"), "tools": tools.get("allow", []), "disallowed_tools": tools.get("deny", []), "_adapter_notes": {"agent_dir": str(agent_dir)}}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\agents
```

Expected: `_defaults.json` plus `main`, `research`, `daily`, `freya`, `profit`, `personal`.

## Task 4: Import Commands, Bindings, Channels, Gateway, Plugins

**Files:**
- Create `scripts\decl_state\import_decl_openclaw.py`
- Create `decl\commands\_settings.json`
- Create `decl\bindings\<id>\binding.json`
- Create `decl\channels\<id>\channel.json`
- Create `decl\gateway\gateway.json`
- Create `decl\plugins\<id>\plugin.json`

- [ ] Commands stay singleton settings, not fake command directories.
- [ ] Bindings preserve `match` verbatim.
- [ ] Channels keep nested provider/account semantics in `_adapter_config`.

```python
def binding_id(agent_id: str, index: int) -> str:
    return f"binding-{agent_id}-{index:03d}"
```

```python
{"id": channel_id, "kind": channel_id, "auth_ref": auth_ref, "enabled": item.get("enabled", True), "_adapter_config": item}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_decl_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\commands\_settings.json
Get-ChildItem C:\Users\huibozi\.openclaw\decl\bindings
Get-ChildItem C:\Users\huibozi\.openclaw\decl\channels
Get-ChildItem C:\Users\huibozi\.openclaw\decl\plugins
```

Expected: at least `telegram`, `feishu`, `minimax` plugin entries and binding ids like `binding-daily-001`.

## Task 5: Import Package Skills

**Files:**
- Create `scripts\decl_state\import_skills_openclaw.py`
- Create `decl\skills\<id>\skill.json`
- Create `decl\skills\<id>\skill.md`

- [ ] Convert each package-style skill with `package.json + SKILL.md` into canonical `skill.json + skill.md`.

```python
{"id": skill_id, "name": package_json.get("name", skill_id), "description": package_json.get("description", f"Imported OpenClaw skill package {skill_id}"), "_adapter_notes": {"package_json": str(skill_dir / "package.json")}}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_skills_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\skills
```

Expected: `opennews` and `opentwitter` are present; original `skills\*` packages remain untouched.

## Task 6: Import Cron And Index Cron Runs

**Files:**
- Create `scripts\decl_state\import_cron_openclaw.py`
- Create `decl\cron\jobs.json`
- Create `state\cron-runs\index.json`

- [ ] Import `cron/jobs.json` into canonical declaration form and build a metadata-only run index.

```python
{"id": "cron-jobs", "source": str(CRON_ROOT / "jobs.json"), "jobs": jobs.get("jobs", [])}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_cron_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\decl\cron\jobs.json -TotalCount 60
Get-Content C:\Users\huibozi\.openclaw\state\cron-runs\index.json -TotalCount 60
```

Expected: declaration contains job list; run index contains metadata only.

## Task 7: Build Redacted Sensitive Indexes

**Files:**
- Create `scripts\decl_state\build_sensitive_indexes_openclaw.py`
- Create `state\indexes\credentials\index.json`
- Create `state\indexes\devices\index.json`
- Create `state\indexes\memory\index.json`
- Create `generated\reports\openclaw-sensitive-index-summary.json`

- [ ] Index `credentials/` by file name, relative path, size, modified time, exists flag.
- [ ] Index `devices/` with redacted device identity fields only.
- [ ] Index `memory/*.sqlite` by file name, size, modified time, and table list only.

```python
{"name": path.name, "relative_path": str(path.relative_to(root)), "size": stat.st_size, "exists": True}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\build_sensitive_indexes_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\state\indexes\credentials\index.json -TotalCount 40
Get-Content C:\Users\huibozi\.openclaw\state\indexes\memory\index.json -TotalCount 60
```

Expected: no secret values appear in any canonical index.

## Task 8: Build Unified Session Manifest

**Files:**
- Create `scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Create `state\sessions\index.json`

- [ ] Scan `agents/*/sessions/*.jsonl` and emit metadata only.

```python
{"session_id": path.stem, "agent_id": agent_dir.name, "source_path": str(path), "started_at": None, "updated_at": utc_now()}
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\state\sessions\index.json -TotalCount 60
```

Expected: session manifest exists; transcript bodies were not copied.

## Task 9: Registries, Validation, Snapshot, Backfill

**Files:**
- Create `scripts\decl_state\build_registries_openclaw.py`
- Create `scripts\decl_state\validate_decl_openclaw.py`
- Create `scripts\decl_state\validate_state_openclaw.py`
- Create `scripts\decl_state\build_snapshot_openclaw.py`
- Create `scripts\decl_state\backfill_decl_generation_openclaw.py`
- Create `scripts\decl_state\validate_full_openclaw.py`
- Create ten registry files under `generated\registries\`

- [ ] Build registries for the ten canonical groups. `commands` reads `_settings.json`; `gateway` is a singleton `gateway.json`; empty `rules` and `mcp` must still emit empty registries.

```python
GROUPS = {"agents": "agent.json", "skills": "skill.json", "commands": "_settings.json", "bindings": "binding.json", "channels": "channel.json", "gateway": "gateway.json", "plugins": "plugin.json", "cron": "jobs.json", "rules": "policy.json", "mcp": "connector.json"}
```

- [ ] `validate_decl_openclaw.py` must fail if any registry file is missing after a registry build.
- [ ] `validate_state_openclaw.py` must treat stale historical gaps as warnings, not errors.
- [ ] `validate_full_openclaw.py` must run the locked sequence:

```python
STEPS = [("validate declarations", "validate_decl_openclaw.py"), ("rebuild registries", "build_registries_openclaw.py"), ("rebuild state indexes", "rebuild_state_indexes_openclaw.py"), ("validate state", "validate_state_openclaw.py"), ("build snapshot", "build_snapshot_openclaw.py"), ("backfill decl_generation", "backfill_decl_generation_openclaw.py")]
```

- [ ] Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\generated\registries
Get-Content C:\Users\huibozi\.openclaw\generated\reports\openclaw-full-validation.json -TotalCount 120
```

Expected:
- exit code is `0` or `2`, never `1`
- ten registry files exist
- `decl/agents/` has the six known agents
- `commands`, `bindings`, `channels`, `gateway`, `plugins`, and `cron` all exist in canonical form
- `credentials/`, `devices/`, `memory/*.sqlite`, and `agents/*/sessions/*.jsonl` remain untouched

## Task 10: Operator Guide

**Files:**
- Create `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

- [ ] Write the guide with three sections: canonical roots, runtime surfaces left in place, and safety rules.
- [ ] Include these validation commands verbatim:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

- [ ] Run the commands from the guide and verify they match reality.

## Acceptance Checklist

- `validate_full_openclaw.py` exits `0` or `2`, never `1`
- `decl/agents/` contains declarations for the six live agents
- `decl/commands/_settings.json` exists
- `decl/bindings/`, `decl/channels/`, `decl/gateway/`, `decl/plugins/`, and `decl/cron/` exist and contain imported declarations
- `decl/rules/` and `decl/mcp/` exist as canonical empty roots
- `state/sessions/index.json` and `state/cron-runs/index.json` are metadata-only
- `state/indexes/credentials/index.json`, `state/indexes/devices/index.json`, and `state/indexes/memory/index.json` exist and are redacted
- `generated/registries/` contains ten registry files
- no live runtime files were rewritten under `credentials/`, `devices/`, `memory/`, `skills/`, or `agents/*/sessions/`

## Self-Review

- Coverage: agents, commands, bindings, channels, gateway, plugins, skills, cron, sensitive indexes, state indexes, registries, validation, snapshots, and operator docs all have dedicated tasks.
- Placeholder scan: no unresolved placeholders or deferred implementation notes should remain.
- Type consistency: `binding.json` keeps `match`; `channel.json` keeps `_adapter_config`; commands stay singleton `_settings.json`.
