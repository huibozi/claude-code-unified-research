# Manifest: claude-code-instructkr

## Identity

- Local path: `C:\Users\huibozi\claude-code-forks\claude-code-instructkr`
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
