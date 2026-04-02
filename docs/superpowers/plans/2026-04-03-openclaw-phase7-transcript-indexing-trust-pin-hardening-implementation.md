# OpenClaw Phase 7 Transcript Indexing + Trust Pin Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the last two structural audit gaps in the live `C:\Users\huibozi\.openclaw` runtime by indexing handoff transcripts into the canonical session index and pinning plugin trust with an explicit `plugins.allow` allowlist.

**Architecture:** Keep the Phase 1-6 declaration/runtime split intact and make only narrow hardening changes. Extend `state/sessions/index.json` so it indexes both regular agent sessions and `agent/sessions/handoff-*.jsonl` transcripts with an explicit `session_kind`, then harden plugin trust by adding an explicit `plugins.allow` allowlist that includes every currently enabled plugin instead of only `handoff-bridge`.

**Tech Stack:** OpenClaw runtime JSONC config, Python 3.11, PowerShell 7+, OpenClaw CLI, JSON Schema-backed validators, live runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `decl/`, `state/`, and `generated/` remain the canonical layering model.
- `decl/handoffs/*/handoff.json` remains read-only fact source.
- `state/handoff-events/events.jsonl` remains append-only audit output.
- `memory/*.sqlite` remains untouched.
- `validate_full_openclaw.py` may still return `2` because older accepted Phase 5 events are missing `context_hash`; that is expected historical warning, not a Phase 7 failure.
- `plugins.allow` is an allowlist, so once it is non-empty it must contain all currently trusted active plugin ids:
  - `feishu`
  - `telegram`
  - `minimax`
  - `handoff-bridge`
- Config changes require `openclaw gateway restart` after editing `openclaw.json`.

## Deliverables

- `state/sessions/index.json` indexes `handoff-*.jsonl` runtime transcripts with `session_kind: "handoff"`
- `validate_state_openclaw.py` checks that handoff transcripts are indexed
- `openclaw.json` includes explicit `plugins.allow`
- `openclaw plugins inspect handoff-bridge --json` no longer reports the trust/provenance warning for `handoff-bridge`
- `OPENCLAW-DECL-STATE.md` documents transcript-index and trust-pin maintenance

## File Map

**Runtime indexing and validation**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py`

**Runtime config hardening**
- Modify `C:\Users\huibozi\.openclaw\openclaw.json`

**Docs**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

## Task 1: Index Handoff Transcripts In The Canonical Session Index

**Files:**
- Create: `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py`
- Modify: `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify: `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`

- [ ] **Step 1: Create a backup checkpoint for the state-indexing files**

```powershell
$stamp = Get-Date -Format 'yyyyMMddTHHmmssZ'
$backup = "C:\Users\huibozi\.openclaw\backups\decl-state\phase7-$stamp"
New-Item -ItemType Directory -Path $backup -Force | Out-Null
Copy-Item C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py $backup
Copy-Item C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py $backup
```

- [ ] **Step 2: Write the failing runtime-hardening test**

Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py`:

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(r"C:\Users\huibozi\.openclaw")
sys.path.insert(0, str(ROOT / "scripts" / "decl_state"))

from common import read_jsonc


class Phase7TranscriptIndexingTests(unittest.TestCase):
    def test_handoff_transcript_is_indexed_with_session_kind(self) -> None:
        payload = read_jsonc(ROOT / "state" / "sessions" / "index.json")
        entries = payload.get("entries", [])
        target = next(
            (
                entry
                for entry in entries
                if entry.get("session_id") == "handoff:daily-to-research:2026-04-02T17-12-32-303Z"
            ),
            None,
        )
        self.assertIsNotNone(target)
        self.assertEqual(target.get("session_kind"), "handoff")
        self.assertTrue(str(target.get("source_path", "")).endswith("handoff-daily-to-research-2026-04-02T17-12-32-303Z.jsonl"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the test and state validation to confirm the gap is real**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
```

Expected: the new test fails because the handoff transcript is not yet in `state/sessions/index.json`; `validate_state_openclaw.py` may still return `2` because of historical `context_hash` warnings.

- [ ] **Step 4: Extend the session rebuild logic to index handoff transcripts explicitly**

Update `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py` with a dedicated helper and dual scan:

```python
def _session_id_from_runtime_file(path):
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        payload = json.loads(first_line)
        return payload.get("id") or path.stem
    except Exception:
        return path.stem


def session_entries() -> list[dict]:
    entries = []
    if not AGENTS_ROOT.exists():
        return entries
    for agent_dir in sorted(AGENTS_ROOT.iterdir()):
        regular_root = agent_dir / "sessions"
        runtime_handoff_root = agent_dir / "agent" / "sessions"

        if regular_root.exists():
            for path in sorted(regular_root.glob("*.jsonl")):
                stat = path.stat()
                entries.append(
                    {
                        "session_id": path.stem,
                        "agent_id": agent_dir.name,
                        "source_path": str(path),
                        "started_at": None,
                        "updated_at": mtime_utc(path),
                        "size": stat.st_size,
                        "session_kind": "regular",
                    }
                )

        if runtime_handoff_root.exists():
            for path in sorted(runtime_handoff_root.glob("handoff-*.jsonl")):
                stat = path.stat()
                entries.append(
                    {
                        "session_id": _session_id_from_runtime_file(path),
                        "agent_id": agent_dir.name,
                        "source_path": str(path),
                        "started_at": None,
                        "updated_at": mtime_utc(path),
                        "size": stat.st_size,
                        "session_kind": "handoff",
                    }
                )
    return entries
```

Update `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py` so it validates `session_kind` and confirms handoff transcripts are indexed:

```python
handoff_sessions = [entry for entry in entries if entry.get("session_kind") == "handoff"]
for entry in entries:
    if entry.get("session_kind") not in {"regular", "handoff"}:
        errors.append(f"invalid session_kind for session {entry.get('session_id')}: {entry.get('session_kind')}")
for entry in handoff_sessions:
    source_path = str(entry.get("source_path", ""))
    if "agent\\sessions\\handoff-" not in source_path:
        errors.append(f"handoff session indexed from unexpected path: {source_path}")
    if not str(entry.get("session_id", "")).startswith("handoff:"):
        warnings.append(f"handoff session missing logical handoff session id: {entry.get('source_path')}")
if not handoff_sessions:
    warnings.append("no handoff transcripts indexed in state/sessions/index.json")
```

- [ ] **Step 5: Rebuild state indexes and re-run the test**

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
```

Expected: the test passes; `state/sessions/index.json` contains the known handoff transcript with `session_kind: "handoff"`; `validate_state_openclaw.py` still may return `2` only because of old Phase 5 `context_hash` warnings.

## Task 2: Pin Plugin Trust With An Explicit Allowlist

**Files:**
- Modify: `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py`
- Modify: `C:\Users\huibozi\.openclaw\openclaw.json`

- [ ] **Step 1: Extend the same test file with a failing trust-pin assertion**

Append to `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py`:

```python
class Phase7TrustPinTests(unittest.TestCase):
    def test_plugins_allow_pins_all_currently_enabled_plugins(self) -> None:
        payload = read_jsonc(ROOT / "openclaw.json")
        allow = payload.get("plugins", {}).get("allow", [])
        self.assertEqual(set(allow), {"feishu", "telegram", "minimax", "handoff-bridge"})
```

- [ ] **Step 2: Run the test and inspect the plugin to capture the current warning**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py -v
openclaw plugins inspect handoff-bridge --json
```

Expected: the Python test fails because `plugins.allow` is empty; inspect output contains the trust/provenance warning for `handoff-bridge`.

- [ ] **Step 3: Add an explicit `plugins.allow` list without accidentally disabling the other live plugins**

Edit the `plugins` block in `C:\Users\huibozi\.openclaw\openclaw.json` to this shape:

```json
"plugins": {
  "allow": [
    "feishu",
    "telegram",
    "minimax",
    "handoff-bridge"
  ],
  "entries": {
    "feishu": {
      "enabled": true
    },
    "telegram": {
      "enabled": true
    },
    "minimax": {
      "enabled": true
    },
    "handoff-bridge": {
      "enabled": true
    }
  }
}
```

- [ ] **Step 4: Restart the gateway and confirm the trust warning is gone**

Run:

```powershell
openclaw gateway restart
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py -v
openclaw plugins inspect handoff-bridge --json
```

Expected:
- the Python test passes
- inspect no longer reports either of these trust messages:
  - `loaded without install/load-path provenance`
  - `plugins.allow is empty`
- unrelated warnings, such as a channel secret warning from another plugin, may still appear and do not fail this task

## Task 3: Update The Operator Guide And Run Final Verification

**Files:**
- Modify: `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`
- Modify: `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py` only if the new session-index validation requires a summary line change

- [ ] **Step 1: Document the new transcript-index and trust-pin rules**

Append a short Phase 7 section to `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`:

```markdown
## Phase 7 transcript indexing and trust pin maintenance
- `state/sessions/index.json` must index both `agents/*/sessions/*.jsonl` and `agents/*/agent/sessions/handoff-*.jsonl`.
- `session_kind` must be `regular` or `handoff`.
- Handoff transcript entries must preserve the logical `handoff:*` session id from the runtime file header, not only the sanitized filename.
- `plugins.allow` must explicitly list every trusted enabled plugin id.
- When `plugins.allow` changes, run `openclaw gateway restart` before validation.
```

- [ ] **Step 2: Run the final fresh verification bundle**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase7_runtime_hardening.py -v
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase6_shared_context.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
openclaw plugins inspect handoff-bridge --json
```

Expected:
- `test_phase7_runtime_hardening.py`: PASS
- plugin Node tests: PASS
- Phase 6 shared-context tests: PASS
- `validate_full_openclaw.py`: `0` or `2`
- if `validate_full_openclaw.py` returns `2`, the remaining warnings should still be the known historical Phase 5 `context_hash` gaps, not transcript-index or trust-pin failures
- inspect output contains no trust-provenance warning for `handoff-bridge`

- [ ] **Step 3: Verify the indexed handoff transcript entry and the trust-pin outcome explicitly**

Run:

```powershell
@'
import json
from pathlib import Path
root = Path(r"C:\Users\huibozi\.openclaw")
payload = json.loads((root / "state" / "sessions" / "index.json").read_text(encoding="utf-8"))
entry = next(
    item for item in payload["entries"]
    if item.get("session_id") == "handoff:daily-to-research:2026-04-02T17-12-32-303Z"
)
print(entry["session_kind"])
print(entry["source_path"])
'@ | python -
```

Expected output:
- first line: `handoff`
- second line ends with `agents\research\agent\sessions\handoff-daily-to-research-2026-04-02T17-12-32-303Z.jsonl`

## Self-Review Checklist

- Spec coverage: Task 1 covers transcript indexing, Task 2 covers trust pinning, Task 3 covers final validation and operator guide updates.
- Placeholder scan: no `TBD`, `TODO`, or abstract `handle appropriately` instructions remain.
- Type consistency: `session_kind` uses only `regular | handoff`; `plugins.allow` carries plugin ids, not file paths.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-03-openclaw-phase7-transcript-indexing-trust-pin-hardening-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
