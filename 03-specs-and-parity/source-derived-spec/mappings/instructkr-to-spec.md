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
