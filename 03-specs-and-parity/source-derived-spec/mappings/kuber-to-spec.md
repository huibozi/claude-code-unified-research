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
