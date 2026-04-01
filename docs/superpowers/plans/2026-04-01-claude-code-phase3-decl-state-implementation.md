# Claude Code Phase 3 Decl-State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure `C:\Users\huibozi\.claude` into a canonical `decl/`, `state/`, and `generated/` layout without breaking the current Claude Code runtime, then validate the cutover with repeatable scripts and reports.

**Architecture:** Keep `C:\Users\huibozi\.claude\decl` as the only human-edited fact source for agents, skills, commands, rules, and MCP connectors. Keep `C:\Users\huibozi\.claude\state` as normalized runtime copies and `C:\Users\huibozi\.claude\generated` as disposable derived outputs. Generate legacy compatibility surfaces from `decl/` for agents, commands, rules, and MCP, and treat skills as an inventory-first migration where canonical metadata lives in `decl/skills` while existing legacy `SKILL.md` bodies remain the compatibility corpus during Phase 3.

**Tech Stack:** PowerShell 7+, Python 3.11, Markdown, JSON, JSON Schema Draft 2020-12, `jsonschema`, existing Claude Code runtime files under `C:\Users\huibozi\.claude`

---

## Current Baseline To Preserve

- `C:\Users\huibozi\.claude` is **not** a git repository, so rollback checkpoints must be filesystem backups under `C:\Users\huibozi\.claude\backups\decl-state\`.
- Current legacy declaration surfaces:
  - `C:\Users\huibozi\.claude\agents\*.md` (`architect`, `build-error-resolver`, `code-reviewer`, `doc-updater`, `e2e-runner`, `planner`, `refactor-cleaner`, `security-reviewer`, `tdd-guide`)
  - `C:\Users\huibozi\.claude\commands\*.md` (`build-fix`, `checkpoint`, `code-review`, `e2e`, `eval`, `learn`, `orchestrate`, `plan`, `refactor-clean`, `setup-pm`, `tdd`, `test-coverage`, `update-codemaps`, `update-docs`, `verify`)
  - `C:\Users\huibozi\.claude\rules\*.md` (`agents`, `coding-style`, `git-workflow`, `hooks`, `patterns`, `performance`, `security`, `testing`)
  - `C:\Users\huibozi\.claude.json` currently holds the active `mcpServers` block, including `codex`
- Current legacy state surfaces:
  - `C:\Users\huibozi\.claude\sessions\*.json`
  - `C:\Users\huibozi\.claude\history.jsonl`
  - `C:\Users\huibozi\.claude\projects\`
  - `C:\Users\huibozi\.claude\shell-snapshots\`
- Current skill corpus:
  - `C:\Users\huibozi\.claude\skills\` contains `1324` directories, `1317` of which already contain `SKILL.md`
  - `C:\Users\huibozi\.claude\ultimate-skills\` contains a curated subset, including `brainstorming`, `dispatching-parallel-agents`, `executing-plans`, and `finishing-a-development-branch`
- Phase 3 scope includes only:
  - `agents`, `skills`, `commands`, `rules`, `mcp`
  - `sessions`, `projects`, `history`, `shell-snapshots`
  - validation, registry, snapshot, and compatibility-mirror tooling
- Phase 3 does **not** restructure `plugins/`, `contexts/`, `todos/`, `claude-organizer/`, `backups/`, or `debug/` beyond inventory and drift reporting.

## Implementation Layout

- Canonical declaration root: `C:\Users\huibozi\.claude\decl\`
- Normalized state root: `C:\Users\huibozi\.claude\state\`
- Derived outputs root: `C:\Users\huibozi\.claude\generated\`
- Migration and validation scripts: `C:\Users\huibozi\.claude\scripts\decl_state\`
- Operator note for future humans: `C:\Users\huibozi\.claude\CLAUDE-DECL-STATE.md`

### Task 1: Bootstrap Canonical Layout And Rollback Inventory

**Files:**
- Create: `C:\Users\huibozi\.claude\decl\README.md`
- Create: `C:\Users\huibozi\.claude\state\README.md`
- Create: `C:\Users\huibozi\.claude\generated\README.md`
- Create: `C:\Users\huibozi\.claude\generated\.gitignore`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\common.py`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\bootstrap.py`
- Create: `C:\Users\huibozi\.claude\generated\reports\bootstrap-inventory.json`
- Create: `C:\Users\huibozi\.claude\backups\decl-state\bootstrap-<timestamp>\` (filesystem checkpoint written by the script)

- [ ] **Step 1: Create the shared helper module used by every migration script**

Write `C:\Users\huibozi\.claude\scripts\decl_state\common.py` with these helpers:

```python
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(r"C:\Users\huibozi\.claude")
HOME_CONFIG_PATH = Path(r"C:\Users\huibozi\.claude.json")
DECL_ROOT = CLAUDE_ROOT / "decl"
STATE_ROOT = CLAUDE_ROOT / "state"
GENERATED_ROOT = CLAUDE_ROOT / "generated"
BACKUP_ROOT = CLAUDE_ROOT / "backups" / "decl-state"
REPORTS_ROOT = GENERATED_ROOT / "reports"
REGISTRIES_ROOT = GENERATED_ROOT / "registries"
SNAPSHOTS_ROOT = GENERATED_ROOT / "snapshots"


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_tree(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)
```

- [ ] **Step 2: Create the bootstrap script that lays down the canonical folders and captures a rollback checkpoint**

Write `C:\Users\huibozi\.claude\scripts\decl_state\bootstrap.py`:

```python
from __future__ import annotations

from common import (
    BACKUP_ROOT,
    CLAUDE_ROOT,
    DECL_ROOT,
    GENERATED_ROOT,
    HOME_CONFIG_PATH,
    REPORTS_ROOT,
    STATE_ROOT,
    copy_tree,
    ensure_dir,
    timestamp_slug,
    utc_now,
    write_json,
)

DECL_DIRS = ["agents", "skills", "commands", "rules", "mcp"]
STATE_DIRS = ["sessions", "projects", "history", "shell-snapshots"]
GENERATED_DIRS = ["registries", "reports", "snapshots"]
LEGACY_PATHS = [
    "agents",
    "commands",
    "rules",
    "skills",
    "ultimate-skills",
    "sessions",
    "projects",
    "shell-snapshots",
    "history.jsonl",
    "settings.json",
    "settings.local.json",
    "project-config.json",
]


def main() -> None:
    stamp = timestamp_slug()
    backup_dir = ensure_dir(BACKUP_ROOT / f"bootstrap-{stamp}")

    ensure_dir(DECL_ROOT)
    ensure_dir(STATE_ROOT)
    ensure_dir(GENERATED_ROOT)

    for name in DECL_DIRS:
        ensure_dir(DECL_ROOT / name)
    for name in STATE_DIRS:
        ensure_dir(STATE_ROOT / name)
    for name in GENERATED_DIRS:
        ensure_dir(GENERATED_ROOT / name)

    for legacy_name in LEGACY_PATHS:
        source = CLAUDE_ROOT / legacy_name
        destination = backup_dir / "legacy" / legacy_name
        if source.is_dir():
            copy_tree(source, destination)
        elif source.exists():
            ensure_dir(destination.parent)
            destination.write_bytes(source.read_bytes())

    if HOME_CONFIG_PATH.exists():
        home_copy = backup_dir / "legacy-home-config" / HOME_CONFIG_PATH.name
        ensure_dir(home_copy.parent)
        home_copy.write_bytes(HOME_CONFIG_PATH.read_bytes())

    write_json(
        REPORTS_ROOT / "bootstrap-inventory.json",
        {
            "generated_at": utc_now(),
            "backup_dir": str(backup_dir),
            "decl_dirs": DECL_DIRS,
            "state_dirs": STATE_DIRS,
            "generated_dirs": GENERATED_DIRS,
            "legacy_paths": LEGACY_PATHS,
        },
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write the three root READMEs and the generated ignore file**

Create these exact contents:

```markdown
# Declaration Layer

Edit files in this tree directly. This is the only authoritative source for agents, skills, commands, rules, and MCP connectors.

Do not hand-edit `..\generated\` or the legacy top-level compatibility files.
```

```markdown
# State Layer

This tree stores normalized runtime copies of sessions, projects, history, and shell snapshots.

State files may reference declaration objects by `id`, `decl_generation`, and `snapshot_ref`. They never own declaration content.
```

```markdown
# Generated Layer

This tree contains derived outputs only:
- `registries/`
- `reports/`
- `snapshots/`

Every validate run fully rewrites `registries/` and `reports/`. `snapshots/` keeps only the newest five files.
```

```gitignore
*
!.gitignore
```

- [ ] **Step 4: Run the bootstrap script**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\bootstrap.py
```

Expected: `decl\`, `state\`, and `generated\` exist, `bootstrap-inventory.json` exists, and a new `C:\Users\huibozi\.claude\backups\decl-state\bootstrap-<timestamp>\` directory exists.

- [ ] **Step 5: Verify the bootstrap output**

Run:

```powershell
Get-ChildItem C:\Users\huibozi\.claude\decl
Get-ChildItem C:\Users\huibozi\.claude\state
Get-ChildItem C:\Users\huibozi\.claude\generated
Get-Content C:\Users\huibozi\.claude\generated\reports\bootstrap-inventory.json
```

Expected: all three roots and their child directories exist; the inventory JSON lists legacy paths and the timestamped backup path.

### Task 2: Add Declaration Schemas And Validation Entry Points

**Files:**
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\schemas\agent.schema.json`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\schemas\skill.schema.json`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\schemas\command.schema.json`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\schemas\policy.schema.json`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\schemas\connector.schema.json`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\parsers.py`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\validate_decl.py`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\validate_state.py`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\validate_full.py`
- Create: `C:\Users\huibozi\.claude\generated\reports\decl-health.json`
- Create: `C:\Users\huibozi\.claude\generated\reports\state-health.json`

- [ ] **Step 1: Write the five declaration schemas with the locked Phase 3 field names**

Use this pattern for every schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": true,
  "required": ["id", "description"],
  "properties": {
    "id": { "type": "string", "minLength": 1 }
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

- [ ] **Step 2: Write the parser helpers for frontmatter markdown inputs**

Write `C:\Users\huibozi\.claude\scripts\decl_state\parsers.py`:

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

- [ ] **Step 3: Write the declaration validator**

Write `C:\Users\huibozi\.claude\scripts\decl_state\validate_decl.py`:

```python
from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from common import DECL_ROOT, REPORTS_ROOT, read_json, utc_now, write_json


DECL_MAP = {
    "agents": "agent.schema.json",
    "skills": "skill.schema.json",
    "commands": "command.schema.json",
    "rules": "policy.schema.json",
    "mcp": "connector.schema.json",
}


def iter_decl_json_files(group_root: Path):
    for child in sorted(group_root.iterdir()):
        if child.is_dir():
            for candidate in sorted(child.glob("*.json")):
                yield candidate


def main() -> None:
    errors = []
    warnings = []
    ids_seen: dict[str, set[str]] = {key: set() for key in DECL_MAP}

    for group, schema_name in DECL_MAP.items():
        schema = read_json(Path(__file__).parent / "schemas" / schema_name)
        validator = Draft202012Validator(schema)
        for json_path in iter_decl_json_files(DECL_ROOT / group):
            payload = read_json(json_path)
            object_id = payload["id"]
            if object_id in ids_seen[group]:
                errors.append(f"duplicate id {group}:{object_id}")
            ids_seen[group].add(object_id)
            for issue in validator.iter_errors(payload):
                errors.append(f"{json_path}: {issue.message}")

    write_json(
        REPORTS_ROOT / "decl-health.json",
        {
            "generated_at": utc_now(),
            "errors": errors,
            "warnings": warnings,
            "status": "pass" if not errors else "fail",
        },
    )

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write the state validator and full validator**

Use these behaviors:

```text
validate_state.py
- scan state/sessions, state/projects, state/history, state/shell-snapshots
- warn on dangling agent_id, skill_id, connector_id, command_id
- do not hard-fail on historical dangling references
- write generated/reports/state-health.json

validate_full.py
- run validate_decl.py
- run validate_state.py
- run build_registries.py
- run build_snapshot.py
- rerun registry backfill
- run mirror_decl.py --check-drift
- prune generated/snapshots to latest 5
```

Use `subprocess.run(..., check=True)` inside `validate_full.py`.

- [ ] **Step 5: Verify the validation entry points parse cleanly**

Run:

```powershell
python -c "import jsonschema, yaml; print('deps-ok')"
python -m py_compile C:\Users\huibozi\.claude\scripts\decl_state\common.py C:\Users\huibozi\.claude\scripts\decl_state\parsers.py C:\Users\huibozi\.claude\scripts\decl_state\validate_decl.py C:\Users\huibozi\.claude\scripts\decl_state\validate_state.py C:\Users\huibozi\.claude\scripts\decl_state\validate_full.py
```

Expected: `deps-ok` and no Python compile errors.

### Task 3: Import Agents, Commands, And Rules Into `decl/`

**Files:**
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py`
- Create: `C:\Users\huibozi\.claude\decl\agents\<agent-id>\agent.json` and `prompt.md` for `architect`, `build-error-resolver`, `code-reviewer`, `doc-updater`, `e2e-runner`, `planner`, `refactor-cleaner`, `security-reviewer`, `tdd-guide`
- Create: `C:\Users\huibozi\.claude\decl\commands\<command-id>\command.json` and `README.md` for `build-fix`, `checkpoint`, `code-review`, `e2e`, `eval`, `learn`, `orchestrate`, `plan`, `refactor-clean`, `setup-pm`, `tdd`, `test-coverage`, `update-codemaps`, `update-docs`, `verify`
- Create: `C:\Users\huibozi\.claude\decl\rules\<rule-id>\policy.json` and `policy.md` for `agents`, `coding-style`, `git-workflow`, `hooks`, `patterns`, `performance`, `security`, `testing`

- [ ] **Step 1: Write the importer that transforms legacy markdown into canonical declaration units**

Write `C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py` with these top-level functions:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from common import CLAUDE_ROOT, DECL_ROOT, ensure_dir, write_json
from parsers import read_frontmatter_markdown


def compute_profile_for_model(model: str | None) -> str:
    if model == "opus":
        return "high"
    if model in {"sonnet", "haiku"}:
        return "balanced"
    return "balanced"


def import_agent(markdown_path: Path) -> None:
    metadata, body = read_frontmatter_markdown(markdown_path)
    agent_id = markdown_path.stem
    target = ensure_dir(DECL_ROOT / "agents" / agent_id)
    write_json(
        target / "agent.json",
        {
            "id": agent_id,
            "description": metadata.get("description", ""),
            "model": metadata.get("model", "inherit"),
            "compute_profile": compute_profile_for_model(metadata.get("model")),
            "tools": metadata.get("tools", []),
            "skills": [],
            "permission_mode": "inherit",
            "memory_scope": "session",
            "isolation": "none",
            "max_turns": 0,
            "required_mcp_servers": [],
        },
    )
    (target / "prompt.md").write_text(body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", action="store_true")
    parser.add_argument("--commands", action="store_true")
    parser.add_argument("--rules", action="store_true")
    parser.add_argument("--mcp", action="store_true")
    parser.add_argument("--skills", action="store_true")
    args = parser.parse_args()

    if args.agents:
        for path in sorted((CLAUDE_ROOT / "agents").glob("*.md")):
            import_agent(path)
```

Use the same `argparse` dispatch pattern for commands, rules, MCP, and skills so the plan's later commands are runnable.

Mirror this pattern for commands and rules:

```python
def import_command(markdown_path: Path) -> None:
    ...
    "handler_type": "pipeline" if markdown_path.stem in {"plan", "orchestrate"} else "skill",
    "aliases": [f"/{markdown_path.stem}"],
    "kind": "interactive",
    "input_contract": {"type": "freeform-markdown"},
    "enabled_when": ["default"],
```

```python
def import_rule(markdown_path: Path) -> None:
    ...
    "scope": "global",
    "priority": 90 if markdown_path.stem == "security" else 50,
    "allow_rules": [],
    "deny_rules": [],
    "ask_rules": [],
    "danger_filters": [],
    "audit_requirements": [],
```

- [ ] **Step 2: Seed the import logic with a known-good example from the current `architect` agent**

The importer should produce this exact shape in `C:\Users\huibozi\.claude\decl\agents\architect\agent.json`:

```json
{
  "id": "architect",
  "description": "Software architecture specialist for system design, scalability, and technical decision-making. Use PROACTIVELY when planning new features, refactoring large systems, or making architectural decisions.",
  "model": "opus",
  "compute_profile": "high",
  "tools": ["Read", "Grep", "Glob"],
  "skills": [],
  "permission_mode": "inherit",
  "memory_scope": "session",
  "isolation": "none",
  "max_turns": 0,
  "required_mcp_servers": []
}
```

The importer should also strip the frontmatter and write the markdown body to `C:\Users\huibozi\.claude\decl\agents\architect\prompt.md`.

- [ ] **Step 3: Run the declaration importer**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py --agents --commands --rules
```

Expected: canonical directories appear under `decl\agents`, `decl\commands`, and `decl\rules` for all existing markdown files.

- [ ] **Step 4: Validate the imported declaration files**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\validate_decl.py
Get-Content C:\Users\huibozi\.claude\generated\reports\decl-health.json
```

Expected: `status` is `pass`, no duplicate IDs, and the report contains zero schema errors.

- [ ] **Step 5: Create a rollback checkpoint after the declaration import**

Run:

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Copy-Item -Recurse -Force C:\Users\huibozi\.claude\decl "C:\Users\huibozi\.claude\backups\decl-state\decl-after-import-$stamp"
```

Expected: a new backup copy of the canonical declaration tree exists under `backups\decl-state\`.

### Task 4: Import MCP Connectors And Protect Root Config Compatibility

**Files:**
- Modify: `C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\render_root_config.py`
- Create: `C:\Users\huibozi\.claude\decl\mcp\codex\connector.json`
- Create: `C:\Users\huibozi\.claude\decl\mcp\codex\README.md`
- Modify: `C:\Users\huibozi\.claude.json` (only the `mcpServers` subtree, preserving unrelated keys)

- [ ] **Step 1: Extend the declaration importer to read the active MCP server definitions from the root home config**

Add this function to `C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py`:

```python
from common import HOME_CONFIG_PATH, read_json


def import_mcp() -> None:
    home_config = read_json(HOME_CONFIG_PATH)
    for connector_id, payload in sorted(home_config.get("mcpServers", {}).items()):
        target = ensure_dir(DECL_ROOT / "mcp" / connector_id)
        write_json(
            target / "connector.json",
            {
                "id": connector_id,
                "kind": payload.get("type", "stdio"),
                "transport": payload.get("type", "stdio"),
                "command": payload.get("command", ""),
                "args": payload.get("args", []),
                "env_policy": sorted(payload.get("env", {}).keys()),
                "capabilities": ["tools"],
                "auth_mode": "none",
                "healthcheck": {
                    "command": [payload.get("command", ""), "--version"],
                    "expect_exit_code": 0,
                },
            },
        )
```

For `codex`, the expected canonical file is:

```json
{
  "id": "codex",
  "kind": "stdio",
  "transport": "stdio",
  "command": "codex",
  "args": ["mcp-server"],
  "env_policy": [],
  "capabilities": ["tools"],
  "auth_mode": "none",
  "healthcheck": {
    "command": ["codex", "--version"],
    "expect_exit_code": 0
  }
}
```

- [ ] **Step 2: Write the root config renderer that updates only the compatibility MCP block**

Write `C:\Users\huibozi\.claude\scripts\decl_state\render_root_config.py`:

```python
from __future__ import annotations

from common import DECL_ROOT, HOME_CONFIG_PATH, read_json, write_json


def main() -> None:
    root_config = read_json(HOME_CONFIG_PATH)
    mcp_servers = {}
    for connector_dir in sorted((DECL_ROOT / "mcp").iterdir()):
        payload = read_json(connector_dir / "connector.json")
        existing_server = root_config.get("mcpServers", {}).get(payload["id"], {})
        existing_env = existing_server.get("env", {})
        mcp_servers[payload["id"]] = {
            "type": payload["kind"],
            "command": payload["command"],
            "args": payload["args"],
            "env": {name: existing_env.get(name, "") for name in payload["env_policy"]},
        }
    root_config["mcpServers"] = mcp_servers
    write_json(HOME_CONFIG_PATH, root_config)


if __name__ == "__main__":
    main()
```

This renderer must **not** copy secrets into `decl/`. `env_policy` stores only environment variable names, never values.

- [ ] **Step 3: Run the MCP import and root-config render**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py --mcp
python C:\Users\huibozi\.claude\scripts\decl_state\render_root_config.py
```

Expected: `C:\Users\huibozi\.claude\decl\mcp\codex\connector.json` exists and `C:\Users\huibozi\.claude.json` still contains all unrelated user settings plus the rendered `mcpServers` block.

- [ ] **Step 4: Verify the root config render was non-destructive**

Run:

```powershell
@'
import json
from pathlib import Path
payload = json.loads(Path(r"C:\Users\huibozi\.claude.json").read_text(encoding="utf-8"))
print(sorted(payload["mcpServers"].keys()))
print("oauthAccount" in payload)
print("projects" in payload)
'@ | python -
```

Expected: `['codex']`, then `True`, then `True`.

### Task 5: Inventory The Skill Corpus And Import A Managed First Cohort

**Files:**
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\inventory_skills.py`
- Modify: `C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py`
- Create: `C:\Users\huibozi\.claude\decl\skills\README.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\brainstorming\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\dispatching-parallel-agents\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\executing-plans\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\finishing-a-development-branch\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\subagent-driven-development\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\verification-before-completion\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\decl\skills\using-git-worktrees\skill.json` and `skill.md`
- Create: `C:\Users\huibozi\.claude\generated\reports\skills-inventory.json`

- [ ] **Step 1: Inventory the existing skill corpus before importing any managed subset**

Write `C:\Users\huibozi\.claude\scripts\decl_state\inventory_skills.py`:

```python
from __future__ import annotations

from pathlib import Path

from common import CLAUDE_ROOT, REPORTS_ROOT, utc_now, write_json


ROOTS = [
    CLAUDE_ROOT / "skills",
    CLAUDE_ROOT / "ultimate-skills",
]


def main() -> None:
    entries = []
    for root in ROOTS:
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir():
                entries.append(
                    {
                        "id": child.name,
                        "legacy_root": str(root),
                        "skill_md_exists": (child / "SKILL.md").exists(),
                    }
                )

    write_json(
        REPORTS_ROOT / "skills-inventory.json",
        {
            "generated_at": utc_now(),
            "entry_count": len(entries),
            "entries": entries,
        },
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Extend the declaration importer with a managed skill cohort**

Add this exact cohort map to `C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py`:

```python
MANAGED_SKILLS = {
    "brainstorming": Path(r"C:\Users\huibozi\.claude\ultimate-skills\brainstorming\SKILL.md"),
    "dispatching-parallel-agents": Path(r"C:\Users\huibozi\.claude\ultimate-skills\dispatching-parallel-agents\SKILL.md"),
    "executing-plans": Path(r"C:\Users\huibozi\.claude\ultimate-skills\executing-plans\SKILL.md"),
    "finishing-a-development-branch": Path(r"C:\Users\huibozi\.claude\ultimate-skills\finishing-a-development-branch\SKILL.md"),
    "subagent-driven-development": Path(r"C:\Users\huibozi\.claude\skills\subagent-driven-development\SKILL.md"),
    "verification-before-completion": Path(r"C:\Users\huibozi\.claude\skills\verification-before-completion\SKILL.md"),
    "using-git-worktrees": Path(r"C:\Users\huibozi\.claude\skills\using-git-worktrees\SKILL.md"),
}
```

Then add this importer:

```python
def import_skill(skill_id: str, skill_path: Path) -> None:
    metadata, body = read_frontmatter_markdown(skill_path)
    target = ensure_dir(DECL_ROOT / "skills" / skill_id)
    write_json(
        target / "skill.json",
        {
            "id": skill_id,
            "name": metadata.get("name", skill_id),
            "description": metadata.get("description", ""),
            "when_to_use": [metadata.get("description", "")] if metadata.get("description") else [],
            "allowed_tools": [],
            "argument_hint": f"Use {skill_id} only when the request clearly matches its description.",
            "model_override": None,
            "path_conditions": [],
            "hooks": [],
        },
    )
    (target / "skill.md").write_text(body, encoding="utf-8")
```

- [ ] **Step 3: Run the skill inventory and the managed skill import**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\inventory_skills.py
python C:\Users\huibozi\.claude\scripts\decl_state\import_decl.py --skills
```

Expected: `skills-inventory.json` reports the full legacy corpus and the seven managed skills exist in `C:\Users\huibozi\.claude\decl\skills\`.

- [ ] **Step 4: Verify the first managed skill import**

Run:

```powershell
Get-Content C:\Users\huibozi\.claude\decl\skills\brainstorming\skill.json
Get-Content -TotalCount 20 C:\Users\huibozi\.claude\decl\skills\brainstorming\skill.md
```

Expected: `skill.json` uses `id`, not `name`, as the unique key, and `skill.md` contains the body without frontmatter duplication.

### Task 6: Build Registries, Snapshots, And Drift Reports

**Files:**
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\build_registries.py`
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\build_snapshot.py`
- Create: `C:\Users\huibozi\.claude\generated\registries\agents.registry.json`
- Create: `C:\Users\huibozi\.claude\generated\registries\skills.registry.json`
- Create: `C:\Users\huibozi\.claude\generated\registries\commands.registry.json`
- Create: `C:\Users\huibozi\.claude\generated\registries\rules.registry.json`
- Create: `C:\Users\huibozi\.claude\generated\registries\mcp.registry.json`
- Create: `C:\Users\huibozi\.claude\generated\snapshots\decl-<timestamp>.json`
- Create: `C:\Users\huibozi\.claude\generated\reports\mirror-drift.json`

- [ ] **Step 1: Write the registry builder with the locked registry shape**

Write `C:\Users\huibozi\.claude\scripts\decl_state\build_registries.py`:

```python
from __future__ import annotations

from common import DECL_ROOT, REGISTRIES_ROOT, sha256_file, utc_now, write_json


GROUPS = {
    "agents": "agent.json",
    "skills": "skill.json",
    "commands": "command.json",
    "rules": "policy.json",
    "mcp": "connector.json",
}


def build_group(group: str, filename: str) -> None:
    entries = []
    for child in sorted((DECL_ROOT / group).iterdir()):
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


def main() -> None:
    for group, filename in GROUPS.items():
        build_group(group, filename)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the snapshot builder using the locked generation order**

Write `C:\Users\huibozi\.claude\scripts\decl_state\build_snapshot.py`:

```python
from __future__ import annotations

import hashlib
import json

from common import REGISTRIES_ROOT, SNAPSHOTS_ROOT, read_json, timestamp_slug, utc_now, write_json


def main() -> None:
    registry_payloads = {}
    for path in sorted(REGISTRIES_ROOT.glob("*.registry.json")):
        registry_payloads[path.name] = read_json(path)

    combined = json.dumps(registry_payloads, sort_keys=True, ensure_ascii=False)
    decl_generation = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]

    snapshot_path = SNAPSHOTS_ROOT / f"decl-{timestamp_slug()}.json"
    write_json(
        snapshot_path,
        {
            "generated_at": utc_now(),
            "decl_generation": decl_generation,
            "registries": registry_payloads,
        },
    )

    for path in sorted(REGISTRIES_ROOT.glob("*.registry.json")):
        payload = read_json(path)
        for entry in payload["entries"]:
            entry["decl_generation"] = decl_generation
        write_json(path, payload)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the registry and snapshot generation**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\build_registries.py
python C:\Users\huibozi\.claude\scripts\decl_state\build_snapshot.py
```

Expected: five `*.registry.json` files exist and the newest `decl-<timestamp>.json` snapshot contains a non-empty `decl_generation`.

- [ ] **Step 4: Verify the registry backfill order**

Run:

```powershell
@'
import json
from pathlib import Path
for path in sorted(Path(r"C:\Users\huibozi\.claude\generated\registries").glob("*.registry.json")):
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path.name, {entry["decl_generation"] for entry in payload["entries"][:1]})
'@ | python -
```

Expected: every registry prints a non-`pending` `decl_generation` value.

### Task 7: Mirror Canonical Declarations Back To Legacy Compatibility Surfaces

**Files:**
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\mirror_decl.py`
- Modify: `C:\Users\huibozi\.claude\agents\*.md`
- Modify: `C:\Users\huibozi\.claude\commands\*.md`
- Modify: `C:\Users\huibozi\.claude\rules\*.md`
- Modify: `C:\Users\huibozi\.claude.json`
- Create: `C:\Users\huibozi\.claude\generated\reports\mirror-drift.json`

- [ ] **Step 1: Write the mirror script with one-way source markers**

Write `C:\Users\huibozi\.claude\scripts\decl_state\mirror_decl.py`:

```python
from __future__ import annotations

from pathlib import Path

from common import CLAUDE_ROOT, DECL_ROOT, REPORTS_ROOT, utc_now, write_json


def generated_header(source_path: Path) -> str:
    return (
        f"<!-- generated by decl_state mirror from {source_path}; "
        "manual edits are overwritten -->\n\n"
    )
```

Implement three renderers:

```python
render_agent(agent_dir) -> writes C:\Users\huibozi\.claude\agents\<id>.md
render_command(command_dir) -> writes C:\Users\huibozi\.claude\commands\<id>.md
render_rule(rule_dir) -> writes C:\Users\huibozi\.claude\rules\<id>.md
```

Each renderer should prepend the generated header and then rebuild the legacy markdown from the canonical JSON plus body file.

- [ ] **Step 2: Add a drift-check mode before destructive overwrite**

The script must support:

```text
python mirror_decl.py --check-drift
python mirror_decl.py --write
```

`--check-drift` should compare the rendered text to the current legacy file and write this report to `C:\Users\huibozi\.claude\generated\reports\mirror-drift.json`:

```json
{
  "generated_at": "2026-04-01T00:00:00Z",
  "status": "warning",
  "drifted_files": [
    {
      "path": "C:\\Users\\huibozi\\.claude\\agents\\architect.md",
      "reason": "legacy file differs from canonical render"
    }
  ]
}
```

- [ ] **Step 3: Run the drift check, then write the compatibility mirror**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\mirror_decl.py --check-drift
Get-Content C:\Users\huibozi\.claude\generated\reports\mirror-drift.json
python C:\Users\huibozi\.claude\scripts\decl_state\mirror_decl.py --write
python C:\Users\huibozi\.claude\scripts\decl_state\render_root_config.py
```

Expected: drift warnings are recorded first, then the legacy markdown files are regenerated with source markers, and the root `.claude.json` still contains the rendered `mcpServers` block.

- [ ] **Step 4: Verify a mirrored file now advertises its one-way source**

Run:

```powershell
Get-Content -TotalCount 8 C:\Users\huibozi\.claude\agents\architect.md
```

Expected: line 1 is the generated HTML comment and the rest of the file matches the canonical prompt and metadata.

### Task 8: Import Runtime State, Backfill `decl_generation`, And Publish Steady-State Docs

**Files:**
- Create: `C:\Users\huibozi\.claude\scripts\decl_state\import_state.py`
- Create: `C:\Users\huibozi\.claude\state\history\history.jsonl`
- Create: `C:\Users\huibozi\.claude\state\projects\index.json`
- Create: `C:\Users\huibozi\.claude\state\sessions\index.json`
- Create: `C:\Users\huibozi\.claude\generated\reports\migration-summary.json`
- Create: `C:\Users\huibozi\.claude\CLAUDE-DECL-STATE.md`
- Modify: `C:\Users\huibozi\.claude\scripts\decl_state\validate_state.py`
- Modify: `C:\Users\huibozi\.claude\scripts\decl_state\validate_full.py`

- [ ] **Step 1: Write the state importer that copies and annotates sessions, history, projects, and shell snapshots**

Write `C:\Users\huibozi\.claude\scripts\decl_state\import_state.py` with these behaviors:

```python
from __future__ import annotations

import json
import shutil

from common import CLAUDE_ROOT, STATE_ROOT, SNAPSHOTS_ROOT, utc_now, write_json


def current_decl_generation() -> str | None:
    snapshots = sorted(SNAPSHOTS_ROOT.glob("decl-*.json"))
    if not snapshots:
        return None
    payload = json.loads(snapshots[-1].read_text(encoding="utf-8"))
    return payload["decl_generation"]
```

For sessions:

```text
- copy each legacy session JSON from C:\Users\huibozi\.claude\sessions\
- preserve original payload
- if the payload already contains an agent or command name that can be mapped to current declaration IDs, add decl_generation and snapshot_ref
- if not traceable, set decl_generation to None and record a warning
```

For history:

```text
- read C:\Users\huibozi\.claude\history.jsonl line by line
- when the line parses as JSON, add decl_generation only if a referenced session can be mapped
- when the line cannot be mapped, preserve the content and emit a warning into migration-summary.json
```

For projects:

```text
- copy each directory under C:\Users\huibozi\.claude\projects\ into C:\Users\huibozi\.claude\state\projects\
- write state\projects\index.json containing project_id, source_path, default agent_id when inferable, and connector_ids when inferable from root config
```

- [ ] **Step 2: Run the state importer**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\import_state.py
```

Expected: normalized copies exist under `state\sessions`, `state\projects`, `state\history`, and `state\shell-snapshots`; `migration-summary.json` lists warnings for any historical records that cannot be backfilled.

- [ ] **Step 3: Tighten the state validator to treat dangling references as warnings only**

Update `C:\Users\huibozi\.claude\scripts\decl_state\validate_state.py` so it:

```text
- loads IDs from generated/registries/*.registry.json
- scans state/sessions/*.json
- scans state/projects/index.json
- scans state/history/history.jsonl
- records warnings for unknown agent_id, skill_ids, connector_ids, command_id
- never exits non-zero only because of historical dangling references
```

- [ ] **Step 4: Write the operator guide for steady-state usage**

Create `C:\Users\huibozi\.claude\CLAUDE-DECL-STATE.md` with these sections:

```markdown
# Claude Decl-State Workflow

## Edit Rules
- Edit only `decl/`
- Never hand-edit `generated/`
- Assume top-level legacy files are mirrors

## Validation Commands
- `python C:\Users\huibozi\.claude\scripts\decl_state\validate_decl.py`
- `python C:\Users\huibozi\.claude\scripts\decl_state\validate_state.py`
- `python C:\Users\huibozi\.claude\scripts\decl_state\validate_full.py`

## Mirror Commands
- `python C:\Users\huibozi\.claude\scripts\decl_state\mirror_decl.py --check-drift`
- `python C:\Users\huibozi\.claude\scripts\decl_state\mirror_decl.py --write`

## Snapshot And Cleanup Rules
- `generated/registries/` and `generated/reports/` are overwritten on every full validate
- `generated/snapshots/` keeps the newest five files
```

- [ ] **Step 5: Run the full validation gate**

Run:

```powershell
python C:\Users\huibozi\.claude\scripts\decl_state\validate_full.py
Get-Content C:\Users\huibozi\.claude\generated\reports\decl-health.json
Get-Content C:\Users\huibozi\.claude\generated\reports\state-health.json
Get-Content C:\Users\huibozi\.claude\generated\reports\mirror-drift.json
Get-Content C:\Users\huibozi\.claude\generated\reports\migration-summary.json
```

Expected:

```text
decl-health.json -> status pass
state-health.json -> warnings allowed, no hard errors caused only by historical drift
mirror-drift.json -> empty or warning-only drift list after mirror write
migration-summary.json -> includes import counts plus unmapped historical record warnings
```

## Self-Review

### Spec coverage

- `decl/`, `state/`, `generated/` bootstrap: Task 1
- declaration schemas and locked field names (`compute_profile`, `id`, `pipeline`, `priority`, `env_policy`): Task 2
- agents, commands, rules canonical import: Task 3
- MCP canonicalization and root config compatibility: Task 4
- skills inventory-first migration with managed first cohort: Task 5
- registry and snapshot ordering (`registry -> snapshot -> backfill`): Task 6
- one-way compatibility mirror and drift warnings: Task 7
- state import, `decl_generation` backfill, and warning-only historical drift handling: Task 8

### Placeholder scan

- No `TODO`
- No `TBD`
- No unnamed files
- No unspecified commands

### Type consistency

- Skills use `id` as the unique identifier; `name` is optional display metadata only.
- Agents use `compute_profile`, not `effort`.
- Commands use `pipeline`, not `workflow`.
- Policies include `priority`.
- Registries receive `decl_generation` only after the snapshot builder computes it.
