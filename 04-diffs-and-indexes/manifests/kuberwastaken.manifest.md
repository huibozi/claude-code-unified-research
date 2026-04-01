# Manifest: claude-code-Kuberwastaken

## Identity

- Local path: `C:\Users\huibozi\claude-code-forks\claude-code-Kuberwastaken`
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
