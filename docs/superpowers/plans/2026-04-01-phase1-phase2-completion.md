# Phase 1 And Phase 2 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Complete the unified research repository baseline and the unified runtime specification so Phase 1 and Phase 2 can be treated as finished with verification evidence.

**Architecture:** Keep the repository source-free and evidence-driven. Phase 1 outputs live under provenance, manifests, indexes, and parity layers. Phase 2 outputs live under the source-derived spec layer with concepts, schemas, mappings, examples, and validation reports.

**Tech Stack:** Markdown, JSON Schema Draft 2020-12, Python 3.11 with `jsonschema`, Git, PowerShell

---

### Task 1: Complete Phase 1 Provenance And Manifest Artifacts

**Files:**
- Modify: `README.md`
- Modify: `04-diffs-and-indexes/provenance-index/provenance.md`
- Modify: `04-diffs-and-indexes/manifests/current-comparison-summary.md`
- Create: `04-diffs-and-indexes/manifests/source-baseline.manifest.md`
- Create: `04-diffs-and-indexes/manifests/source-leak.manifest.md`
- Create: `04-diffs-and-indexes/manifests/kuberwastaken.manifest.md`
- Create: `04-diffs-and-indexes/manifests/instructkr.manifest.md`
- Create: `04-diffs-and-indexes/structure-diffs/source-vs-source-leak.md`
- Create: `04-diffs-and-indexes/structure-diffs/source-vs-kuberwastaken.md`
- Create: `04-diffs-and-indexes/structure-diffs/source-vs-instructkr.md`
- Create: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`
- Create: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`

- [x] **Step 1: Inspect the four local source trees and capture file counts, line counts, top-level structure, and notable modules**

Run:

```powershell
@'
from pathlib import Path
repos = {
    "source": Path(r"C:\Users\huibozi\claude-code-source"),
    "source_leak": Path(r"C:\Users\huibozi\claude-code-source-leak"),
    "kuberwastaken": Path(r"C:\Users\huibozi\claude-code-forks\claude-code-Kuberwastaken"),
    "instructkr": Path(r"C:\Users\huibozi\claude-code-forks\claude-code-instructkr"),
}
exts = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".rs", ".md"}
for name, root in repos.items():
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    print(name, len(files))
    print(sorted(p.relative_to(root).parts[0] for p in files if p.relative_to(root).parts))
@ | python -
```

Expected: the command prints per-repository counts and top-level module surfaces that can be summarized into manifests.

- [x] **Step 2: Write the detailed Phase 1 manifests and structural diff documents**

Write markdown summaries that include:

```text
- provenance facts
- top-level directories
- approximate code scale
- dominant languages
- major module surfaces
- comparison notes against the primary source baseline
```

- [x] **Step 3: Update the provenance index and repository root README to reflect the completed research layout**

Add fields for:

```text
local path
upstream URL
commit
type
acquisition date
read-only policy
duplication status
publication status
notes
```

- [x] **Step 4: Verify Phase 1 file coverage**

Run:

```powershell
Get-ChildItem -Recurse -File .\04-diffs-and-indexes
Get-ChildItem -Recurse -File .\03-specs-and-parity\module-matrices
```

Expected: all manifest, diff, symbol-index, and capability-matrix files exist.

### Task 2: Author The Unified Runtime Spec Concepts

**Files:**
- Create: `03-specs-and-parity/source-derived-spec/README.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/runtime.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/session.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/agent.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/command.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/tool.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/skill.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/task.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/memory.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/connector.md`
- Create: `03-specs-and-parity/source-derived-spec/concepts/policy.md`

- [x] **Step 1: Create the source-derived spec README with object list, grouping, and document map**

Include:

```text
- purpose of the spec layer
- the ten core objects
- five module groups
- links to concepts, schemas, mappings, and examples
```

- [x] **Step 2: Write the ten concept documents with consistent sections**

Use the same headings in every concept file:

```text
Purpose
Core responsibilities
Required fields
Lifecycle or execution semantics
Relationships to other objects
Evidence from tracked repositories
Open parity notes
```

- [x] **Step 3: Cross-link concept files back to Phase 1 evidence**

Each concept should cite at least one relevant repository artifact from:

```text
04-diffs-and-indexes/manifests/
04-diffs-and-indexes/symbol-index/
03-specs-and-parity/module-matrices/
```

- [x] **Step 4: Verify concept coverage**

Run:

```powershell
Get-ChildItem .\03-specs-and-parity\source-derived-spec\concepts\*.md | Measure-Object | Select-Object -ExpandProperty Count
```

Expected: `10`

### Task 3: Add Schemas, Mappings, And Examples

**Files:**
- Create: `03-specs-and-parity/source-derived-spec/schemas/runtime.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/session.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/agent.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/command.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/tool.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/skill.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/task.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/memory.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/connector.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/schemas/policy.schema.json`
- Create: `03-specs-and-parity/source-derived-spec/mappings/source-to-spec.md`
- Create: `03-specs-and-parity/source-derived-spec/mappings/kuber-to-spec.md`
- Create: `03-specs-and-parity/source-derived-spec/mappings/instructkr-to-spec.md`
- Create: `03-specs-and-parity/source-derived-spec/examples/openclaw-agent.example.json`
- Create: `03-specs-and-parity/source-derived-spec/examples/codex-skill.example.json`
- Create: `03-specs-and-parity/source-derived-spec/examples/task-lifecycle.example.json`

- [x] **Step 1: Write Draft 2020-12 JSON Schemas for all ten objects**

Every schema should define:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://huibozi.github.io/claude-code-unified-research/<object>.schema.json",
  "type": "object",
  "required": ["..."],
  "properties": {}
}
```

- [x] **Step 2: Write mapping documents for source, Kuberwastaken, and instructkr**

Every mapping file should include a table with:

```text
Spec object
Observed implementation surface
Coverage level
Evidence
Notes
```

- [x] **Step 3: Write three schema-valid examples**

Use:

```text
openclaw-agent.example.json -> Agent schema
codex-skill.example.json -> Skill schema
task-lifecycle.example.json -> Task schema
```

- [x] **Step 4: Verify JSON syntax before schema validation**

Run:

```powershell
Get-ChildItem .\03-specs-and-parity\source-derived-spec\schemas\*.json | ForEach-Object { Get-Content -Raw $_ | ConvertFrom-Json | Out-Null }
Get-ChildItem .\03-specs-and-parity\source-derived-spec\examples\*.json | ForEach-Object { Get-Content -Raw $_ | ConvertFrom-Json | Out-Null }
```

Expected: no parse errors.

### Task 4: Add Verification Scripts, Reports, And Final Phase Gate Evidence

**Files:**
- Create: `06-verification/checks/verify_phase1_phase2.py`
- Modify: `06-verification/reports/research-repo-health.md`
- Create: `06-verification/reports/runtime-spec-health.md`
- Create: `06-verification/reports/mapping-coverage.md`
- Create: `06-verification/reports/parity-conflicts.md`
- Modify: `06-verification/README.md`

- [x] **Step 1: Write a verification script that checks required file presence and validates examples against schemas**

The script should:

```text
- assert all required markdown and json files exist
- assert there are 10 concept files
- parse all schema files as JSON
- parse all example files as JSON
- validate each example against its target schema with jsonschema
- print PASS or FAIL per section and return non-zero on failure
```

- [x] **Step 2: Run the verification script**

Run:

```powershell
python .\06-verification\checks\verify_phase1_phase2.py
```

Expected: a zero exit code and PASS output for Phase 1 and Phase 2 checks.

- [x] **Step 3: Update health reports with actual verification results**

Reports must state:

```text
- what was checked
- what passed
- what remains intentionally open
- whether Phase 1 is complete
- whether Phase 2 is complete
```

- [x] **Step 4: Commit the completed Phase 1 and Phase 2 repository state**

Run:

```powershell
git add .
git commit -m "feat: complete Phase 1 and Phase 2 research runtime spec"
```

Expected: one commit containing manifests, concepts, schemas, mappings, examples, verification script, and updated reports.

