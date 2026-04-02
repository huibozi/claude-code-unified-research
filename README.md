# Unified Claude Code Research

Research repository for studying Claude Code source artifacts, clean-room rewrites, parity work, and downstream runtime migration design.

This repository intentionally excludes raw leaked source code. It stores provenance, comparison outputs, derived specifications, and migration planning artifacts only.

## Status

- Phase 1 research repository baseline: complete
- Phase 2 unified runtime specification baseline: complete
- Claude Code decl-state implementation baseline: complete
- Codex Phase 1 decl-state implementation baseline: complete
- OpenClaw Phase 1 decl-state implementation baseline: complete
- OpenClaw Phase 2 routing surface implementation baseline: complete
- Raw leaked source publication: intentionally excluded

## Key Documents

- `04-diffs-and-indexes/provenance-index/provenance.md`: source registry and handling policy
- `04-diffs-and-indexes/manifests/current-comparison-summary.md`: current comparison baseline
- `03-specs-and-parity/module-matrices/repository-capability-matrix.md`: cross-repository capability map
- `03-specs-and-parity/source-derived-spec/README.md`: unified runtime spec entrypoint
- `03-specs-and-parity/source-derived-spec/2026-04-01-unified-claude-code-research-runtime-design.md`: approved design record
- `docs/superpowers/specs/2026-04-02-three-runtime-rollout-map.md`: current decision map across Claude Code, Codex, and OpenClaw
- `docs/superpowers/specs/2026-04-01-codex-phase1-decl-state-mapping.md`: approved Codex Phase 1 mapping blueprint
- `docs/superpowers/plans/2026-04-02-openclaw-phase1-decl-state-implementation.md`: approved OpenClaw Phase 1 implementation plan
- `docs/superpowers/plans/2026-04-02-openclaw-phase2-routing-surface-implementation.md`: approved OpenClaw Phase 2 implementation plan
- `03-specs-and-parity/parity-reports/codex-phase1-execution-parity.md`: blueprint-to-runtime execution parity notes
- `03-specs-and-parity/parity-reports/openclaw-phase1-execution-parity.md`: OpenClaw Phase 1 runtime execution parity notes
- `03-specs-and-parity/parity-reports/openclaw-phase2-execution-parity.md`: OpenClaw Phase 2 routing-surface execution parity notes
- `06-verification/reports/codex-phase1-implementation-health.md`: Codex Phase 1 execution and verification evidence
- `06-verification/reports/openclaw-phase1-implementation-health.md`: OpenClaw Phase 1 execution and verification evidence
- `06-verification/reports/openclaw-phase2-implementation-health.md`: OpenClaw Phase 2 execution and verification evidence
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
