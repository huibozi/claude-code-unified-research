# Manifest: claude-code-source

## Identity

- Local path: `C:\Users\huibozi\claude-code-source`
- Upstream: `https://github.com/alex000kim/claude-code.git`
- Commit: `1becaba`
- Role: primary factual implementation baseline

## Tree shape

Top-level entries:

- `.git`
- `src`

Primary `src/` module surfaces:

- `assistant`, `bootstrap`, `bridge`, `buddy`, `cli`, `commands`, `components`, `constants`, `context`, `coordinator`
- `entrypoints`, `hooks`, `ink`, `keybindings`, `memdir`, `migrations`, `moreright`, `native-ts`, `outputStyles`, `plugins`
- `query`, `remote`, `schemas`, `screens`, `server`, `services`, `skills`, `state`, `tasks`, `tools`, `types`, `upstreamproxy`, `utils`, `vim`, `voice`

## Counted scale

- Counted code files: `1902`
- Counted code lines: `513237`
- Extension mix: `.ts` `1332`, `.tsx` `552`, `.js` `18`

High-density directories:

- `src/commands`: `207` files
- `src/tools`: `184` files
- `src/services`: `130` files
- `src/skills`: `20` files
- `src/tasks`: `12` files
- `src/bridge`: `31` files

## Anchor evidence files

- `src/main.tsx`
- `src/entrypoints/cli.tsx`
- `src/QueryEngine.ts`
- `src/query.ts`
- `src/tools.ts`
- `src/Tool.ts`
- `src/skills/loadSkillsDir.ts`
- `src/tools/AgentTool/loadAgentsDir.ts`
- `src/services/mcp/client.ts`
- `src/services/tools/toolOrchestration.ts`
- `src/utils/permissions/permissionSetup.ts`
- `src/tasks/LocalAgentTask/LocalAgentTask.tsx`
- `src/tasks/RemoteAgentTask/RemoteAgentTask.tsx`
- `src/bridge/bridgeMain.ts`

## Why this repository matters

This tree is the behavioral source of truth for the research repo. It shows the widest command surface, the broadest tool registry, the most complete skill pipeline, the strongest permissions layer, and the clearest task and bridge implementations.
