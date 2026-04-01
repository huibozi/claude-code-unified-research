# Unified Claude Code Research

Research repository for studying Claude Code source artifacts, clean-room rewrites, parity work, and downstream runtime migration design.

This repository intentionally excludes raw leaked source code.

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
