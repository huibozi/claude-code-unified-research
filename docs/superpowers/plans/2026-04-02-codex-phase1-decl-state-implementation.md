# Codex Phase 1 Decl-State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add canonical `decl/`, `state/`, and `generated/` layers to `C:\Users\huibozi\.codex` without changing the live Codex runtime behavior that still depends on `config.toml`, `skills/`, `rules/`, `sessions/`, and the native SQLite files.

**Architecture:** Keep Codex native runtime surfaces in place and treat them as adapter inputs, not migration targets. Add a JSON declaration layer under `decl/`, additive normalized state indexes under `state/`, and disposable registries, reports, and snapshots under `generated/`. Validation follows the locked order `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`, with exit codes `0 = pass`, `1 = error`, and `2 = warn`.

**Tech Stack:** PowerShell 7+, Python 3.11, `tomllib`, `sqlite3`, Markdown, JSON, JSON Schema Draft 2020-12, `jsonschema`, live Codex runtime files under `C:\Users\huibozi\.codex`

---

## Current Baseline To Preserve

- `C:\Users\huibozi\.codex` is not a git repository, so rollback checkpoints must be filesystem backups under `C:\Users\huibozi\.codex\backups\decl-state\`.
- Native runtime config remains at `C:\Users\huibozi\.codex\config.toml` with the current fields:
  - `model = "gpt-5.4"`
  - `model_reasoning_effort = "xhigh"`
  - `[features].multi_agent = true`
  - `[windows].sandbox = "elevated"`
- Native rule surface remains `C:\Users\huibozi\.codex\rules\default.rules`.
- Native skill corpus remains `C:\Users\huibozi\.codex\skills\.system\openai-docs\SKILL.md`, `C:\Users\huibozi\.codex\skills\.system\skill-creator\SKILL.md`, and `C:\Users\huibozi\.codex\skills\.system\skill-installer\SKILL.md`.
- Native session state remains in:
  - `C:\Users\huibozi\.codex\session_index.jsonl`
  - `C:\Users\huibozi\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`
- Native runtime databases remain untouched:
  - `C:\Users\huibozi\.codex\state_5.sqlite`
  - `C:\Users\huibozi\.codex\logs_1.sqlite`
- `C:\Users\huibozi\.codex\superpowers\` remains a separate installed workflow tree and is not migrated into `decl/` or `state/`.
- `C:\Users\huibozi\.codex\memories\` remains untouched in Phase 1.
- Codex Phase 1 is additive only. It does not rewrite `config.toml`, `rules/default.rules`, `skills/`, `sessions/`, SQLite files, or `superpowers/`.

## Implementation Layout

- Canonical declaration root: `C:\Users\huibozi\.codex\decl\`
- Normalized state root: `C:\Users\huibozi\.codex\state\`
- Derived outputs root: `C:\Users\huibozi\.codex\generated\`
- Migration and validation scripts: `C:\Users\huibozi\.codex\scripts\decl_state\`
- Operator note for future humans: `C:\Users\huibozi\.codex\CODEX-DECL-STATE.md`

Phase 1 canonical roots:

```text
C:\Users\huibozi\.codex\
  decl\
    agents\
    skills\
    rules\
    commands\
    mcp\
  state\
    sessions\
    indexes\
      sqlite\
  generated\
    registries\
    reports\
    snapshots\
```

Important semantics:

- `decl/` is human-edited and uses JSON declaration payloads.
- `state/` stores normalized indexes and metadata views only.
- `state/indexes/sqlite/` stores metadata about native SQLite files, never the live `.sqlite` files themselves.
- `generated/` is disposable and must be recreated by scripts.
- Top-level native Codex files are not mirrors in Phase 1. They remain live runtime inputs.

### Task 1: Bootstrap The Canonical Roots And Additive Rollback Inventory

**Files:**
- Create: `C:\Users\huibozi\.codex\decl\README.md`
- Create: `C:\Users\huibozi\.codex\state\README.md`
- Create: `C:\Users\huibozi\.codex\state\indexes\sqlite\README.md`
- Create: `C:\Users\huibozi\.codex\generated\README.md`
- Create: `C:\Users\huibozi\.codex\generated\.gitignore`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\common.py`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\parsers.py`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\bootstrap.py`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-bootstrap-inventory.json`
- Create: `C:\Users\huibozi\.codex\backups\decl-state\bootstrap-<timestamp>\`

- [ ] **Step 1: Create the shared helper module used by every Codex migration script**

Write `C:\Users\huibozi\.codex\scripts\decl_state\common.py` with these helpers:

```python
from __future__ import annotations

import hashlib
import json
import shutil
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CODEX_ROOT = Path(r"C:\Users\huibozi\.codex")
DECL_ROOT = CODEX_ROOT / "decl"
STATE_ROOT = CODEX_ROOT / "state"
GENERATED_ROOT = CODEX_ROOT / "generated"
SCRIPTS_ROOT = CODEX_ROOT / "scripts" / "decl_state"
BACKUP_ROOT = CODEX_ROOT / "backups" / "decl-state"
REPORTS_ROOT = GENERATED_ROOT / "reports"
REGISTRIES_ROOT = GENERATED_ROOT / "registries"
SNAPSHOTS_ROOT = GENERATED_ROOT / "snapshots"
CONFIG_TOML_PATH = CODEX_ROOT / "config.toml"
SESSION_INDEX_PATH = CODEX_ROOT / "session_index.jsonl"
RULES_PATH = CODEX_ROOT / "rules" / "default.rules"
STATE_DB_PATH = CODEX_ROOT / "state_5.sqlite"
LOG_DB_PATH = CODEX_ROOT / "logs_1.sqlite"

STATUS_PASS = 0
STATUS_ERROR = 1
STATUS_WARN = 2


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        ensure_dir(dst.parent)
        shutil.copy2(src, dst)


def prune_snapshots(max_keep: int = 5) -> None:
    snapshots = sorted(SNAPSHOTS_ROOT.glob("decl-*.json"))
    for old_path in snapshots[:-max_keep]:
        old_path.unlink()
```

- [ ] **Step 2: Create the frontmatter parser for the managed skill imports**

Write `C:\Users\huibozi\.codex\scripts\decl_state\parsers.py`:

```python
from __future__ import annotations

import re
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def read_frontmatter_markdown(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw
    metadata = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).lstrip()
    return metadata, body
```
- [ ] **Step 3: Create the bootstrap script that lays down the additive layout and captures a rollback checkpoint**

Write `C:\Users\huibozi\.codex\scripts\decl_state\bootstrap.py`:

```python
from __future__ import annotations

from common import (
    BACKUP_ROOT,
    CODEX_ROOT,
    CONFIG_TOML_PATH,
    GENERATED_ROOT,
    LOG_DB_PATH,
    REPORTS_ROOT,
    RULES_PATH,
    SESSION_INDEX_PATH,
    STATE_DB_PATH,
    STATE_ROOT,
    DECL_ROOT,
    copy_if_exists,
    ensure_dir,
    sha256_file,
    timestamp_slug,
    utc_now,
    write_json,
)

DECL_DIRS = ["agents", "skills", "rules", "commands", "mcp"]
STATE_DIRS = ["sessions", "indexes", "indexes/sqlite"]
GENERATED_DIRS = ["registries", "reports", "snapshots"]
SMALL_BACKUPS = [
    "config.toml",
    "auth.json",
    "models_cache.json",
    "session_index.jsonl",
    "rules/default.rules",
]


def main() -> None:
    stamp = timestamp_slug()
    backup_dir = ensure_dir(BACKUP_ROOT / f"bootstrap-{stamp}")

    for root in [DECL_ROOT, STATE_ROOT, GENERATED_ROOT]:
        ensure_dir(root)
    for name in DECL_DIRS:
        ensure_dir(DECL_ROOT / name)
    for name in STATE_DIRS:
        ensure_dir(STATE_ROOT / name)
    for name in GENERATED_DIRS:
        ensure_dir(GENERATED_ROOT / name)

    for rel_path in SMALL_BACKUPS:
        src = CODEX_ROOT / rel_path
        dst = backup_dir / "legacy" / rel_path
        copy_if_exists(src, dst)

    session_files = sorted((CODEX_ROOT / "sessions").rglob("rollout-*.jsonl"))
    db_files = [STATE_DB_PATH, LOG_DB_PATH]

    write_json(
        REPORTS_ROOT / "codex-bootstrap-inventory.json",
        {
            "generated_at": utc_now(),
            "backup_dir": str(backup_dir),
            "decl_dirs": DECL_DIRS,
            "state_dirs": STATE_DIRS,
            "generated_dirs": GENERATED_DIRS,
            "small_backups": SMALL_BACKUPS,
            "native_sessions": {
                "count": len(session_files),
                "sample": [str(path) for path in session_files[:5]],
            },
            "native_sqlite": [
                {
                    "path": str(path),
                    "exists": path.exists(),
                    "size_bytes": path.stat().st_size if path.exists() else 0,
                    "sha256": sha256_file(path) if path.exists() else None,
                }
                for path in db_files
            ],
            "runtime_config": {
                "config_toml": str(CONFIG_TOML_PATH),
                "session_index": str(SESSION_INDEX_PATH),
                "rules_file": str(RULES_PATH),
            },
        },
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write the root READMEs and generated ignore file**

Create these exact contents:

```markdown
# Declaration Layer

Edit files in this tree directly. This is the only authoritative source for managed agents, managed skills, managed rules, optional command declarations, and optional MCP connector declarations.

Do not hand-edit `..\generated\`.
Do not assume top-level native Codex files are mirrors in Phase 1.
```

```markdown
# State Layer

This tree stores normalized indexes and metadata views derived from the live Codex runtime.

It does not own the native session archives or the live SQLite files.
```

```markdown
# SQLite Metadata Index

This directory stores JSON metadata views about native SQLite files.

Do not move or copy live `.sqlite` files into this tree.
```

```markdown
# Generated Layer

This tree contains derived outputs only:
- `registries/`
- `reports/`
- `snapshots/`

Every full validation run rewrites `registries/` and `reports/`. Snapshot retention keeps the newest five files.
```

```gitignore
*
!.gitignore
```

- [ ] **Step 5: Run the bootstrap script and verify the additive layout exists**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\bootstrap.py
Get-ChildItem C:\Users\huibozi\.codex\decl
Get-ChildItem C:\Users\huibozi\.codex\state
Get-ChildItem C:\Users\huibozi\.codex\generated
Get-Content C:\Users\huibozi\.codex\generated\reports\codex-bootstrap-inventory.json
```

Expected: all canonical roots exist, `state\indexes\sqlite\README.md` explains that only metadata belongs there, and `codex-bootstrap-inventory.json` records backup paths plus native session and SQLite inventory.

### Task 2: Add Declaration Schemas And The Codex Declaration Validator

**Files:**
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\schemas\agent.schema.json`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\schemas\skill.schema.json`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\schemas\command.schema.json`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\schemas\policy.schema.json`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\schemas\connector.schema.json`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-decl-health.json`

- [ ] **Step 1: Write the five declaration schemas with the locked Phase 1 field names**

Use this pattern for every schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": true,
  "required": ["id", "description"],
  "properties": {
    "id": { "type": "string", "minLength": 1 },
    "description": { "type": "string" }
  }
}
```

Use these required fields per object:

```text
agent: id, description, model, compute_profile, tools, skills, permission_mode, memory_scope, isolation, max_turns, required_mcp_servers
skill: id, description, when_to_use, allowed_tools, argument_hint, model_override, path_conditions, hooks
command: id, description, aliases, kind, input_contract, enabled_when, handler_type
policy: id, scope, priority, allow_rules, deny_rules, ask_rules, danger_filters, audit_requirements
connector: id, kind, transport, command, args, env_policy, capabilities, auth_mode, healthcheck
```

Hard-code these enums:

```text
compute_profile: low | balanced | high
isolation: none | sandboxed | container
handler_type: builtin | skill | pipeline | external
connector.kind: stdio | sse | http
auth_mode: none | token | oauth
```

- [ ] **Step 2: Write the declaration validator for the new canonical JSON declarations**

Write `C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py`:

```python
from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from common import DECL_ROOT, REPORTS_ROOT, STATUS_ERROR, STATUS_PASS, read_json, utc_now, write_json

DECL_MAP = {
    "agents": "agent.schema.json",
    "skills": "skill.schema.json",
    "commands": "command.schema.json",
    "rules": "policy.schema.json",
    "mcp": "connector.schema.json",
}

FILENAME_MAP = {
    "agents": "agent.json",
    "skills": "skill.json",
    "commands": "command.json",
    "rules": "policy.json",
    "mcp": "connector.json",
}


def iter_decl_files(group: str):
    group_root = DECL_ROOT / group
    filename = FILENAME_MAP[group]
    if not group_root.exists():
        return
    for child in sorted(group_root.iterdir()):
        if child.is_dir():
            payload_path = child / filename
            if payload_path.exists():
                yield payload_path


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    ids_seen: dict[str, set[str]] = {group: set() for group in DECL_MAP}

    for group, schema_name in DECL_MAP.items():
        schema_path = Path(__file__).parent / "schemas" / schema_name
        schema = read_json(schema_path)
        validator = Draft202012Validator(schema)
        for json_path in iter_decl_files(group) or []:
            payload = read_json(json_path)
            object_id = payload["id"]
            if object_id in ids_seen[group]:
                errors.append(f"duplicate id {group}:{object_id}")
            ids_seen[group].add(object_id)
            for issue in validator.iter_errors(payload):
                errors.append(f"{json_path}: {issue.message}")

    status = "pass" if not errors else "fail"
    write_json(
        REPORTS_ROOT / "codex-decl-health.json",
        {
            "generated_at": utc_now(),
            "status": status,
            "errors": errors,
            "warnings": warnings,
        },
    )

    raise SystemExit(STATUS_PASS if not errors else STATUS_ERROR)


if __name__ == "__main__":
    main()
```
- [ ] **Step 3: Verify the schemas and declaration validator compile before importing anything**

Run:

```powershell
python -c "import jsonschema, yaml; print('deps-ok')"
python -m py_compile C:\Users\huibozi\.codex\scripts\decl_state\common.py C:\Users\huibozi\.codex\scripts\decl_state\parsers.py C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py
python C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py
Get-Content C:\Users\huibozi\.codex\generated\reports\codex-decl-health.json
```

Expected: `deps-ok`, no Python compile errors, and the declaration health report exists with status `pass` even before managed declarations are imported.

### Task 3: Seed The Canonical Default Agent From `config.toml`

**Files:**
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py`
- Create: `C:\Users\huibozi\.codex\decl\agents\codex-default\agent.json`
- Create: `C:\Users\huibozi\.codex\decl\agents\codex-default\prompt.md`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-agent-import.json`

- [ ] **Step 1: Write the declaration importer with a dedicated agent import path**

Write `C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py` with these top-level functions:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from common import CONFIG_TOML_PATH, DECL_ROOT, REPORTS_ROOT, read_toml, utc_now, write_json, write_text, ensure_dir
from parsers import read_frontmatter_markdown

SYSTEM_SKILLS = {
    "openai-docs": Path(r"C:\Users\huibozi\.codex\skills\.system\openai-docs\SKILL.md"),
    "skill-creator": Path(r"C:\Users\huibozi\.codex\skills\.system\skill-creator\SKILL.md"),
    "skill-installer": Path(r"C:\Users\huibozi\.codex\skills\.system\skill-installer\SKILL.md"),
}


def compute_profile_from_reasoning(reasoning_effort: str | None) -> str:
    if reasoning_effort in {"high", "xhigh"}:
        return "high"
    if reasoning_effort == "low":
        return "low"
    return "balanced"


def import_agent() -> None:
    config = read_toml(CONFIG_TOML_PATH)
    target = ensure_dir(DECL_ROOT / "agents" / "codex-default")
    payload = {
        "id": "codex-default",
        "description": "Default Codex runtime agent derived from config.toml.",
        "model": config.get("model", "inherit"),
        "compute_profile": compute_profile_from_reasoning(config.get("model_reasoning_effort")),
        "tools": [],
        "skills": [],
        "permission_mode": "inherit",
        "memory_scope": "session",
        "isolation": "none",
        "max_turns": 0,
        "required_mcp_servers": [],
        "_adapter_notes": {
            "runtime_reasoning_effort": config.get("model_reasoning_effort"),
            "runtime_sandbox": config.get("windows", {}).get("sandbox"),
            "multi_agent": config.get("features", {}).get("multi_agent", False),
        },
    }
    write_json(target / "agent.json", payload)
    write_text(
        target / "prompt.md",
        "# Codex Default Agent\n\nThis directory is the canonical JSON projection of the live Codex runtime defaults.\n\nUpdate `config.toml`, then rerun `import_decl_codex.py --agent` to refresh this managed declaration.\n",
    )
    write_json(
        REPORTS_ROOT / "codex-agent-import.json",
        {
            "generated_at": utc_now(),
            "agent_path": str(target / "agent.json"),
            "model": payload["model"],
            "compute_profile": payload["compute_profile"],
        },
    )
```

Also add this exact CLI entrypoint at the bottom of the file:

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", action="store_true")
    parser.add_argument("--skills", action="store_true")
    parser.add_argument("--rules", action="store_true")
    args = parser.parse_args()

    if args.agent:
        import_agent()
    if args.skills:
        import_skills()
    if args.rules:
        import_rules()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make sure the expected canonical payload matches the current live Codex runtime**

The importer should produce this exact shape in `C:\Users\huibozi\.codex\decl\agents\codex-default\agent.json`:

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
    "runtime_reasoning_effort": "xhigh",
    "runtime_sandbox": "elevated",
    "multi_agent": true
  }
}
```

This keeps the shared schema neutral while still recording the live Codex sandbox behavior.

- [ ] **Step 3: Run the agent import and immediately validate the declaration layer**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py --agent
python C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py
Get-Content C:\Users\huibozi\.codex\decl\agents\codex-default\agent.json
Get-Content C:\Users\huibozi\.codex\decl\agents\codex-default\prompt.md
```

Expected: `codex-default\agent.json` matches the locked payload, `prompt.md` explains the refresh workflow, and declaration health still reports `pass`.

### Task 4: Import The First Managed Skill Cohort And Wrap The Native Rule Surface

**Files:**
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\inventory_skills_codex.py`
- Modify: `C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py`
- Create: `C:\Users\huibozi\.codex\decl\skills\README.md`
- Create: `C:\Users\huibozi\.codex\decl\skills\openai-docs\skill.json`
- Create: `C:\Users\huibozi\.codex\decl\skills\openai-docs\skill.md`
- Create: `C:\Users\huibozi\.codex\decl\skills\skill-creator\skill.json`
- Create: `C:\Users\huibozi\.codex\decl\skills\skill-creator\skill.md`
- Create: `C:\Users\huibozi\.codex\decl\skills\skill-installer\skill.json`
- Create: `C:\Users\huibozi\.codex\decl\skills\skill-installer\skill.md`
- Create: `C:\Users\huibozi\.codex\decl\rules\default\policy.json`
- Create: `C:\Users\huibozi\.codex\decl\rules\default\policy.md`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-skill-inventory.json`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-skill-import.json`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-rule-import.json`
- [ ] **Step 1: Inventory the current Codex skill corpus before importing the managed subset**

Write `C:\Users\huibozi\.codex\scripts\decl_state\inventory_skills_codex.py`:

```python
from __future__ import annotations

from pathlib import Path

from common import CODEX_ROOT, REPORTS_ROOT, utc_now, write_json

SKILLS_ROOT = CODEX_ROOT / "skills" / ".system"


def main() -> None:
    entries = []
    if SKILLS_ROOT.exists():
        for child in sorted(SKILLS_ROOT.iterdir()):
            if child.is_dir():
                entries.append(
                    {
                        "id": child.name,
                        "source_dir": str(child),
                        "skill_md_exists": (child / "SKILL.md").exists(),
                        "has_agents_dir": (child / "agents").exists(),
                        "has_assets_dir": (child / "assets").exists(),
                        "has_scripts_dir": (child / "scripts").exists(),
                    }
                )

    write_json(
        REPORTS_ROOT / "codex-skill-inventory.json",
        {
            "generated_at": utc_now(),
            "entry_count": len(entries),
            "entries": entries,
        },
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Extend the importer with managed skill and native rule import functions**

Append these exact functions to `C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py`:

```python
def import_skills() -> None:
    imported = []
    for skill_id, skill_path in SYSTEM_SKILLS.items():
        metadata, body = read_frontmatter_markdown(skill_path)
        target = ensure_dir(DECL_ROOT / "skills" / skill_id)
        payload = {
            "id": skill_id,
            "name": metadata.get("name", skill_id),
            "description": metadata.get("description", ""),
            "when_to_use": [metadata.get("description", "")] if metadata.get("description") else [],
            "allowed_tools": [],
            "argument_hint": f"Use {skill_id} only when the request clearly matches its description.",
            "model_override": None,
            "path_conditions": [],
            "hooks": [],
        }
        write_json(target / "skill.json", payload)
        write_text(target / "skill.md", body)
        imported.append({"id": skill_id, "source": str(skill_path)})

    write_json(
        REPORTS_ROOT / "codex-skill-import.json",
        {
            "generated_at": utc_now(),
            "imported": imported,
        },
    )


def import_rules() -> None:
    target = ensure_dir(DECL_ROOT / "rules" / "default")
    rule_text = Path(r"C:\Users\huibozi\.codex\rules\default.rules").read_text(encoding="utf-8")
    write_json(
        target / "policy.json",
        {
            "id": "default",
            "description": "Canonical wrapper around the native Codex default rules file.",
            "scope": "global",
            "priority": 50,
            "allow_rules": [],
            "deny_rules": [],
            "ask_rules": [],
            "danger_filters": [],
            "audit_requirements": [],
            "_adapter_notes": {
                "legacy_rules_path": r"C:\Users\huibozi\.codex\rules\default.rules"
            },
        },
    )
    write_text(
        target / "policy.md",
        "# Native Codex Default Rules\n\nThe canonical policy payload for Phase 1 stays structured in `policy.json`. The live runtime rules remain in `C:\\Users\\huibozi\\.codex\\rules\\default.rules`.\n\n```text\n"
        + rule_text
        + "\n```\n",
    )
    write_json(
        REPORTS_ROOT / "codex-rule-import.json",
        {
            "generated_at": utc_now(),
            "policy_path": str(target / "policy.json"),
            "legacy_path": r"C:\Users\huibozi\.codex\rules\default.rules",
        },
    )
```

Also create `C:\Users\huibozi\.codex\decl\skills\README.md` with this text:

```markdown
# Managed Codex Skills

This tree contains the managed JSON-plus-Markdown subset of the live Codex skill corpus.

The native runtime still loads `C:\Users\huibozi\.codex\skills\`. Phase 1 imports only the approved managed subset.
```

- [ ] **Step 3: Run the skill inventory and import the approved Phase 1 managed subset**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\inventory_skills_codex.py
python C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py --skills --rules
python C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py
```

Expected: three managed skill directories and one canonical default rule directory exist under `decl\`, and declaration validation still reports `pass`.

- [ ] **Step 4: Verify one imported skill and the wrapped rule surface match the locked mapping rules**

Run:

```powershell
Get-Content C:\Users\huibozi\.codex\decl\skills\openai-docs\skill.json
Get-Content -TotalCount 20 C:\Users\huibozi\.codex\decl\skills\openai-docs\skill.md
Get-Content C:\Users\huibozi\.codex\decl\rules\default\policy.json
Get-Content -TotalCount 20 C:\Users\huibozi\.codex\decl\rules\default\policy.md
```

Expected: `skill.json` uses `id` as the unique key, `skill.md` contains the body without frontmatter duplication, `policy.json` includes `priority`, and `policy.md` preserves the native rules as documentation rather than replacing the live runtime file.

### Task 5: Build Registries, Snapshots, And Post-Snapshot Backfill

**Files:**
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\build_registries_codex.py`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\build_snapshot_codex.py`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\backfill_decl_generation_codex.py`
- Create: `C:\Users\huibozi\.codex\generated\registries\agents.registry.json`
- Create: `C:\Users\huibozi\.codex\generated\registries\skills.registry.json`
- Create: `C:\Users\huibozi\.codex\generated\registries\rules.registry.json`
- Create: `C:\Users\huibozi\.codex\generated\registries\commands.registry.json`
- Create: `C:\Users\huibozi\.codex\generated\registries\mcp.registry.json`
- Create: `C:\Users\huibozi\.codex\generated\snapshots\decl-<timestamp>.json`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-registry-summary.json`
- [ ] **Step 1: Write the registry builder with the locked registry shape**

Write `C:\Users\huibozi\.codex\scripts\decl_state\build_registries_codex.py`:

```python
from __future__ import annotations

from common import DECL_ROOT, REGISTRIES_ROOT, REPORTS_ROOT, sha256_file, utc_now, write_json

GROUPS = {
    "agents": "agent.json",
    "skills": "skill.json",
    "rules": "policy.json",
    "commands": "command.json",
    "mcp": "connector.json",
}


def build_group(group: str, filename: str) -> list[dict]:
    entries = []
    group_root = DECL_ROOT / group
    if not group_root.exists():
        return entries
    for child in sorted(group_root.iterdir()):
        if child.is_dir():
            payload_path = child / filename
            if payload_path.exists():
                entries.append(
                    {
                        "id": child.name,
                        "source_path": str(payload_path),
                        "hash": sha256_file(payload_path),
                        "last_updated_at": utc_now(),
                        "decl_generation": "pending",
                    }
                )
    write_json(REGISTRIES_ROOT / f"{group}.registry.json", {"entries": entries})
    return entries


def main() -> None:
    summary = {}
    for group, filename in GROUPS.items():
        summary[group] = {"count": len(build_group(group, filename))}
    write_json(
        REPORTS_ROOT / "codex-registry-summary.json",
        {
            "generated_at": utc_now(),
            "summary": summary,
        },
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the snapshot builder without backfilling registries yet**

Write `C:\Users\huibozi\.codex\scripts\decl_state\build_snapshot_codex.py`:

```python
from __future__ import annotations

import hashlib
import json

from common import REGISTRIES_ROOT, SNAPSHOTS_ROOT, prune_snapshots, read_json, timestamp_slug, utc_now, write_json


def main() -> None:
    registry_payloads = {}
    for path in sorted(REGISTRIES_ROOT.glob("*.registry.json")):
        registry_payloads[path.name] = read_json(path)

    combined = json.dumps(registry_payloads, sort_keys=True, ensure_ascii=False)
    decl_generation = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]

    write_json(
        SNAPSHOTS_ROOT / f"decl-{timestamp_slug()}.json",
        {
            "generated_at": utc_now(),
            "decl_generation": decl_generation,
            "registries": registry_payloads,
        },
    )
    prune_snapshots(max_keep=5)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write the explicit post-snapshot backfill script**

Write `C:\Users\huibozi\.codex\scripts\decl_state\backfill_decl_generation_codex.py`:

```python
from __future__ import annotations

from common import REGISTRIES_ROOT, SNAPSHOTS_ROOT, STATE_ROOT, read_json, write_json


def latest_snapshot() -> tuple[str, str]:
    snapshots = sorted(SNAPSHOTS_ROOT.glob("decl-*.json"))
    if not snapshots:
        raise SystemExit("no snapshots found")
    snapshot_path = snapshots[-1]
    payload = read_json(snapshot_path)
    return payload["decl_generation"], str(snapshot_path)


def backfill_registries(decl_generation: str) -> None:
    for path in sorted(REGISTRIES_ROOT.glob("*.registry.json")):
        payload = read_json(path)
        for entry in payload.get("entries", []):
            entry["decl_generation"] = decl_generation
        write_json(path, payload)


def backfill_session_index(decl_generation: str, snapshot_ref: str) -> None:
    index_path = STATE_ROOT / "sessions" / "index.json"
    if not index_path.exists():
        return
    payload = read_json(index_path)
    for entry in payload.get("entries", []):
        if entry.get("agent_id") == "codex-default":
            entry["decl_generation"] = decl_generation
            entry["snapshot_ref"] = snapshot_ref
    write_json(index_path, payload)


def main() -> None:
    decl_generation, snapshot_ref = latest_snapshot()
    backfill_registries(decl_generation)
    backfill_session_index(decl_generation, snapshot_ref)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run registry generation, snapshot generation, and backfill in the locked order**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\build_registries_codex.py
python C:\Users\huibozi\.codex\scripts\decl_state\build_snapshot_codex.py
python C:\Users\huibozi\.codex\scripts\decl_state\backfill_decl_generation_codex.py
Get-ChildItem C:\Users\huibozi\.codex\generated\registries
Get-ChildItem C:\Users\huibozi\.codex\generated\snapshots
```

Expected: all five registries exist, the newest snapshot has a non-empty `decl_generation`, and every registry entry now contains the same non-`pending` `decl_generation` value.

### Task 6: Derive Normalized Session And SQLite Indexes, Then Validate State

**Files:**
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\rebuild_state_indexes_codex.py`
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\validate_state_codex.py`
- Create: `C:\Users\huibozi\.codex\state\sessions\index.json`
- Create: `C:\Users\huibozi\.codex\state\indexes\sqlite\index.json`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-session-inventory.json`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-state-health.json`

- [ ] **Step 1: Write the state index builder that derives additive views from the live session and SQLite surfaces**

Write `C:\Users\huibozi\.codex\scripts\decl_state\rebuild_state_indexes_codex.py`:

```python
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from common import CODEX_ROOT, LOG_DB_PATH, REPORTS_ROOT, SESSION_INDEX_PATH, STATE_DB_PATH, STATE_ROOT, utc_now, write_json

SESSIONS_ROOT = CODEX_ROOT / "sessions"


def load_session_index() -> dict[str, dict]:
    entries = {}
    if not SESSION_INDEX_PATH.exists():
        return entries
    for raw_line in SESSION_INDEX_PATH.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        payload = json.loads(raw_line)
        entries[payload["id"]] = payload
    return entries


def scan_rollouts() -> dict[str, dict]:
    entries = {}
    for path in sorted(SESSIONS_ROOT.rglob("rollout-*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                event = json.loads(raw_line)
                if event.get("type") != "session_meta":
                    continue
                payload = event.get("payload") or {}
                session_id = payload.get("id")
                if not session_id:
                    break
                subagent = ((payload.get("source") or {}).get("subagent") or {}).get("thread_spawn")
                entry = {
                    "session_id": session_id,
                    "source_path": str(path),
                    "cwd": payload.get("cwd"),
                    "originator": payload.get("originator"),
                    "cli_version": payload.get("cli_version"),
                    "model_provider": payload.get("model_provider"),
                    "agent_id": None if subagent else "codex-default",
                    "skill_ids": [],
                    "connector_ids": [],
                    "decl_generation": None,
                    "snapshot_ref": None,
                    "_adapter_notes": {
                        "agent_nickname": payload.get("agent_nickname"),
                        "agent_role": payload.get("agent_role"),
                        "source": payload.get("source"),
                    },
                }
                entries[session_id] = entry
                break
    return entries

def inspect_sqlite(path: Path) -> dict:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "size_bytes": 0,
            "modified_at": None,
            "tables": [],
        }

    conn = sqlite3.connect(path)
    tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    conn.close()
    stat = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tables": tables,
    }


def main() -> None:
    thread_index = load_session_index()
    rollout_index = scan_rollouts()

    session_entries = []
    for session_id, payload in sorted(rollout_index.items()):
        merged = dict(payload)
        merged["thread_name"] = thread_index.get(session_id, {}).get("thread_name")
        merged["updated_at"] = thread_index.get(session_id, {}).get("updated_at")
        session_entries.append(merged)

    write_json(
        STATE_ROOT / "sessions" / "index.json",
        {
            "generated_at": utc_now(),
            "entries": session_entries,
        },
    )
    write_json(
        REPORTS_ROOT / "codex-session-inventory.json",
        {
            "generated_at": utc_now(),
            "session_count": len(session_entries),
            "session_ids": [entry["session_id"] for entry in session_entries[:20]],
        },
    )
    write_json(
        STATE_ROOT / "indexes" / "sqlite" / "index.json",
        {
            "generated_at": utc_now(),
            "databases": [inspect_sqlite(STATE_DB_PATH), inspect_sqlite(LOG_DB_PATH)],
        },
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rebuild the state indexes and verify the normalized views exist**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\rebuild_state_indexes_codex.py
Get-Content C:\Users\huibozi\.codex\state\sessions\index.json
Get-Content C:\Users\huibozi\.codex\state\indexes\sqlite\index.json
```

Expected: the session index contains normalized entries with `session_id`, `thread_name`, `updated_at`, `source_path`, `cwd`, `originator`, `cli_version`, `model_provider`, `agent_id`, `decl_generation`, and `snapshot_ref`, while the SQLite index contains metadata only and never copies live `.sqlite` files.

- [ ] **Step 3: Write the state validator that allows warnings for incomplete traceability but rejects broken structure**

Write `C:\Users\huibozi\.codex\scripts\decl_state\validate_state_codex.py`:

```python
from __future__ import annotations

from common import REGISTRIES_ROOT, REPORTS_ROOT, STATE_ROOT, STATUS_ERROR, STATUS_PASS, STATUS_WARN, read_json, utc_now, write_json


def load_registry_ids(name: str) -> set[str]:
    path = REGISTRIES_ROOT / f"{name}.registry.json"
    if not path.exists():
        return set()
    payload = read_json(path)
    return {entry["id"] for entry in payload.get("entries", [])}


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    session_index_path = STATE_ROOT / "sessions" / "index.json"
    sqlite_index_path = STATE_ROOT / "indexes" / "sqlite" / "index.json"

    if not session_index_path.exists():
        errors.append("missing state/sessions/index.json")
    if not sqlite_index_path.exists():
        errors.append("missing state/indexes/sqlite/index.json")

    agent_ids = load_registry_ids("agents")
    skill_ids = load_registry_ids("skills")
    connector_ids = load_registry_ids("mcp")

    if session_index_path.exists():
        payload = read_json(session_index_path)
        for entry in payload.get("entries", []):
            agent_id = entry.get("agent_id")
            if agent_id and agent_id not in agent_ids:
                warnings.append(f"unknown agent_id for session {entry['session_id']}: {agent_id}")
            for skill_id in entry.get("skill_ids", []):
                if skill_id not in skill_ids:
                    warnings.append(f"unknown skill_id for session {entry['session_id']}: {skill_id}")
            for connector_id in entry.get("connector_ids", []):
                if connector_id not in connector_ids:
                    warnings.append(f"unknown connector_id for session {entry['session_id']}: {connector_id}")

    if sqlite_index_path.exists():
        payload = read_json(sqlite_index_path)
        if not isinstance(payload.get("databases"), list):
            errors.append("sqlite metadata index must contain a databases list")

    status = "pass"
    exit_code = STATUS_PASS
    if errors:
        status = "fail"
        exit_code = STATUS_ERROR
    elif warnings:
        status = "warn"
        exit_code = STATUS_WARN

    write_json(
        REPORTS_ROOT / "codex-state-health.json",
        {
            "generated_at": utc_now(),
            "status": status,
            "errors": errors,
            "warnings": warnings,
        },
    )

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run state validation and confirm warning-only semantics are working**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\validate_state_codex.py
Get-Content C:\Users\huibozi\.codex\generated\reports\codex-state-health.json
```

Expected: the validator exits `0` or `2`, never `1`, as long as the only issues are incomplete historical traceability or unmanaged subagent sessions.

### Task 7: Wire The Full Validation Gate And Publish The Operator Guide

**Files:**
- Create: `C:\Users\huibozi\.codex\scripts\decl_state\validate_full_codex.py`
- Create: `C:\Users\huibozi\.codex\CODEX-DECL-STATE.md`
- Create: `C:\Users\huibozi\.codex\generated\reports\codex-full-validation.json`
- [ ] **Step 1: Write the full validation entrypoint with the locked execution order and exit-code semantics**

Write `C:\Users\huibozi\.codex\scripts\decl_state\validate_full_codex.py`:

```python
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from common import REPORTS_ROOT, STATUS_ERROR, STATUS_PASS, STATUS_WARN, read_json, utc_now, write_json

SCRIPT_ROOT = Path(r"C:\Users\huibozi\.codex\scripts\decl_state")


def run(script_name: str) -> int:
    result = subprocess.run([sys.executable, str(SCRIPT_ROOT / script_name)], check=False)
    if result.returncode == STATUS_ERROR:
        raise SystemExit(STATUS_ERROR)
    return result.returncode


def load_report(name: str) -> dict:
    return read_json(REPORTS_ROOT / name)


def main() -> None:
    steps = [
        ("validate declarations", "validate_decl_codex.py"),
        ("rebuild registries", "build_registries_codex.py"),
        ("rebuild state indexes", "rebuild_state_indexes_codex.py"),
        ("validate state", "validate_state_codex.py"),
        ("build snapshot", "build_snapshot_codex.py"),
        ("backfill decl_generation", "backfill_decl_generation_codex.py"),
    ]

    step_results = []
    for label, script_name in steps:
        exit_code = run(script_name)
        step_results.append({"step": label, "script": script_name, "exit_code": exit_code})

    decl_report = load_report("codex-decl-health.json")
    state_report = load_report("codex-state-health.json")

    errors = []
    warnings = []
    if decl_report.get("status") == "fail":
        errors.extend(decl_report.get("errors", []))
    warnings.extend(decl_report.get("warnings", []))

    if state_report.get("status") == "fail":
        errors.extend(state_report.get("errors", []))
    else:
        warnings.extend(state_report.get("warnings", []))

    status = "pass"
    exit_code = STATUS_PASS
    if errors:
        status = "fail"
        exit_code = STATUS_ERROR
    elif warnings:
        status = "warn"
        exit_code = STATUS_WARN

    write_json(
        REPORTS_ROOT / "codex-full-validation.json",
        {
            "generated_at": utc_now(),
            "status": status,
            "exit_code": exit_code,
            "steps": step_results,
            "errors": errors,
            "warnings": warnings,
        },
    )

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the operator guide that explains the new steady-state workflow**

Create `C:\Users\huibozi\.codex\CODEX-DECL-STATE.md` with these sections:

```markdown
# Codex Decl-State Workflow

## Edit Rules
- Edit only `decl/` for the managed Phase 1 surfaces.
- Never hand-edit `generated/`.
- Do not assume top-level native Codex files are mirrors.
- Leave `config.toml`, `skills/`, `rules/default.rules`, `sessions/`, and the live SQLite files to the native Codex runtime.

## Validation Commands
- `python C:\Users\huibozi\.codex\scripts\decl_state\validate_decl_codex.py`
- `python C:\Users\huibozi\.codex\scripts\decl_state\validate_state_codex.py`
- `python C:\Users\huibozi\.codex\scripts\decl_state\validate_full_codex.py`

## Import Commands
- `python C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py --agent`
- `python C:\Users\huibozi\.codex\scripts\decl_state\import_decl_codex.py --skills --rules`
- `python C:\Users\huibozi\.codex\scripts\decl_state\rebuild_state_indexes_codex.py`

## Snapshot And Cleanup Rules
- `generated/registries/` and `generated/reports/` are overwritten on every full validate.
- `generated/snapshots/` keeps the newest five files.
- `state/indexes/sqlite/` stores metadata only, never the live `.sqlite` files.
```

- [ ] **Step 3: Run the full validation gate and confirm the Codex Phase 1 additive model is stable**

Run:

```powershell
python C:\Users\huibozi\.codex\scripts\decl_state\validate_full_codex.py
Get-Content C:\Users\huibozi\.codex\generated\reports\codex-decl-health.json
Get-Content C:\Users\huibozi\.codex\generated\reports\codex-state-health.json
Get-Content C:\Users\huibozi\.codex\generated\reports\codex-full-validation.json
```

Expected:

```text
codex-decl-health.json -> status pass
codex-state-health.json -> status pass or warn
codex-full-validation.json -> exit_code 0 or 2, never 1
```

A warning-only result is acceptable in Phase 1 when the warnings are limited to incomplete historical traceability or unmanaged subagent sessions.

## Self-Review

### Spec coverage

- additive `decl/`, `state/`, and `generated/` bootstrap: Task 1
- locked JSON declaration schemas and Codex declaration validation: Task 2
- seeded `codex-default` agent with neutral `isolation` plus adapter notes: Task 3
- managed skill import and native rule wrapper: Task 4
- registry, snapshot, and explicit backfill order: Task 5
- normalized session and SQLite metadata indexes with warning-only state validation: Task 6
- full validation gate, exit-code semantics, and operator guide: Task 7

### Placeholder scan

- No `TODO`
- No `TBD`
- No unnamed files
- No unspecified commands

### Type consistency

- Skills use `id` as the unique identifier; `name` is optional display metadata only.
- Agents use `compute_profile`, not `effort`.
- Policies include `priority`.
- `state/indexes/sqlite/` is metadata-only and never stores live `.sqlite` files.
- Registry and snapshot generation order is `registries -> snapshot -> backfill`.
- Full validation order is `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`.
