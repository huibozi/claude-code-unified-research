from pathlib import Path
from textwrap import dedent
import json

ROOT = Path(__file__).resolve().parents[2]


def write(rel_path: str, content: str) -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def write_json(rel_path: str, payload: dict) -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


ROOT_README = """
# Unified Claude Code Research

Research repository for studying Claude Code source artifacts, clean-room rewrites, parity work, and downstream runtime migration design.

This repository intentionally excludes raw leaked source code. It stores provenance, comparison outputs, derived specifications, and migration planning artifacts only.

## Status

- Phase 1 research repository baseline: complete
- Phase 2 unified runtime specification baseline: complete
- Raw leaked source publication: intentionally excluded

## Key Documents

- `04-diffs-and-indexes/provenance-index/provenance.md`: source registry and handling policy
- `04-diffs-and-indexes/manifests/current-comparison-summary.md`: current comparison baseline
- `03-specs-and-parity/module-matrices/repository-capability-matrix.md`: cross-repository capability map
- `03-specs-and-parity/source-derived-spec/README.md`: unified runtime spec entrypoint
- `03-specs-and-parity/source-derived-spec/2026-04-01-unified-claude-code-research-runtime-design.md`: approved design record
- `06-verification/reports/research-repo-health.md`: Phase 1 completion evidence
- `06-verification/reports/runtime-spec-health.md`: Phase 2 completion evidence

## Structure

- `01-raw-baselines/`: provenance and handling rules for factual source baselines
- `02-clean-room-rewrites/`: clean-room rewrites and migration workspaces
- `03-specs-and-parity/`: derived concepts, schema, parity reports, and matrices
- `04-diffs-and-indexes/`: manifests, diffs, symbol indexes, and provenance indexes
- `05-migration-blueprints/`: downstream redesign work for OpenClaw, Codex, and Claude
- `06-verification/`: verification checks, snapshots, and health reports

## Current policy

- Raw leaked source is not published in this repository.
- Provenance for all comparison inputs is tracked in markdown.
- Design and migration work must trace back to recorded source evidence.
- Duplicate baselines are recorded once as evidence and explicitly labeled as duplicates.
"""


SPEC_LAYER_README = """
# Specs And Parity

This layer stores the unified runtime concepts, schemas, mappings, parity reports, and comparison matrices derived from the recorded sources.

## Subdirectories

- `source-derived-spec/`: canonical concept docs, JSON schemas, mappings, and examples
- `parity-reports/`: reserved for future deeper parity audits
- `module-matrices/`: cross-repository capability matrices and summaries

## Rules

- Reference evidence instead of embedding copied source.
- Keep conflicts visible instead of silently flattening them.
- Treat the source-derived spec as a semantic reduction of the evidence layer, not a replacement for it.
"""


VERIFICATION_README = """
# Verification

This layer stores validation checks, health reports, and phase completion evidence.

## Entry points

- `checks/verify_phase1_phase2.py`: required Phase 1 and Phase 2 validation script
- `reports/research-repo-health.md`: repository evidence health
- `reports/runtime-spec-health.md`: runtime spec validation status
- `reports/mapping-coverage.md`: mapping coverage summary
- `reports/parity-conflicts.md`: unresolved semantic conflicts intentionally kept visible

## Rules

- Use this layer as the gate for marking work complete.
- Keep repository health and runtime-spec health separate when reporting.
- Treat validation output as evidence, not aspiration.
"""


PROVENANCE = """
# Provenance Index

| Source | Local path | Upstream | Commit | Acquisition date | Type | Read-only handling | Duplication status | Publication status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `claude-code-source` | `C:\\Users\\huibozi\\claude-code-source` | `https://github.com/alex000kim/claude-code.git` | `1becaba` | `2026-04-01` | raw baseline | yes | canonical primary baseline | metadata only | largest factual implementation snapshot, only `src/` plus git metadata |
| `claude-code-source-leak` | `C:\\Users\\huibozi\\claude-code-source-leak` | `https://github.com/alex000kim/claude-code.git` | `1becaba` | `2026-04-01` | duplicate raw baseline | yes | duplicate of `claude-code-source` | metadata only | `src` tree verified identical to canonical baseline |
| `claude-code-Kuberwastaken` | `C:\\Users\\huibozi\\claude-code-forks\\claude-code-Kuberwastaken` | `https://github.com/Kuberwastaken/claude-code.git` | `45f7ac9` | `2026-04-01` | clean-room rewrite | no | independent derivative | repo may be cited and linked | Rust rewrite with a strong `spec/` explanation layer |
| `claude-code-instructkr` | `C:\\Users\\huibozi\\claude-code-forks\\claude-code-instructkr` | `https://github.com/instructkr/claude-code.git` | `9ade3a7` | `2026-04-01` | parity workspace | no | independent derivative | repo may be cited and linked | Python-first porting workspace plus ongoing Rust parity work |

## Handling notes

- Raw baselines are tracked as evidence but not published as code in this repository.
- `claude-code-source-leak` is retained only to document duplication and provenance, not as an independent analytical source.
- Clean-room and parity repositories are treated as derivative research inputs with their own architectural value and their own gaps.
"""


CURRENT_COMPARISON_SUMMARY = """
# Current Comparison Summary

## Repository scale snapshot

| Repository | Counted code files | Counted code lines | Dominant languages | Primary value |
|---|---:|---:|---|---|
| `claude-code-source` | 1902 | 513237 | TypeScript, TSX, JavaScript | primary factual implementation baseline |
| `claude-code-source-leak` | 1902 | 513237 | TypeScript, TSX, JavaScript | duplicate provenance baseline |
| `claude-code-Kuberwastaken` | 53 | 23847 | Rust | clean-room rewrite plus spec distillation |
| `claude-code-instructkr` | 102 | 25201 | Python, Rust | parity tracking and migration methodology |

## Top-level architectural takeaway

- `claude-code-source` is the closest thing to a ground-truth implementation snapshot.
- `claude-code-source-leak` does not add new implementation evidence because the `src/` tree is identical to `claude-code-source` at commit `1becaba`.
- `claude-code-Kuberwastaken` is the clearest clean-room reduction of the source into spec topics and Rust crate boundaries.
- `claude-code-instructkr` is the clearest example of how to preserve subsystem shape while porting into a new implementation language and maintaining parity notes.

## Most relevant module surfaces

- Primary source baseline: `src/commands`, `src/tools`, `src/services`, `src/skills`, `src/tasks`, `src/bridge`, `src/query`
- Kuberwastaken: `spec/`, `src-rust/crates/tools`, `src-rust/crates/query`, `src-rust/crates/commands`, `src-rust/crates/bridge`, `src-rust/crates/core`
- instructkr: `src/`, `src/reference_data/`, `rust/crates/runtime`, `rust/crates/tools`, `rust/crates/commands`, `PARITY.md`

## Immediate research guidance

- Use `claude-code-source` for behavioral truth and edge-case discovery.
- Use `claude-code-Kuberwastaken` for accelerated reading of architecture slices.
- Use `claude-code-instructkr` for parity bookkeeping and migration sequencing.
"""

MANIFESTS = {
    "04-diffs-and-indexes/manifests/source-baseline.manifest.md": """
# Manifest: claude-code-source

## Identity

- Local path: `C:\\Users\\huibozi\\claude-code-source`
- Upstream: `https://github.com/alex000kim/claude-code.git`
- Commit: `1becaba`
- Role: primary factual implementation baseline

## Tree shape

Top-level entries:

- `.git`
- `src`

Primary `src/` module surfaces:

- `assistant`, `bootstrap`, `bridge`, `buddy`, `cli`, `commands`, `components`, `constants`, `context`, `coordinator`
- `entrypoints`, `hooks`, `ink`, `keybindings`, `memdir`, `migrations`, `moreright`, `native-ts`, `outputStyles`, `plugins`
- `query`, `remote`, `schemas`, `screens`, `server`, `services`, `skills`, `state`, `tasks`, `tools`, `types`, `upstreamproxy`, `utils`, `vim`, `voice`

## Counted scale

- Counted code files: `1902`
- Counted code lines: `513237`
- Extension mix: `.ts` `1332`, `.tsx` `552`, `.js` `18`

High-density directories:

- `src/commands`: `207` files
- `src/tools`: `184` files
- `src/services`: `130` files
- `src/skills`: `20` files
- `src/tasks`: `12` files
- `src/bridge`: `31` files

## Anchor evidence files

- `src/main.tsx`
- `src/entrypoints/cli.tsx`
- `src/QueryEngine.ts`
- `src/query.ts`
- `src/tools.ts`
- `src/Tool.ts`
- `src/skills/loadSkillsDir.ts`
- `src/tools/AgentTool/loadAgentsDir.ts`
- `src/services/mcp/client.ts`
- `src/services/tools/toolOrchestration.ts`
- `src/utils/permissions/permissionSetup.ts`
- `src/tasks/LocalAgentTask/LocalAgentTask.tsx`
- `src/tasks/RemoteAgentTask/RemoteAgentTask.tsx`
- `src/bridge/bridgeMain.ts`

## Why this repository matters

This tree is the behavioral source of truth for the research repo. It shows the widest command surface, the broadest tool registry, the most complete skill pipeline, the strongest permissions layer, and the clearest task and bridge implementations.
""",
    "04-diffs-and-indexes/manifests/source-leak.manifest.md": """
# Manifest: claude-code-source-leak

## Identity

- Local path: `C:\\Users\\huibozi\\claude-code-source-leak`
- Upstream: `https://github.com/alex000kim/claude-code.git`
- Commit: `1becaba`
- Role: duplicate provenance baseline

## Verified duplication status

- Top-level shape matches the canonical source snapshot: `.git`, `src`
- Counted code files: `1902`
- Counted code lines: `513237`
- `git diff --no-index --quiet src src` between this tree and `claude-code-source` returns identical for the `src/` tree

## Handling decision

This repository is retained only to document duplication and provenance. It should not be counted as an independent implementation witness in future capability or parity analysis.
""",
    "04-diffs-and-indexes/manifests/kuberwastaken.manifest.md": """
# Manifest: claude-code-Kuberwastaken

## Identity

- Local path: `C:\\Users\\huibozi\\claude-code-forks\\claude-code-Kuberwastaken`
- Upstream: `https://github.com/Kuberwastaken/claude-code.git`
- Commit: `45f7ac9`
- Role: clean-room rewrite and spec distillation

## Tree shape

Top-level entries:

- `.git`
- `README.md`
- `public`
- `spec`
- `src-rust`

Spec topics:

- `00_overview.md`
- `01_core_entry_query.md`
- `02_commands.md`
- `03_tools.md`
- `04_components_core_messages.md`
- `05_components_agents_permissions_design.md`
- `06_services_context_state.md`
- `07_hooks.md`
- `08_ink_terminal.md`
- `09_bridge_cli_remote.md`
- `10_utils.md`
- `11_special_systems.md`
- `12_constants_types.md`
- `13_rust_codebase.md`
- `INDEX.md`

Rust crate surfaces:

- `api`, `bridge`, `buddy`, `cli`, `commands`, `core`, `mcp`, `query`, `tools`, `tui`

## Counted scale

- Counted Rust files: `53`
- Counted Rust lines: `23847`

## Anchor evidence files

- `README.md`
- `spec/00_overview.md`
- `spec/01_core_entry_query.md`
- `spec/02_commands.md`
- `spec/03_tools.md`
- `spec/05_components_agents_permissions_design.md`
- `spec/06_services_context_state.md`
- `spec/09_bridge_cli_remote.md`
- `src-rust/crates/cli/src/main.rs`
- `src-rust/crates/query/src/lib.rs`
- `src-rust/crates/tools/src/lib.rs`
- `src-rust/crates/query/src/agent_tool.rs`
- `src-rust/crates/query/src/auto_dream.rs`
- `src-rust/crates/bridge/src/lib.rs`

## Why this repository matters

This repository is the best acceleration layer for reading architecture. It separates raw-source detail from derived behavior, then re-expresses the system in Rust crate boundaries that are easier to reason about when building a new runtime.
""",
    "04-diffs-and-indexes/manifests/instructkr.manifest.md": """
# Manifest: claude-code-instructkr

## Identity

- Local path: `C:\\Users\\huibozi\\claude-code-forks\\claude-code-instructkr`
- Upstream: `https://github.com/instructkr/claude-code.git`
- Commit: `9ade3a7`
- Role: parity workspace and migration methodology reference

## Tree shape

Top-level entries:

- `.claude`
- `.claude.json`
- `.github`
- `assets`
- `rust`
- `src`
- `tests`
- `CLAUDE.md`
- `PARITY.md`
- `README.md`

Python `src/` subsystem shape intentionally mirrors the archived implementation surface, including:

- `assistant`, `bridge`, `cli`, `components`, `constants`, `coordinator`, `entrypoints`, `hooks`, `memdir`, `plugins`
- `remote`, `schemas`, `screens`, `services`, `skills`, `state`, `tools`, `types`, `upstreamproxy`, `vim`, `voice`
- `port_manifest.py`, `query.py`, `QueryEngine.py`, `Tool.py`, `tasks.py`, `runtime.py`, `parity_audit.py`
- `reference_data/` snapshots for commands, tools, and subsystem inventories

Rust crate surfaces:

- `api`, `commands`, `compat-harness`, `runtime`, `rusty-claude-cli`, `tools`

## Counted scale

- Counted code files: `102`
- Counted code lines: `25201`
- Extension mix: `.py` `67`, `.rs` `35`

## Anchor evidence files

- `README.md`
- `PARITY.md`
- `src/port_manifest.py`
- `src/query.py`
- `src/query_engine.py`
- `src/Tool.py`
- `src/tools.py`
- `src/tasks.py`
- `src/permissions.py`
- `src/reference_data/archive_surface_snapshot.json`
- `rust/crates/runtime/src/conversation.rs`
- `rust/crates/runtime/src/config.rs`
- `rust/crates/runtime/src/permissions.rs`
- `rust/crates/tools/src/lib.rs`

## Why this repository matters

This repository shows how to keep architectural shape visible while rewriting implementation language and runtime plumbing. It is the strongest template for parity management, gap reporting, and staged migration away from a leaked archive.
""",
}


STRUCTURE_DIFFS = {
    "04-diffs-and-indexes/structure-diffs/source-vs-source-leak.md": """
# Structure Diff: claude-code-source vs claude-code-source-leak

## Summary

These repositories point to the same upstream, the same commit, and an identical `src/` tree.

| Category | claude-code-source | claude-code-source-leak | Result |
|---|---|---|---|
| Upstream | `alex000kim/claude-code` | `alex000kim/claude-code` | same |
| Commit | `1becaba` | `1becaba` | same |
| Top-level implementation tree | `src/` | `src/` | same |
| Counted code files | `1902` | `1902` | same |
| Counted code lines | `513237` | `513237` | same |
| `src/` diff | identical | identical | same |

## Interpretation

`claude-code-source-leak` should not be treated as a second witness. It only confirms duplication and provenance.
""",
    "04-diffs-and-indexes/structure-diffs/source-vs-kuberwastaken.md": """
# Structure Diff: claude-code-source vs claude-code-Kuberwastaken

## Summary

The primary source baseline is a large TypeScript implementation snapshot. Kuberwastaken is a much smaller Rust clean-room rewrite with an explicit spec layer that distills behavior before implementation.

| Category | claude-code-source | claude-code-Kuberwastaken |
|---|---|---|
| Languages | TypeScript, TSX, JavaScript | Rust |
| Counted code files | `1902` | `53` |
| Counted code lines | `513237` | `23847` |
| Behavioral truth | highest | derived |
| Reading speed | lowest | highest |
| Architectural reduction | implicit in code | explicit in `spec/` |

## Structural differences

- Source keeps nearly every subsystem under one very large `src/` tree.
- Kuberwastaken splits reasoning into `spec/` topics and a `src-rust/crates/` implementation tree.
- Kuberwastaken preserves many capability names but compresses or re-expresses implementation details.
- Kuberwastaken is strongest when used as an architecture reading aid, not as a parity oracle.
""",
    "04-diffs-and-indexes/structure-diffs/source-vs-instructkr.md": """
# Structure Diff: claude-code-source vs claude-code-instructkr

## Summary

The primary source baseline is a direct TypeScript implementation snapshot. instructkr preserves much of the subsystem naming surface but moves implementation toward Python and Rust while tracking missing parity explicitly.

| Category | claude-code-source | claude-code-instructkr |
|---|---|---|
| Languages | TypeScript, TSX, JavaScript | Python, Rust |
| Counted code files | `1902` | `102` |
| Counted code lines | `513237` | `25201` |
| Subsystem-name preservation | native | intentionally mirrored |
| Gap tracking | implicit | explicit in `PARITY.md` |
| Migration guidance | indirect | strong |

## Structural differences

- instructkr keeps many familiar subsystem names under `src/` but shrinks them to a porting workspace.
- instructkr adds `reference_data/` snapshots, making parity auditing easier than in the raw source baseline.
- instructkr carries a second Rust runtime slice under `rust/crates/`, turning it into both a migration workspace and an implementation lab.
- instructkr is best used to plan staged migration work and to make missing parity visible.
""",
}


RUNTIME_CAPABILITY_INDEX = """
# Runtime Capability Index

| Capability | Primary source evidence | Kuberwastaken evidence | instructkr evidence | Notes |
|---|---|---|---|---|
| Runtime bootstrap | `src/main.tsx`, `src/entrypoints/cli.tsx` | `spec/00_overview.md`, `src-rust/crates/cli/src/main.rs` | `src/main.py`, `src/runtime.py`, `rust/crates/rusty-claude-cli/src/main.rs` | all three expose a runtime entrypoint surface |
| Session and query loop | `src/query.ts`, `src/QueryEngine.ts` | `spec/01_core_entry_query.md`, `src-rust/crates/query/src/lib.rs` | `src/query.py`, `src/query_engine.py`, `rust/crates/runtime/src/conversation.rs` | core execution semantics are visible in every repo |
| Command registry | `src/commands/` | `spec/02_commands.md`, `src-rust/crates/commands/src/lib.rs` | `src/commands.py`, `rust/crates/commands/src/lib.rs` | breadth differs sharply |
| Tool registry | `src/tools.ts`, `src/Tool.ts`, `src/tools/` | `spec/03_tools.md`, `src-rust/crates/tools/src/lib.rs` | `src/tools.py`, `src/Tool.py`, `rust/crates/tools/src/lib.rs` | tool semantics survive across every rewrite |
| Skill system | `src/skills/loadSkillsDir.ts` | `src-rust/crates/tools/src/skill_tool.rs`, `src-rust/crates/tools/src/bundled_skills.rs` | `src/skills/`, `src/reference_data/tools_snapshot.json`, `PARITY.md` | TS remains the richest skill pipeline |
| Agent orchestration | `src/tools/AgentTool/loadAgentsDir.ts`, `src/query.ts`, `src/tasks/` | `spec/05_components_agents_permissions_design.md`, `src-rust/crates/query/src/agent_tool.rs` | `src/tasks.py`, `src/coordinator/`, `rust/crates/runtime/src/conversation.rs` | coordination exists everywhere but depth varies |
| Tasks and background work | `src/tasks/LocalAgentTask`, `src/tasks/RemoteAgentTask` | `src-rust/crates/tools/src/tasks.rs`, `src-rust/crates/query/src/cron_scheduler.rs` | `src/task.py`, `src/tasks.py` | instructkr and Kuberwastaken both compress the task model |
| Connectors, MCP, and bridge | `src/services/mcp/client.ts`, `src/bridge/bridgeMain.ts` | `spec/09_bridge_cli_remote.md`, `src-rust/crates/mcp/src/lib.rs`, `src-rust/crates/bridge/src/lib.rs` | `rust/crates/runtime/src/mcp.rs`, `rust/crates/runtime/src/remote.rs`, `src/remote_runtime.py` | bridge and MCP survive as first-class concepts |
| Memory and consolidation | `src/memdir/`, `src/skills/loadSkillsDir.ts`, `src/query.ts` | `src-rust/crates/core/src/memdir.rs`, `src-rust/crates/query/src/auto_dream.rs` | `src/memdir/`, `src/session_store.py`, `PARITY.md` | Kuberwastaken surfaces memory consolidation most explicitly |
| Policy and permissions | `src/utils/permissions/permissionSetup.ts`, `src/services/tools/toolOrchestration.ts` | `spec/05_components_agents_permissions_design.md`, `src-rust/crates/core/src/lib.rs` | `src/permissions.py`, `rust/crates/runtime/src/permissions.rs`, `PARITY.md` | permission semantics are central in every repo |
"""


REPOSITORY_CAPABILITY_MATRIX = """
# Repository Capability Matrix

Coverage meanings:

- `primary`: canonical implementation witness
- `strong`: substantial implementation or distilled behavior coverage
- `partial`: meaningful but incomplete coverage
- `minimal`: naming or placeholder coverage only
- `duplicate`: not an independent witness

| Runtime object | claude-code-source | claude-code-source-leak | claude-code-Kuberwastaken | claude-code-instructkr |
|---|---|---|---|---|
| Runtime | primary | duplicate | strong | partial |
| Session | primary | duplicate | strong | partial |
| Agent | primary | duplicate | strong | partial |
| Command | primary | duplicate | strong | partial |
| Tool | primary | duplicate | strong | partial |
| Skill | primary | duplicate | partial | partial |
| Task | primary | duplicate | partial | partial |
| Memory | primary | duplicate | partial | minimal |
| Connector | primary | duplicate | partial | partial |
| Policy | primary | duplicate | partial | partial |

## Notes

- `claude-code-source` is the canonical evidence base for every object.
- `claude-code-source-leak` confirms duplication only and should not affect coverage scoring.
- `claude-code-Kuberwastaken` is strongest on runtime, query, command, tool, and bridge abstractions.
- `claude-code-instructkr` is strongest on parity bookkeeping and migration scaffolding rather than full runtime breadth.
"""


SOURCE_DERIVED_SPEC_README = """
# Source-Derived Runtime Spec

This directory turns the recorded source evidence into one unified runtime model.

## Core objects

- Runtime
- Session
- Agent
- Command
- Tool
- Skill
- Task
- Memory
- Connector
- Policy

## Module groups

- `core-runtime`: Runtime, Session
- `execution`: Agent, Command, Tool, Skill, Task
- `integration`: Connector, MCP, bridge, transport semantics
- `governance`: Policy, permissions, audit
- `knowledge`: Memory, parity, indexes, spec maintenance

## Contents

- `concepts/`: semantic definitions for the ten objects
- `schemas/`: JSON Schema Draft 2020-12 contracts for the ten objects
- `mappings/`: source-to-spec alignment for the three non-duplicate repositories
- `examples/`: schema-valid example payloads for downstream runtime work
- `2026-04-01-unified-claude-code-research-runtime-design.md`: the approved design record

## Reading order

1. Read `../module-matrices/repository-capability-matrix.md`
2. Read the concept file for the object you care about
3. Open the matching schema
4. Check the corresponding mapping table for source, Kuberwastaken, and instructkr
5. Use an example payload as the starting point for downstream runtime design
"""

OBJECTS = {
    "runtime": {
        "title": "Runtime",
        "purpose": "Defines the top-level execution environment that owns registries, state, policy, and connector wiring.",
        "responsibilities": ["Boot the system and hold immutable identity such as name and version.", "Expose registries for commands, tools, skills, and agents.", "Bind state storage, policy storage, and connector registration into one runtime context."],
        "fields": ["id", "name", "version", "registries", "state_store", "policy_store", "connector_registry", "feature_flags"],
        "semantics": ["A runtime exists before any session begins.", "Feature flags and connector availability shape the capabilities exposed to sessions and agents.", "Downstream implementations may host more than one runtime, but every session must point at exactly one runtime."],
        "relationships": ["Parents Session through `runtime_id`.", "Owns the registries consumed by Command, Tool, Skill, Agent, and Connector.", "Delegates policy decisions to Policy and memory access to Memory stores."],
        "evidence": ["`claude-code-source`: `src/main.tsx`, `src/entrypoints/cli.tsx`, `src/tools.ts`", "`claude-code-Kuberwastaken`: `spec/00_overview.md`, `spec/13_rust_codebase.md`, `src-rust/crates/cli/src/main.rs`", "`claude-code-instructkr`: `src/main.py`, `src/runtime.py`, `rust/crates/rusty-claude-cli/src/main.rs`", "Research layer: `04-diffs-and-indexes/manifests/source-baseline.manifest.md`, `03-specs-and-parity/module-matrices/repository-capability-matrix.md`"],
        "parity": ["Kuberwastaken compresses runtime semantics into crate boundaries and spec topics rather than a giant app shell.", "instructkr preserves a runtime surface but does not yet match full TypeScript breadth."],
    },
    "session": {
        "title": "Session",
        "purpose": "Represents one active conversation or execution context with its own model, cwd, memory references, and transcript.",
        "responsibilities": ["Track per-run state such as current model, mode, cwd, and status.", "Bind an agent identity to a concrete conversation transcript.", "Snapshot permission and memory context for deterministic resumption."],
        "fields": ["id", "runtime_id", "agent_id", "cwd", "mode", "model", "permission_snapshot", "memory_refs", "transcript_ref", "status"],
        "semantics": ["A session is created inside one runtime and normally owned by one active agent.", "Session status changes over time: active, paused, completed, or failed.", "Resuming work means restoring transcript, permissions, and memory references together."],
        "relationships": ["Belongs to Runtime.", "References one Agent, zero or more Memory records, and one transcript location.", "Provides context to Task execution and policy checks."],
        "evidence": ["`claude-code-source`: `src/query.ts`, `src/QueryEngine.ts`, `src/assistant/sessionHistory.ts`", "`claude-code-Kuberwastaken`: `spec/01_core_entry_query.md`, `src-rust/crates/query/src/lib.rs`, `src-rust/crates/cli/src/main.rs`", "`claude-code-instructkr`: `src/query.py`, `src/query_engine.py`, `rust/crates/runtime/src/session.rs`", "Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`"],
        "parity": ["instructkr and Kuberwastaken both model conversation state, but they do not expose every TS transport and resume behavior.", "The TypeScript baseline remains the clearest reference for session lifecycle breadth."],
    },
    "agent": {
        "title": "Agent",
        "purpose": "Describes an execution identity with model choice, tool scope, skill scope, permissions, and isolation settings.",
        "responsibilities": ["Define what model and reasoning effort to use.", "Constrain allowed tools, skills, and required connectors.", "Control permission mode, memory scope, isolation, and turn limits."],
        "fields": ["id", "agent_type", "source", "model", "effort", "tools", "skills", "permission_mode", "memory_scope", "isolation", "max_turns", "hooks", "required_connectors"],
        "semantics": ["Agents may be user-facing, background, remote, or child-worker identities.", "An agent definition should be declarative enough to recreate a session elsewhere.", "Permission and isolation rules are part of the agent contract, not an afterthought."],
        "relationships": ["Used by Session and Task.", "Consumes Tool, Skill, Connector, Memory, and Policy objects.", "Spawns or coordinates other agents through AgentTool-style facilities."],
        "evidence": ["`claude-code-source`: `src/tools/AgentTool/loadAgentsDir.ts`, `src/query.ts`, `src/tasks/LocalAgentTask/LocalAgentTask.tsx`", "`claude-code-Kuberwastaken`: `spec/05_components_agents_permissions_design.md`, `src-rust/crates/query/src/agent_tool.rs`", "`claude-code-instructkr`: `src/tasks.py`, `src/coordinator/__init__.py`, `rust/crates/runtime/src/conversation.rs`", "Research layer: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`"],
        "parity": ["Kuberwastaken retains stronger agent semantics than instructkr.", "instructkr exposes coordinator and task surfaces, but not full parity with the TS agent configuration pipeline."],
    },
    "command": {
        "title": "Command",
        "purpose": "Represents a user-triggered named entrypoint such as slash commands, setup commands, or structured CLI actions.",
        "responsibilities": ["Give stable names and aliases to user-invokable actions.", "Describe enablement conditions and input contracts.", "Point to the implementation surface that handles the command."],
        "fields": ["name", "aliases", "source", "kind", "description", "input_contract", "handler_ref", "enabled_when"],
        "semantics": ["Commands are resolved before tool calling and often reconfigure runtime state.", "A command may be interactive, noninteractive, setup-oriented, or administrative.", "The same semantic command can have different handler implementations across runtimes."],
        "relationships": ["Registered by Runtime registries.", "Often mutates Session state or dispatches into Tool and Task execution.", "May depend on Connector or Policy availability."],
        "evidence": ["`claude-code-source`: `src/commands/`, `src/commands/review`, `src/commands/memory`, `src/commands/config`", "`claude-code-Kuberwastaken`: `spec/02_commands.md`, `src-rust/crates/commands/src/lib.rs`, `src-rust/crates/commands/src/named_commands.rs`", "`claude-code-instructkr`: `src/commands.py`, `src/reference_data/commands_snapshot.json`, `rust/crates/commands/src/lib.rs`", "Research layer: `04-diffs-and-indexes/manifests/source-baseline.manifest.md`"],
        "parity": ["TypeScript has the broadest command surface by far.", "Both rewrites compress command breadth but preserve the need for a registry and stable command semantics."],
    },
    "tool": {
        "title": "Tool",
        "purpose": "Represents a model-callable capability with typed I/O, side-effect rules, and concurrency and permission metadata.",
        "responsibilities": ["Expose capability metadata to the model and runtime.", "Define input and output contracts.", "Describe permission and side-effect boundaries for orchestration."],
        "fields": ["name", "source", "description", "input_schema", "output_schema", "permission_requirements", "is_concurrency_safe", "side_effect_level"],
        "semantics": ["Tools are registered centrally and filtered by runtime context.", "Tool execution must be auditable and permission-aware.", "Concurrency safety matters because tool orchestration can fan out parallel work."],
        "relationships": ["Owned by Runtime registries and consumed by Agent and Session.", "Guarded by Policy and often backed by Connector integrations.", "Composed by Skill definitions."],
        "evidence": ["`claude-code-source`: `src/Tool.ts`, `src/tools.ts`, `src/services/tools/toolOrchestration.ts`, `src/tools/`", "`claude-code-Kuberwastaken`: `spec/03_tools.md`, `src-rust/crates/tools/src/lib.rs`, `src-rust/crates/tools/src/mcp_resources.rs`", "`claude-code-instructkr`: `src/Tool.py`, `src/tools.py`, `rust/crates/tools/src/lib.rs`, `PARITY.md`", "Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`"],
        "parity": ["The source baseline remains the only place with the full TS tool surface.", "Both derivative repos make tool registries explicit, which helps downstream runtime design."],
    },
    "skill": {
        "title": "Skill",
        "purpose": "Defines a reusable high-level behavior package with its own prompts, tool allowances, routing hints, and path conditions.",
        "responsibilities": ["Package higher-level behavior beyond a single tool.", "Describe when the skill should be selected and what tools it may call.", "Allow model overrides, execution context changes, and path-based activation."],
        "fields": ["name", "source", "description", "when_to_use", "allowed_tools", "argument_hint", "model_override", "execution_context", "path_conditions", "hooks"],
        "semantics": ["Skills sit between commands and tools: they shape strategy rather than just exposing primitive actions.", "A runtime can ship bundled skills and also load local or connector-provided skills.", "Path conditions allow skills to become context-aware without becoming hard-coded into the runtime."],
        "relationships": ["Consumed by Agent definitions and suggested within Session execution.", "Restricted by Tool and Policy constraints.", "May be discovered from local directories or external connectors."],
        "evidence": ["`claude-code-source`: `src/skills/loadSkillsDir.ts`, `src/skills/bundledSkills.ts`, `src/commands/skills/`", "`claude-code-Kuberwastaken`: `src-rust/crates/tools/src/skill_tool.rs`, `src-rust/crates/tools/src/bundled_skills.rs`", "`claude-code-instructkr`: `src/skills/`, `src/reference_data/tools_snapshot.json`, `PARITY.md`", "Research layer: `04-diffs-and-indexes/manifests/kuberwastaken.manifest.md`"],
        "parity": ["The TS baseline has the most advanced skill loading and path-activation behavior.", "Both rewrites preserve the concept of skills but not the full registry and lifecycle depth."],
    },
    "task": {
        "title": "Task",
        "purpose": "Represents asynchronous or background execution units such as child-agent runs, remote jobs, or scheduled work.",
        "responsibilities": ["Track ownership, input, progress, result location, and resume strategy.", "Separate long-running work from the main foreground session.", "Support notification and recovery behavior."],
        "fields": ["id", "type", "owner_agent", "origin", "input", "status", "progress", "result_ref", "notification_policy", "resume_strategy"],
        "semantics": ["Tasks may be local, remote, or delegated to other agents.", "A task lifecycle should be inspectable and resumable from recorded state.", "Notification policy is part of the runtime contract for background work."],
        "relationships": ["Created by Session or Command flows and usually owned by an Agent.", "Can require Connector access for remote or MCP-backed execution.", "Often writes into Memory or transcript outputs after completion."],
        "evidence": ["`claude-code-source`: `src/tasks/LocalAgentTask/LocalAgentTask.tsx`, `src/tasks/RemoteAgentTask/RemoteAgentTask.tsx`, `src/commands/ultraplan.tsx`", "`claude-code-Kuberwastaken`: `src-rust/crates/tools/src/tasks.rs`, `src-rust/crates/query/src/cron_scheduler.rs`", "`claude-code-instructkr`: `src/task.py`, `src/tasks.py`, `rust/crates/runtime/src/conversation.rs`", "Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`"],
        "parity": ["The source baseline contains the clearest local-versus-remote task split.", "Kuberwastaken and instructkr both keep the task idea alive but compress its lifecycle details."],
    },
    "memory": {
        "title": "Memory",
        "purpose": "Captures persistent knowledge records and memory directory artifacts used to orient future sessions and agents.",
        "responsibilities": ["Store durable knowledge outside a single turn or tool call.", "Organize retention and ownership rules.", "Let sessions and agents retrieve stable context quickly."],
        "fields": ["id", "scope", "owner", "source", "content_ref", "last_updated_at", "retention_policy"],
        "semantics": ["Memory is distinct from transcript history even when both reference the same facts.", "Scopes typically range from session-local to user- or project-level.", "Background consolidation or pruning can change memory state independently of foreground work."],
        "relationships": ["Referenced by Session and Agent.", "Governed by Policy retention rules.", "May be produced or updated by Task execution and skill pipelines."],
        "evidence": ["`claude-code-source`: `src/memdir/`, `src/commands/memory/`, `src/query.ts`", "`claude-code-Kuberwastaken`: `src-rust/crates/core/src/memdir.rs`, `src-rust/crates/query/src/auto_dream.rs`", "`claude-code-instructkr`: `src/memdir/`, `src/session_store.py`, `PARITY.md`", "Research layer: `04-diffs-and-indexes/manifests/instructkr.manifest.md`"],
        "parity": ["Kuberwastaken makes memory consolidation especially legible through its `auto_dream` slice.", "instructkr keeps memory surfaces but currently has the lightest durable-memory implementation depth."],
    },
    "connector": {
        "title": "Connector",
        "purpose": "Represents external integrations such as MCP servers, bridges, remote runtimes, channels, and webhooks.",
        "responsibilities": ["Describe transport, authentication mode, capabilities, and resource contracts.", "Normalize external systems into a runtime-usable integration shape.", "Provide health state that the runtime can inspect before use."],
        "fields": ["id", "kind", "transport", "capabilities", "auth_mode", "resource_contracts", "health_state"],
        "semantics": ["Connectors may expose tools, resources, commands, or notifications.", "Connector health is dynamic and should be observable.", "Runtime and session layers may filter connectors based on policy and environment."],
        "relationships": ["Registered by Runtime and required by Agent definitions.", "Often back Tool execution and remote Task flows.", "Constrained by Policy and surfaced to Session status."],
        "evidence": ["`claude-code-source`: `src/services/mcp/client.ts`, `src/bridge/bridgeMain.ts`, `src/remote/`", "`claude-code-Kuberwastaken`: `spec/09_bridge_cli_remote.md`, `src-rust/crates/mcp/src/lib.rs`, `src-rust/crates/bridge/src/lib.rs`", "`claude-code-instructkr`: `src/remote_runtime.py`, `rust/crates/runtime/src/mcp.rs`, `rust/crates/runtime/src/remote.rs`", "Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`"],
        "parity": ["The source baseline remains the richest reference for MCP client lifecycle and bridge integration.", "Both rewrites prove that connectors can be normalized as a first-class runtime object."],
    },
    "policy": {
        "title": "Policy",
        "purpose": "Captures allow, deny, ask, danger-filter, and audit rules that shape what the runtime may do.",
        "responsibilities": ["Centralize permission decisions and danger filters.", "Provide explicit audit requirements for risky actions.", "Separate policy expression from tool implementation."],
        "fields": ["id", "scope", "allow_rules", "deny_rules", "ask_rules", "danger_filters", "audit_requirements"],
        "semantics": ["Policy applies at runtime, session, and agent levels.", "Not every denial should be static; some actions route through an ask-policy path.", "Audit requirements should survive even when execution is automated."],
        "relationships": ["Consumed by Runtime, Session, Agent, Tool, and Connector flows.", "Interacts with Task scheduling and Memory retention.", "Provides the governance boundary for dangerous operations."],
        "evidence": ["`claude-code-source`: `src/utils/permissions/permissionSetup.ts`, `src/services/tools/toolOrchestration.ts`, `src/commands/permissions/`", "`claude-code-Kuberwastaken`: `spec/05_components_agents_permissions_design.md`, `src-rust/crates/core/src/lib.rs`", "`claude-code-instructkr`: `src/permissions.py`, `rust/crates/runtime/src/permissions.rs`, `PARITY.md`", "Research layer: `03-specs-and-parity/module-matrices/repository-capability-matrix.md`"],
        "parity": ["The source baseline shows the widest policy and permission surface.", "Derivative repositories preserve the concept but not the full TS policy ecosystem."],
    },
}

SCHEMAS = {
    "runtime": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/runtime.schema.json", "title": "Runtime", "type": "object", "additionalProperties": False, "required": ["id", "name", "version", "registries", "state_store", "policy_store", "connector_registry", "feature_flags"], "properties": {"id": {"type": "string"}, "name": {"type": "string"}, "version": {"type": "string"}, "registries": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}, "state_store": {"type": "object", "additionalProperties": False, "required": ["type", "location"], "properties": {"type": {"type": "string"}, "location": {"type": "string"}}}, "policy_store": {"type": "object", "additionalProperties": False, "required": ["type", "location"], "properties": {"type": {"type": "string"}, "location": {"type": "string"}}}, "connector_registry": {"type": "array", "items": {"type": "string"}}, "feature_flags": {"type": "array", "items": {"type": "string"}}}},
    "session": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/session.schema.json", "title": "Session", "type": "object", "additionalProperties": False, "required": ["id", "runtime_id", "agent_id", "cwd", "mode", "model", "permission_snapshot", "memory_refs", "transcript_ref", "status"], "properties": {"id": {"type": "string"}, "runtime_id": {"type": "string"}, "agent_id": {"type": "string"}, "cwd": {"type": "string"}, "mode": {"type": "string"}, "model": {"type": "string"}, "permission_snapshot": {"type": "object"}, "memory_refs": {"type": "array", "items": {"type": "string"}}, "transcript_ref": {"type": "string"}, "status": {"type": "string", "enum": ["new", "active", "paused", "completed", "failed"]}}},
    "agent": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/agent.schema.json", "title": "Agent", "type": "object", "additionalProperties": False, "required": ["id", "agent_type", "source", "model", "effort", "tools", "skills", "permission_mode", "memory_scope", "isolation", "max_turns", "hooks", "required_connectors"], "properties": {"id": {"type": "string"}, "agent_type": {"type": "string"}, "source": {"type": "string"}, "model": {"type": "string"}, "effort": {"type": "string", "enum": ["low", "medium", "high", "xhigh"]}, "tools": {"type": "array", "items": {"type": "string"}}, "skills": {"type": "array", "items": {"type": "string"}}, "permission_mode": {"type": "string"}, "memory_scope": {"type": "string", "enum": ["session", "local", "project", "user", "mixed"]}, "isolation": {"type": "string"}, "max_turns": {"type": "integer", "minimum": 1}, "hooks": {"type": "array", "items": {"type": "string"}}, "required_connectors": {"type": "array", "items": {"type": "string"}}}},
    "command": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/command.schema.json", "title": "Command", "type": "object", "additionalProperties": False, "required": ["name", "aliases", "source", "kind", "description", "input_contract", "handler_ref", "enabled_when"], "properties": {"name": {"type": "string"}, "aliases": {"type": "array", "items": {"type": "string"}}, "source": {"type": "string"}, "kind": {"type": "string"}, "description": {"type": "string"}, "input_contract": {"type": "object"}, "handler_ref": {"type": "string"}, "enabled_when": {"type": "array", "items": {"type": "string"}}}},
    "tool": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/tool.schema.json", "title": "Tool", "type": "object", "additionalProperties": False, "required": ["name", "source", "description", "input_schema", "output_schema", "permission_requirements", "is_concurrency_safe", "side_effect_level"], "properties": {"name": {"type": "string"}, "source": {"type": "string"}, "description": {"type": "string"}, "input_schema": {"type": "object"}, "output_schema": {"type": "object"}, "permission_requirements": {"type": "array", "items": {"type": "string"}}, "is_concurrency_safe": {"type": "boolean"}, "side_effect_level": {"type": "string", "enum": ["none", "low", "medium", "high"]}}},
    "skill": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/skill.schema.json", "title": "Skill", "type": "object", "additionalProperties": False, "required": ["name", "source", "description", "when_to_use", "allowed_tools", "argument_hint", "model_override", "execution_context", "path_conditions", "hooks"], "properties": {"name": {"type": "string"}, "source": {"type": "string"}, "description": {"type": "string"}, "when_to_use": {"type": "string"}, "allowed_tools": {"type": "array", "items": {"type": "string"}}, "argument_hint": {"type": "string"}, "model_override": {"type": ["string", "null"]}, "execution_context": {"type": "string"}, "path_conditions": {"type": "array", "items": {"type": "string"}}, "hooks": {"type": "array", "items": {"type": "string"}}}},
    "task": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/task.schema.json", "title": "Task", "type": "object", "additionalProperties": False, "required": ["id", "type", "owner_agent", "origin", "input", "status", "progress", "result_ref", "notification_policy", "resume_strategy"], "properties": {"id": {"type": "string"}, "type": {"type": "string"}, "owner_agent": {"type": "string"}, "origin": {"type": "string"}, "input": {"type": "object"}, "status": {"type": "string", "enum": ["queued", "running", "paused", "completed", "failed"]}, "progress": {"type": "integer", "minimum": 0, "maximum": 100}, "result_ref": {"type": "string"}, "notification_policy": {"type": "string"}, "resume_strategy": {"type": "string"}}},
    "memory": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/memory.schema.json", "title": "Memory", "type": "object", "additionalProperties": False, "required": ["id", "scope", "owner", "source", "content_ref", "last_updated_at", "retention_policy"], "properties": {"id": {"type": "string"}, "scope": {"type": "string", "enum": ["session", "local", "project", "user"]}, "owner": {"type": "string"}, "source": {"type": "string"}, "content_ref": {"type": "string"}, "last_updated_at": {"type": "string", "format": "date-time"}, "retention_policy": {"type": "string"}}},
    "connector": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/connector.schema.json", "title": "Connector", "type": "object", "additionalProperties": False, "required": ["id", "kind", "transport", "capabilities", "auth_mode", "resource_contracts", "health_state"], "properties": {"id": {"type": "string"}, "kind": {"type": "string", "enum": ["mcp", "channel", "bridge", "webhook", "remote-runtime", "local-service"]}, "transport": {"type": "string"}, "capabilities": {"type": "array", "items": {"type": "string"}}, "auth_mode": {"type": "string"}, "resource_contracts": {"type": "array", "items": {"type": "string"}}, "health_state": {"type": "string", "enum": ["unknown", "healthy", "degraded", "offline"]}}},
    "policy": {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://huibozi.github.io/claude-code-unified-research/policy.schema.json", "title": "Policy", "type": "object", "additionalProperties": False, "required": ["id", "scope", "allow_rules", "deny_rules", "ask_rules", "danger_filters", "audit_requirements"], "properties": {"id": {"type": "string"}, "scope": {"type": "string"}, "allow_rules": {"type": "array", "items": {"type": "string"}}, "deny_rules": {"type": "array", "items": {"type": "string"}}, "ask_rules": {"type": "array", "items": {"type": "string"}}, "danger_filters": {"type": "array", "items": {"type": "string"}}, "audit_requirements": {"type": "array", "items": {"type": "string"}}}},
}

MAPPINGS = {
    "03-specs-and-parity/source-derived-spec/mappings/source-to-spec.md": """
# Mapping: claude-code-source to unified runtime spec

| Spec object | Coverage level | Observed implementation surface | Evidence | Notes |
|---|---|---|---|---|
| Runtime | primary | app bootstrap, registries, feature gating, startup wiring | `src/main.tsx`, `src/entrypoints/cli.tsx`, `src/tools.ts` | canonical runtime witness |
| Session | primary | query engine, transcript, session history, resume behavior | `src/query.ts`, `src/QueryEngine.ts`, `src/assistant/sessionHistory.ts` | richest lifecycle reference |
| Agent | primary | agent loading, child-agent orchestration, local and remote agent tasks | `src/tools/AgentTool/loadAgentsDir.ts`, `src/tasks/LocalAgentTask/LocalAgentTask.tsx`, `src/tasks/RemoteAgentTask/RemoteAgentTask.tsx` | strongest agent contract source |
| Command | primary | broad slash-command and administrative command surface | `src/commands/` | widest command registry |
| Tool | primary | central tool contracts, orchestration, permissions-aware execution | `src/Tool.ts`, `src/tools.ts`, `src/services/tools/toolOrchestration.ts` | strongest tool semantics |
| Skill | primary | bundled and local skill loading with path conditions | `src/skills/loadSkillsDir.ts`, `src/skills/bundledSkills.ts` | best skill DSL witness |
| Task | primary | local, remote, and background task models | `src/tasks/`, `src/commands/ultraplan.tsx` | task split is explicit |
| Memory | primary | memory commands, memdir, consolidation-related behavior | `src/memdir/`, `src/commands/memory/`, `src/query.ts` | strongest durable-memory reference |
| Connector | primary | MCP client, remote surfaces, bridge runtime | `src/services/mcp/client.ts`, `src/bridge/bridgeMain.ts`, `src/remote/` | connector breadth is highest here |
| Policy | primary | permissions setup, orchestration safety, permissions commands | `src/utils/permissions/permissionSetup.ts`, `src/services/tools/toolOrchestration.ts`, `src/commands/permissions/` | policy semantics are clearest here |
""",
    "03-specs-and-parity/source-derived-spec/mappings/kuber-to-spec.md": """
# Mapping: claude-code-Kuberwastaken to unified runtime spec

| Spec object | Coverage level | Observed implementation surface | Evidence | Notes |
|---|---|---|---|---|
| Runtime | strong | clean-room bootstrap and crate layout | `spec/00_overview.md`, `src-rust/crates/cli/src/main.rs` | distilled rather than exhaustive |
| Session | strong | query loop and conversation flow | `spec/01_core_entry_query.md`, `src-rust/crates/query/src/lib.rs` | useful execution summary |
| Agent | strong | coordinator and agent tool behavior | `spec/05_components_agents_permissions_design.md`, `src-rust/crates/query/src/agent_tool.rs` | good orchestration reference |
| Command | strong | named command registry | `spec/02_commands.md`, `src-rust/crates/commands/src/lib.rs` | narrower than TS but explicit |
| Tool | strong | Rust tool registry and specialized tool files | `spec/03_tools.md`, `src-rust/crates/tools/src/lib.rs` | strong clean-room tool mapping |
| Skill | partial | bundled skill and skill tool support | `src-rust/crates/tools/src/skill_tool.rs`, `src-rust/crates/tools/src/bundled_skills.rs` | lacks TS skill breadth |
| Task | partial | task and scheduler slices | `src-rust/crates/tools/src/tasks.rs`, `src-rust/crates/query/src/cron_scheduler.rs` | compressed task model |
| Memory | partial | memdir and auto-dream features | `src-rust/crates/core/src/memdir.rs`, `src-rust/crates/query/src/auto_dream.rs` | memory concepts visible, not full parity |
| Connector | partial | MCP and bridge crates | `spec/09_bridge_cli_remote.md`, `src-rust/crates/mcp/src/lib.rs`, `src-rust/crates/bridge/src/lib.rs` | clear connector semantics |
| Policy | partial | permissions design and core safety primitives | `spec/05_components_agents_permissions_design.md`, `src-rust/crates/core/src/lib.rs` | policy exists but ecosystem is thinner |
""",
    "03-specs-and-parity/source-derived-spec/mappings/instructkr-to-spec.md": """
# Mapping: claude-code-instructkr to unified runtime spec

| Spec object | Coverage level | Observed implementation surface | Evidence | Notes |
|---|---|---|---|---|
| Runtime | partial | Python and Rust runtime entrypoints | `src/main.py`, `src/runtime.py`, `rust/crates/rusty-claude-cli/src/main.rs` | architecture preserved, implementation compressed |
| Session | partial | query engine and session persistence | `src/query.py`, `src/query_engine.py`, `rust/crates/runtime/src/session.rs` | useful migration reference |
| Agent | partial | coordinator and task-oriented execution | `src/tasks.py`, `src/coordinator/`, `rust/crates/runtime/src/conversation.rs` | lacks full TS configuration depth |
| Command | partial | mirrored command inventories and Rust command crate | `src/commands.py`, `src/reference_data/commands_snapshot.json`, `rust/crates/commands/src/lib.rs` | command shape preserved better than behavior |
| Tool | partial | Python tool metadata and Rust tool crate | `src/tools.py`, `src/Tool.py`, `rust/crates/tools/src/lib.rs` | parity intentionally incomplete |
| Skill | partial | local skill surfaces and parity notes | `src/skills/`, `PARITY.md` | no full bundled-skill parity |
| Task | partial | Python task modules and Rust conversation loop | `src/task.py`, `src/tasks.py`, `rust/crates/runtime/src/conversation.rs` | task model exists but is lighter |
| Memory | minimal | memdir and session-store placeholders | `src/memdir/`, `src/session_store.py` | durable-memory system still thin |
| Connector | partial | remote runtime and MCP-related Rust modules | `src/remote_runtime.py`, `rust/crates/runtime/src/mcp.rs`, `rust/crates/runtime/src/remote.rs` | connector concepts survive |
| Policy | partial | Python and Rust permissions surfaces plus parity report | `src/permissions.py`, `rust/crates/runtime/src/permissions.rs`, `PARITY.md` | policy breadth below TS |
""",
}


EXAMPLES = {
    "03-specs-and-parity/source-derived-spec/examples/openclaw-agent.example.json": {"id": "openclaw-coder", "agent_type": "worker", "source": "openclaw", "model": "claude-4.6", "effort": "high", "tools": ["shell", "file_read", "file_edit", "mcp_resources"], "skills": ["repo-audit", "task-execution"], "permission_mode": "ask", "memory_scope": "project", "isolation": "workspace", "max_turns": 40, "hooks": ["pre_tool_use", "post_tool_use"], "required_connectors": ["filesystem", "github", "local-mcp"]},
    "03-specs-and-parity/source-derived-spec/examples/codex-skill.example.json": {"name": "openai-docs", "source": "codex", "description": "Choose official OpenAI documentation paths and summarize the implementation guidance for the active task.", "when_to_use": "Use when the task depends on official OpenAI API or model documentation.", "allowed_tools": ["openai_docs", "web_search"], "argument_hint": "Prefer the product area or model family as the main argument.", "model_override": None, "execution_context": "interactive-session", "path_conditions": ["docs/**", "api/**"], "hooks": ["pre_skill_load"]},
    "03-specs-and-parity/source-derived-spec/examples/task-lifecycle.example.json": {"id": "task-ultraplan-001", "type": "remote-plan", "owner_agent": "coordinator", "origin": "slash-command:/plan", "input": {"goal": "Design an OpenClaw runtime migration slice", "budget_minutes": 30}, "status": "running", "progress": 45, "result_ref": "remote://ultraplan/task-ultraplan-001", "notification_policy": "notify-on-complete", "resume_strategy": "poll-and-resume"},
}


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_concept_doc(obj: dict) -> str:
    return f"""
# {obj['title']}

## Purpose

{obj['purpose']}

## Core responsibilities

{bullet_list(obj['responsibilities'])}

## Required fields

{bullet_list([f'`{field}`' for field in obj['fields']])}

## Lifecycle or execution semantics

{bullet_list(obj['semantics'])}

## Relationships to other objects

{bullet_list(obj['relationships'])}

## Evidence from tracked repositories

{bullet_list(obj['evidence'])}

## Open parity notes

{bullet_list(obj['parity'])}
"""


def main() -> None:
    write("README.md", ROOT_README)
    write("03-specs-and-parity/README.md", SPEC_LAYER_README)
    write("06-verification/README.md", VERIFICATION_README)
    write("04-diffs-and-indexes/provenance-index/provenance.md", PROVENANCE)
    write("04-diffs-and-indexes/manifests/current-comparison-summary.md", CURRENT_COMPARISON_SUMMARY)
    for rel, content in MANIFESTS.items():
        write(rel, content)
    for rel, content in STRUCTURE_DIFFS.items():
        write(rel, content)
    write("04-diffs-and-indexes/symbol-index/runtime-capability-index.md", RUNTIME_CAPABILITY_INDEX)
    write("03-specs-and-parity/module-matrices/repository-capability-matrix.md", REPOSITORY_CAPABILITY_MATRIX)
    write("03-specs-and-parity/source-derived-spec/README.md", SOURCE_DERIVED_SPEC_README)
    for name, data in OBJECTS.items():
        write(f"03-specs-and-parity/source-derived-spec/concepts/{name}.md", build_concept_doc(data))
    for name, schema in SCHEMAS.items():
        write_json(f"03-specs-and-parity/source-derived-spec/schemas/{name}.schema.json", schema)
    for rel, content in MAPPINGS.items():
        write(rel, content)
    for rel, payload in EXAMPLES.items():
        write_json(rel, payload)
    print("Phase 1 and Phase 2 artifacts generated.")


if __name__ == "__main__":
    main()
