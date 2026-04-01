# Parity Conflicts

Date: 2026-04-01

These conflicts are intentionally recorded instead of flattened away.

## Active semantic conflicts

1. `claude-code-source-leak` is a duplicate baseline, not an independent witness.
2. `claude-code-Kuberwastaken` is a clean-room rewrite with an explicit spec layer, so many implementation details are compressed relative to the raw source baseline.
3. `claude-code-instructkr` preserves architectural shape well, but `PARITY.md` still records meaningful gaps around plugins, hooks execution, CLI breadth, skills registry depth, structured transports, and the wider services ecosystem.
4. Memory depth differs materially across repositories: the source baseline is richest, Kuberwastaken makes consolidation legible, and instructkr remains comparatively thin.
5. Connector and bridge semantics survive across all repositories, but the concrete runtime plumbing differs enough that the unified spec must stay conceptual rather than implementation-specific.

## Resolution policy

- keep the source baseline as the behavioral truth source
- keep clean-room and parity repositories as derivative references, not replacements
- record compression or omission as a parity note instead of silently treating it as equivalent
