# Verification

This layer stores validation checks, health reports, and phase completion evidence.

## Entry points

- `checks/verify_phase1_phase2.py`: required Phase 1 and Phase 2 validation script
- `reports/research-repo-health.md`: repository evidence health
- `reports/runtime-spec-health.md`: runtime spec validation status
- `reports/codex-phase1-implementation-health.md`: live Codex Phase 1 execution and validation status
- `reports/openclaw-phase1-implementation-health.md`: live OpenClaw Phase 1 execution and validation status
- `reports/openclaw-phase2-implementation-health.md`: live OpenClaw Phase 2 execution and validation status
- `reports/openclaw-phase3-implementation-health.md`: live OpenClaw Phase 3 execution and validation status
- `reports/openclaw-phase4-implementation-health.md`: live OpenClaw Phase 4 execution and validation status
- `reports/openclaw-phase5-implementation-health.md`: live OpenClaw Phase 5 execution and validation status
- `reports/openclaw-phase6-implementation-health.md`: live OpenClaw Phase 6 execution and validation status
- `reports/mapping-coverage.md`: mapping coverage summary
- `reports/parity-conflicts.md`: unresolved semantic conflicts intentionally kept visible

## Rules

- Use this layer as the gate for marking work complete.
- Keep repository health and runtime-spec health separate when reporting.
- Treat validation output as evidence, not aspiration.
