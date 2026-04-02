# Specs And Parity

This layer stores the unified runtime concepts, schemas, mappings, parity reports, and comparison matrices derived from the recorded sources.

## Subdirectories

- `source-derived-spec/`: canonical concept docs, JSON schemas, mappings, and examples
- `parity-reports/`: execution parity notes, semantic conflicts, and future deeper parity audits
- `module-matrices/`: cross-repository capability matrices and summaries

## Current parity reports

- `parity-reports/codex-phase1-execution-parity.md`: live Codex Phase 1 execution parity
- `parity-reports/openclaw-phase1-execution-parity.md`: live OpenClaw Phase 1 execution parity
- `parity-reports/openclaw-phase2-execution-parity.md`: live OpenClaw Phase 2 routing-surface execution parity
- `parity-reports/openclaw-phase3-execution-parity.md`: live OpenClaw Phase 3 memory-catalog execution parity

## Rules

- Reference evidence instead of embedding copied source.
- Keep conflicts visible instead of silently flattening them.
- Treat the source-derived spec as a semantic reduction of the evidence layer, not a replacement for it.
