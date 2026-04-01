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
