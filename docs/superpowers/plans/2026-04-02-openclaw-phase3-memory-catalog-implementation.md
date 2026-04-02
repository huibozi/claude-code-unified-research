# OpenClaw Phase 3 Memory Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add canonical OpenClaw memory surface declarations, agent-to-memory mounts, and memory access policy so the live file-based memory and sqlite index layers become schema-validated, cross-referenced, and auditable without mutating live sqlite or workspace content.

**Architecture:** Keep live runtime memory roots in place and extend only the canonical declaration layer under `decl/`, the metadata-only indexes under `state/`, and the generated registries, reports, and snapshots under `generated/`. Phase 3 does not invent a new core runtime concept; it implements the existing unified `Memory` object for OpenClaw by cataloging live file-store and sqlite-index surfaces, then attaching explicit `memory_refs[]` and `policy_refs[]` so access boundaries are visible and verifiable.

**Tech Stack:** PowerShell 7+, Python 3.11, `json`, `jsonschema`, `sqlite3`, JSON Schema Draft 2020-12, Markdown, live OpenClaw runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `C:\Users\huibozi\.openclaw\openclaw.json` remains the live runtime config and compatibility surface.
- `C:\Users\huibozi\.openclaw\memory\main.sqlite` and `C:\Users\huibozi\.openclaw\memory\research.sqlite` remain in place and stay metadata-indexed only.
- `C:\Users\huibozi\.openclaw\workspace*\memory\*` and `C:\Users\huibozi\.openclaw\workspace*\.learnings\*` remain the live file-memory source; Phase 3 catalogs them but does not rewrite them.
- `C:\Users\huibozi\.openclaw\agents\*\sessions\*.jsonl` remain the live transcript source; `state\sessions\index.json` stays metadata-only.
- Existing routing policies under `decl\rules\` remain valid; Phase 3 adds memory-access policy beside them instead of reshaping them.
- Validation order stays locked as `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`.
- Exit codes remain `0 = pass`, `1 = error`, `2 = warn`.

## Phase 3 Deliverables

- `decl\memory\` with nine canonical memory surface declarations
- `agent.json` with `memory_refs[]` as the fact source and `memory_scope` upgraded to support `mixed`
- Five explicit memory-access policies under `decl\rules\`
- `state\indexes\memory\index.json` upgraded from sqlite-only metadata to a combined catalog view that also reports file-store roots without reading file content
- `generated\registries\memory.registry.json`, bringing generated registry count from `10` to `11`
- Cross-reference validation for:
  - `agent.memory_refs[] -> memory.registry`
  - `memory.policy_refs[] -> rules.registry`
  - `memory.reader_refs[] / writer_refs[] / shared_with[] -> agents.registry`
  - memory-access policy `readers[] / writers[] / shared_with[] / rebuild_rights[] -> agents.registry`

## Files To Modify

**Canonical declaration data**
- Create `C:\Users\huibozi\.openclaw\decl\memory\<id>\memory.json`
- Modify `C:\Users\huibozi\.openclaw\decl\agents\*\agent.json`
- Modify `C:\Users\huibozi\.openclaw\decl\rules\*\policy.json`

**Schemas**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\memory.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\agent.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\policy.schema.json`

**Import and validation scripts**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_memory_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\build_sensitive_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\build_registries_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`

**Tests**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py`

**Documentation**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

## Target Shapes

**Memory surface**

```json
{
  "id": "research-store",
  "description": "Research-domain sqlite retrieval index for research/profit memory.",
  "kind": "sqlite-index",
  "store_kind": "retrieval",
  "source_roots": [
    "C:\\Users\\huibozi\\.openclaw\\workspace-research\\memory",
    "C:\\Users\\huibozi\\.openclaw\\workspace-research\\.learnings"
  ],
  "sqlite_path": "C:\\Users\\huibozi\\.openclaw\\memory\\research.sqlite",
  "indexing_mode": "manual",
  "reader_refs": ["research", "profit"],
  "writer_refs": ["research", "profit"],
  "shared_with": ["profit"],
  "policy_refs": ["research-domain-access"],
  "retention": {
    "max_age_days": 365,
    "max_entries": 5000,
    "compaction": "manual"
  },
  "_adapter_notes": {
    "schema_family": "chunks-fts-embedding-cache",
    "runtime_role": "index-layer"
  }
}
```

**Agent memory attachment**

```json
{
  "id": "daily",
  "memory_scope": "mixed",
  "memory_refs": [
    "workspace-daily-files",
    "daily-learnings",
    "shared-learnings"
  ]
}
```

**Memory access policy**

```json
{
  "id": "shared-learnings-access",
  "description": "Shared learning surface is readable by every live agent but writable only by designated maintainers.",
  "scope": "memory:shared-learnings",
  "priority": 70,
  "readers": ["research", "profit", "daily", "main", "personal", "freya"],
  "writers": ["research", "daily", "personal"],
  "shared_with": ["research", "profit", "daily", "main", "personal", "freya"],
  "rebuild_rights": ["research", "main"],
  "retention": {
    "max_age_days": 3650,
    "max_entries": 10000,
    "compaction": "manual"
  },
  "audit_requirements": ["retain-memory-boundary-log"]
}
```

## Canonical Memory Surface Set

Phase 3 locks the first catalog to these nine surfaces:

- `main-store` -> `C:\Users\huibozi\.openclaw\memory\main.sqlite`
- `research-store` -> `C:\Users\huibozi\.openclaw\memory\research.sqlite`
- `workspace-main-files` -> `C:\Users\huibozi\.openclaw\workspace\memory`
- `workspace-research-files` -> `C:\Users\huibozi\.openclaw\workspace-research\memory`
- `workspace-daily-files` -> `C:\Users\huibozi\.openclaw\workspace-daily\memory`
- `research-learnings` -> `C:\Users\huibozi\.openclaw\workspace-research\.learnings`
- `daily-learnings` -> `C:\Users\huibozi\.openclaw\workspace-daily\.learnings`
- `personal-learnings` -> `C:\Users\huibozi\.openclaw\workspace-personal\.learnings`
- `shared-learnings` -> `C:\Users\huibozi\.openclaw\shared-learnings`

## Canonical Agent Memory Mapping

Phase 3 locks agent `memory_refs[]` to the live shape below:

- `research` -> `research-store`, `workspace-research-files`, `research-learnings`, `shared-learnings`
- `profit` -> `research-store`, `research-learnings`, `shared-learnings`
- `daily` -> `workspace-daily-files`, `daily-learnings`, `shared-learnings`
- `main` -> `main-store`, `workspace-main-files`, `shared-learnings`
- `personal` -> `personal-learnings`, `shared-learnings`
- `freya` -> `personal-learnings`, `shared-learnings`

`memory_scope` becomes a summary field only:

- `research`, `profit`, `daily`, `main` -> `mixed`
- `personal`, `freya` -> `shared`

## Task 1: Add Memory Surface Schema And Test Scaffold

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\memory.schema.json`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py`

- [ ] Add `memory.schema.json` with the minimum surface shape and cross-runtime-neutral field names.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "id",
    "description",
    "kind",
    "store_kind",
    "source_roots",
    "indexing_mode",
    "reader_refs",
    "writer_refs",
    "shared_with",
    "policy_refs",
    "retention"
  ],
  "properties": {
    "id": {"type": "string", "minLength": 1},
    "description": {"type": "string"},
    "kind": {"type": "string", "enum": ["file-store", "sqlite-index", "hybrid"]},
    "store_kind": {"type": "string", "enum": ["retrieval", "kv", "append-log"]},
    "source_roots": {"type": "array", "items": {"type": "string"}},
    "sqlite_path": {"type": "string"},
    "indexing_mode": {"type": "string", "enum": ["manual", "auto", "scheduled"]},
    "reader_refs": {"type": "array", "items": {"type": "string"}},
    "writer_refs": {"type": "array", "items": {"type": "string"}},
    "shared_with": {"type": "array", "items": {"type": "string"}},
    "policy_refs": {"type": "array", "items": {"type": "string"}},
    "retention": {
      "type": "object",
      "required": ["max_age_days", "max_entries", "compaction"],
      "properties": {
        "max_age_days": {"type": "integer", "minimum": 1},
        "max_entries": {"type": "integer", "minimum": 1},
        "compaction": {"type": "string", "enum": ["manual", "auto"]}
      }
    },
    "_adapter_notes": {"type": "object"}
  }
}
```

- [ ] Add a focused unittest that validates one sqlite-index surface and one file-store surface against the new schema.

```python
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(r"C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\memory.schema.json")


class MemorySchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.schema)

    def test_sqlite_surface_is_valid(self) -> None:
        payload = {
            "id": "research-store",
            "description": "Research sqlite index",
            "kind": "sqlite-index",
            "store_kind": "retrieval",
            "source_roots": [r"C:\Users\huibozi\.openclaw\workspace-research\memory"],
            "sqlite_path": r"C:\Users\huibozi\.openclaw\memory\research.sqlite",
            "indexing_mode": "manual",
            "reader_refs": ["research", "profit"],
            "writer_refs": ["research", "profit"],
            "shared_with": ["profit"],
            "policy_refs": ["research-domain-access"],
            "retention": {"max_age_days": 365, "max_entries": 5000, "compaction": "manual"},
        }
        self.validator.validate(payload)

    def test_file_surface_is_valid(self) -> None:
        payload = {
            "id": "daily-learnings",
            "description": "Daily learnings files",
            "kind": "file-store",
            "store_kind": "append-log",
            "source_roots": [r"C:\Users\huibozi\.openclaw\workspace-daily\.learnings"],
            "indexing_mode": "manual",
            "reader_refs": ["daily"],
            "writer_refs": ["daily"],
            "shared_with": [],
            "policy_refs": ["daily-domain-access"],
            "retention": {"max_age_days": 3650, "max_entries": 5000, "compaction": "manual"},
        }
        self.validator.validate(payload)
```

- [ ] Run the new test file before touching importers.

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py -v
```

Expected: both tests pass and prove the schema is syntactically usable.

## Task 2: Import The Nine Canonical Memory Surfaces

**Files:**
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\import_memory_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\decl\memory\<id>\memory.json`

- [ ] Write `import_memory_openclaw.py` with one deterministic constructor per surface so the live mapping is explicit instead of inferred.

```python
from pathlib import Path

from common import DECL_ROOT, OPENCLAW_ROOT, utc_now, write_json

MEMORY_SURFACES = [
    {
        "id": "main-store",
        "description": "Primary sqlite retrieval index for the main OpenClaw domain.",
        "kind": "sqlite-index",
        "store_kind": "retrieval",
        "source_roots": [str(OPENCLAW_ROOT / "workspace" / "memory")],
        "sqlite_path": str(OPENCLAW_ROOT / "memory" / "main.sqlite"),
        "indexing_mode": "manual",
        "reader_refs": ["main"],
        "writer_refs": ["main"],
        "shared_with": [],
        "policy_refs": ["main-domain-access"],
        "retention": {"max_age_days": 365, "max_entries": 5000, "compaction": "manual"},
        "_adapter_notes": {"schema_family": "chunks-fts-embedding-cache", "runtime_role": "index-layer"},
    },
    {
        "id": "research-store",
        "description": "Research-domain sqlite retrieval index for research and profit.",
        "kind": "sqlite-index",
        "store_kind": "retrieval",
        "source_roots": [
            str(OPENCLAW_ROOT / "workspace-research" / "memory"),
            str(OPENCLAW_ROOT / "workspace-research" / ".learnings"),
        ],
        "sqlite_path": str(OPENCLAW_ROOT / "memory" / "research.sqlite"),
        "indexing_mode": "manual",
        "reader_refs": ["research", "profit"],
        "writer_refs": ["research", "profit"],
        "shared_with": ["profit"],
        "policy_refs": ["research-domain-access"],
        "retention": {"max_age_days": 365, "max_entries": 5000, "compaction": "manual"},
        "_adapter_notes": {"schema_family": "chunks-fts-embedding-cache", "runtime_role": "index-layer"},
    },
    {
        "id": "workspace-main-files",
        "description": "Primary workspace file-memory store for the main agent.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "workspace" / "memory")],
        "indexing_mode": "manual",
        "reader_refs": ["main"],
        "writer_refs": ["main"],
        "shared_with": [],
        "policy_refs": ["main-domain-access"],
        "retention": {"max_age_days": 180, "max_entries": 2000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "live-file-memory"},
    },
    {
        "id": "workspace-research-files",
        "description": "Research workspace file-memory store.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "workspace-research" / "memory")],
        "indexing_mode": "manual",
        "reader_refs": ["research"],
        "writer_refs": ["research"],
        "shared_with": ["profit"],
        "policy_refs": ["research-domain-access"],
        "retention": {"max_age_days": 180, "max_entries": 3000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "live-file-memory"},
    },
    {
        "id": "workspace-daily-files",
        "description": "Daily workspace file-memory store.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "workspace-daily" / "memory")],
        "indexing_mode": "manual",
        "reader_refs": ["daily"],
        "writer_refs": ["daily"],
        "shared_with": [],
        "policy_refs": ["daily-domain-access"],
        "retention": {"max_age_days": 180, "max_entries": 3000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "live-file-memory"},
    },
    {
        "id": "research-learnings",
        "description": "Research-domain learnings shared by research and profit.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "workspace-research" / ".learnings")],
        "indexing_mode": "manual",
        "reader_refs": ["research", "profit"],
        "writer_refs": ["research", "profit"],
        "shared_with": ["profit"],
        "policy_refs": ["research-domain-access"],
        "retention": {"max_age_days": 3650, "max_entries": 5000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "learnings-log"},
    },
    {
        "id": "daily-learnings",
        "description": "Daily agent learnings log.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "workspace-daily" / ".learnings")],
        "indexing_mode": "manual",
        "reader_refs": ["daily"],
        "writer_refs": ["daily"],
        "shared_with": [],
        "policy_refs": ["daily-domain-access"],
        "retention": {"max_age_days": 3650, "max_entries": 5000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "learnings-log"},
    },
    {
        "id": "personal-learnings",
        "description": "Personal workspace learnings shared by personal and freya.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "workspace-personal" / ".learnings")],
        "indexing_mode": "manual",
        "reader_refs": ["personal", "freya"],
        "writer_refs": ["personal", "freya"],
        "shared_with": ["freya"],
        "policy_refs": ["personal-domain-access"],
        "retention": {"max_age_days": 3650, "max_entries": 5000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "learnings-log"},
    },
    {
        "id": "shared-learnings",
        "description": "Cross-agent learnings hub readable across OpenClaw agents.",
        "kind": "file-store",
        "store_kind": "append-log",
        "source_roots": [str(OPENCLAW_ROOT / "shared-learnings")],
        "indexing_mode": "manual",
        "reader_refs": ["research", "profit", "daily", "main", "personal", "freya"],
        "writer_refs": ["research", "daily", "personal"],
        "shared_with": ["research", "profit", "daily", "main", "personal", "freya"],
        "policy_refs": ["shared-learnings-access"],
        "retention": {"max_age_days": 3650, "max_entries": 10000, "compaction": "manual"},
        "_adapter_notes": {"runtime_role": "shared-learning-hub"},
    },
]
```

- [ ] Add all nine entries, including the three learnings surfaces and `shared-learnings`, then write each one to `decl\memory\<id>\memory.json`.

```python
def write_surface(payload: dict[str, object]) -> None:
    write_json(DECL_ROOT / "memory" / payload["id"] / "memory.json", {**payload, "_imported_at": utc_now()})

for payload in MEMORY_SURFACES:
    write_surface(payload)
```

- [ ] Run the importer and inspect the directory.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_memory_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\memory
Get-Content C:\Users\huibozi\.openclaw\decl\memory\research-store\memory.json
```

Expected: nine child directories exist and `research-store` shows `sqlite_path`, `source_roots`, `policy_refs`, and `reader_refs`.

## Task 3: Attach Memory Refs To Agents

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\agent.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\agents\*\agent.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py`

- [ ] Extend `agent.schema.json` so `memory_scope` becomes a bounded summary and `memory_refs[]` is first-class.

```json
{
  "required": [
    "id",
    "description",
    "model",
    "compute_profile",
    "tools",
    "skills",
    "permission_mode",
    "memory_scope",
    "memory_refs",
    "isolation",
    "max_turns",
    "required_mcp_servers"
  ],
  "properties": {
    "memory_scope": {"type": "string", "enum": ["session", "project", "shared", "mixed", "none"]},
    "memory_refs": {"type": "array", "items": {"type": "string"}}
  }
}
```

- [ ] Add a single mapping table in `import_agents_openclaw.py` and stamp every imported/discovered agent from that table.

```python
MEMORY_MAP = {
    "research": {"memory_scope": "mixed", "memory_refs": ["research-store", "workspace-research-files", "research-learnings", "shared-learnings"]},
    "profit": {"memory_scope": "mixed", "memory_refs": ["research-store", "research-learnings", "shared-learnings"]},
    "daily": {"memory_scope": "mixed", "memory_refs": ["workspace-daily-files", "daily-learnings", "shared-learnings"]},
    "main": {"memory_scope": "mixed", "memory_refs": ["main-store", "workspace-main-files", "shared-learnings"]},
    "personal": {"memory_scope": "shared", "memory_refs": ["personal-learnings", "shared-learnings"]},
    "freya": {"memory_scope": "shared", "memory_refs": ["personal-learnings", "shared-learnings"]},
}
```

```python
memory_fields = MEMORY_MAP.get(agent_id, {"memory_scope": "none", "memory_refs": []})
```

- [ ] Extend the unittest file with one regression test that checks a mixed agent and a shared agent.

```python
    def test_research_agent_memory_shape(self) -> None:
        payload = json.loads(Path(r"C:\Users\huibozi\.openclaw\decl\agents\research\agent.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["memory_scope"], "mixed")
        self.assertIn("research-store", payload["memory_refs"])

    def test_freya_agent_memory_shape(self) -> None:
        payload = json.loads(Path(r"C:\Users\huibozi\.openclaw\decl\agents\freya\agent.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["memory_scope"], "shared")
        self.assertEqual(payload["memory_refs"], ["personal-learnings", "shared-learnings"])
```

- [ ] Re-import agents and run the tests.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py -v
Get-Content C:\Users\huibozi\.openclaw\decl\agents\research\agent.json
```

Expected: all six agents have `memory_refs[]` and only `personal` plus `freya` report `memory_scope = shared`.

## Task 4: Add Memory Access Policies And Attach Them To Surfaces

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\policy.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\decl\rules\research-domain-access\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\main-domain-access\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\daily-domain-access\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\personal-domain-access\policy.json`
- Create `C:\Users\huibozi\.openclaw\decl\rules\shared-learnings-access\policy.json`

- [ ] Extend `policy.schema.json` with the memory-access fields without breaking existing routing policies.

```json
{
  "properties": {
    "readers": {"type": "array", "items": {"type": "string"}},
    "writers": {"type": "array", "items": {"type": "string"}},
    "shared_with": {"type": "array", "items": {"type": "string"}},
    "rebuild_rights": {"type": "array", "items": {"type": "string"}},
    "retention": {
      "type": "object",
      "properties": {
        "max_age_days": {"type": "integer"},
        "max_entries": {"type": "integer"},
        "compaction": {"type": "string", "enum": ["manual", "auto"]}
      }
    }
  }
}
```

- [ ] Extend `import_rules_openclaw.py` with five deterministic memory-access policies instead of folding memory semantics into the old routing policies.

```python
MEMORY_POLICIES = [
    {
        "id": "research-domain-access",
        "description": "Research and profit share the research memory domain.",
        "scope": "memory:research-store",
        "priority": 80,
        "readers": ["research", "profit"],
        "writers": ["research", "profit"],
        "shared_with": ["profit"],
        "rebuild_rights": ["research"],
        "retention": {"max_age_days": 365, "max_entries": 5000, "compaction": "manual"},
        "audit_requirements": ["retain-memory-boundary-log"],
    },
    {
        "id": "main-domain-access",
        "description": "Main-domain memory is writable only by main and not shared into the personal domain.",
        "scope": "memory:main-store",
        "priority": 80,
        "readers": ["main"],
        "writers": ["main"],
        "shared_with": [],
        "rebuild_rights": ["main"],
        "retention": {"max_age_days": 365, "max_entries": 5000, "compaction": "manual"},
        "audit_requirements": ["retain-memory-boundary-log"],
    },
    {
        "id": "daily-domain-access",
        "description": "Daily memory stays inside the daily workspace boundary.",
        "scope": "agent:daily",
        "priority": 80,
        "readers": ["daily"],
        "writers": ["daily"],
        "shared_with": [],
        "rebuild_rights": ["daily"],
        "retention": {"max_age_days": 365, "max_entries": 5000, "compaction": "manual"},
        "audit_requirements": ["retain-memory-boundary-log"],
    },
    {
        "id": "personal-domain-access",
        "description": "Personal workspace learnings are shared only between personal and freya.",
        "scope": "agent:personal",
        "priority": 80,
        "readers": ["personal", "freya"],
        "writers": ["personal", "freya"],
        "shared_with": ["freya"],
        "rebuild_rights": ["personal"],
        "retention": {"max_age_days": 3650, "max_entries": 5000, "compaction": "manual"},
        "audit_requirements": ["retain-memory-boundary-log"],
    },
    {
        "id": "shared-learnings-access",
        "description": "Shared learnings are readable across agents under explicit write control.",
        "scope": "memory:shared-learnings",
        "priority": 70,
        "readers": ["research", "profit", "daily", "main", "personal", "freya"],
        "writers": ["research", "daily", "personal"],
        "shared_with": ["research", "profit", "daily", "main", "personal", "freya"],
        "rebuild_rights": ["research", "main"],
        "retention": {"max_age_days": 3650, "max_entries": 10000, "compaction": "manual"},
        "audit_requirements": ["retain-memory-boundary-log"],
    },
]
```

- [ ] Update memory surface import or a post-processing step so each surface gets the correct `policy_refs[]`.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py
Get-ChildItem C:\Users\huibozi\.openclaw\decl\rules
Get-Content C:\Users\huibozi\.openclaw\decl\rules\shared-learnings-access\policy.json
Get-Content C:\Users\huibozi\.openclaw\decl\memory\shared-learnings\memory.json
```

Expected: five new memory policies exist and `shared-learnings\memory.json` references `shared-learnings-access`.

## Task 5: Upgrade Memory State Indexes Without Reading Content

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\build_sensitive_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`

- [ ] Extend `build_sensitive_indexes_openclaw.py` so the memory index reports both sqlite metadata and file-root summaries.

```python
def file_root_summary(root: Path) -> dict[str, object]:
    files = sorted(path for path in root.rglob("*") if path.is_file()) if root.exists() else []
    total_size = sum(path.stat().st_size for path in files)
    return {
        "root": str(root),
        "exists": root.exists(),
        "file_count": len(files),
        "total_size": total_size,
    }
```

```python
memory = {
    "sqlite_entries": sqlite_entries(memory_root),
    "file_roots": [
        file_root_summary(OPENCLAW_ROOT / "workspace" / "memory"),
        file_root_summary(OPENCLAW_ROOT / "workspace-research" / "memory"),
        file_root_summary(OPENCLAW_ROOT / "workspace-daily" / "memory"),
        file_root_summary(OPENCLAW_ROOT / "workspace-research" / ".learnings"),
        file_root_summary(OPENCLAW_ROOT / "workspace-daily" / ".learnings"),
        file_root_summary(OPENCLAW_ROOT / "workspace-personal" / ".learnings"),
        file_root_summary(OPENCLAW_ROOT / "shared-learnings"),
    ],
}
```

- [ ] Update `validate_state_openclaw.py` so the report surfaces file-root coverage without trying to parse file contents.

```python
memory_index = read_json(STATE_ROOT / "indexes" / "memory" / "index.json")
file_roots = memory_index.get("file_roots", [])
if not file_roots:
    errors.append("expected non-empty memory file_roots metadata")
```

- [ ] Run the index builder and inspect the output.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\build_sensitive_indexes_openclaw.py
Get-Content C:\Users\huibozi\.openclaw\state\indexes\memory\index.json
```

Expected: `index.json` contains `sqlite_entries` and `file_roots`, and each root reports only file count, size, and existence.

## Task 6: Add Memory Cross-Reference Validation And The Eleventh Registry

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\build_registries_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py`

- [ ] Add `memory` to both declaration maps.

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
}
```

```python
FILENAME_MAP = {
    "memory": "memory.json",
}
```

- [ ] Extend `validate_decl_openclaw.py` with the memory cross-checks after schema validation.

```python
memory_ids = ids_seen["memory"]

for json_path, payload in payloads_seen["agents"]:
    for ref in payload.get("memory_refs", []):
        if ref not in memory_ids:
            errors.append(f"{json_path}: unknown memory_ref {ref}")

for json_path, payload in payloads_seen["memory"]:
    for ref in payload.get("policy_refs", []):
        if ref not in rule_ids:
            errors.append(f"{json_path}: unknown memory policy_ref {ref}")
    for ref_group in ("reader_refs", "writer_refs", "shared_with"):
        for ref in payload.get(ref_group, []):
            if ref not in agent_ids:
                errors.append(f"{json_path}: unknown {ref_group} agent {ref}")
```

- [ ] Add `memory` to `build_registries_openclaw.py` and bump full-validation expectations from `10` registries to `11`.

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
}
```

```python
if len(registry_paths) != 11:
    errors.append(f"expected 11 registry files, found {len(registry_paths)}")
```

- [ ] Extend the unittest file with one negative check by constructing an invalid payload in memory and asserting schema failure or validator failure.

```python
    def test_memory_surface_requires_policy_refs(self) -> None:
        payload = {
            "id": "broken-surface",
            "description": "broken",
            "kind": "file-store",
            "store_kind": "append-log",
            "source_roots": [],
            "indexing_mode": "manual",
            "reader_refs": [],
            "writer_refs": [],
            "shared_with": [],
            "retention": {"max_age_days": 1, "max_entries": 1, "compaction": "manual"},
        }
        with self.assertRaises(Exception):
            self.validator.validate(payload)
```

- [ ] Run the tests and validators.

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase3_memory.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Expected: tests pass, validators exit `0` or `2`, and `validate_full_openclaw.py` expects `11` registries.

## Task 7: Rebuild Generated State And Update The Operator Guide

**Files:**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`
- Regenerate `C:\Users\huibozi\.openclaw\generated\registries\*.registry.json`
- Regenerate `C:\Users\huibozi\.openclaw\generated\reports\openclaw-*.json`
- Regenerate `C:\Users\huibozi\.openclaw\generated\snapshots\decl-*.json`

- [ ] Run the full Phase 3 import and validation pipeline from scratch.

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_memory_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_agents_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\import_rules_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\build_sensitive_indexes_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

- [ ] Add a dedicated maintenance section to `OPENCLAW-DECL-STATE.md` so future edits know the ownership boundaries.

```markdown
## Phase 3 Memory Maintenance

- `decl/memory/*/memory.json` owns canonical memory surfaces and policy attachments.
- `decl/agents/*/agent.json` owns `memory_refs[]`; `memory_scope` is summary-only.
- `decl/rules/*/policy.json` owns memory-access policy beside routing policy.
- `state/indexes/memory/index.json` stays metadata-only and must never read live file content or write sqlite.
- `memory/*.sqlite`, `workspace*/memory/*`, and `workspace*/.learnings/*` remain live runtime sources.
```

- [ ] Verify the generated layer meets the Phase 3 acceptance bar.

```powershell
Get-ChildItem C:\Users\huibozi\.openclaw\generated\registries
Get-Content C:\Users\huibozi\.openclaw\generated\reports\openclaw-full-validation.json
Get-Content C:\Users\huibozi\.openclaw\state\indexes\memory\index.json
```

Expected: `memory.registry.json` exists, total registries equal `11`, and the memory index includes `file_roots` plus sqlite metadata.

## Acceptance Checklist

- `validate_full_openclaw.py` exits `0` or `2`
- `decl\memory\` contains exactly nine surface declarations
- all six agents contain `memory_refs[]` and valid `memory_scope` values
- `decl\rules\` contains five new memory-access policies, bringing total rule count to eight
- every memory surface contains `policy_refs[]`
- `generated\registries\memory.registry.json` exists and total registry count is `11`
- `memory\main.sqlite` and `memory\research.sqlite` are not modified in place
- `state\indexes\memory\index.json` includes `file_roots` summaries without storing file contents

## Self-Review

- Spec coverage: the plan covers the locked Phase 3 requirements: nine memory surfaces, `memory_refs[]`, `mixed` scope, five memory-access policies, `policy_refs[]`, upgraded memory indexes, and the eleventh registry.
- Placeholder scan: no `TBD`, `TODO`, or deferred implementation language remains.
- Type consistency: `memory_refs`, `policy_refs`, `reader_refs`, `writer_refs`, `shared_with`, and `rebuild_rights` use the same names across tasks, target shapes, and acceptance criteria.
