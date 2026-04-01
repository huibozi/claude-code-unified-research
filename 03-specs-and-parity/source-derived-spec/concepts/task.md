# Task

## Purpose

Represents asynchronous or background execution units such as child-agent runs, remote jobs, or scheduled work.

## Core responsibilities

- Track ownership, input, progress, result location, and resume strategy.
- Separate long-running work from the main foreground session.
- Support notification and recovery behavior.

## Required fields

- `id`
- `type`
- `owner_agent`
- `origin`
- `input`
- `status`
- `progress`
- `result_ref`
- `notification_policy`
- `resume_strategy`

## Lifecycle or execution semantics

- Tasks may be local, remote, or delegated to other agents.
- A task lifecycle should be inspectable and resumable from recorded state.
- Notification policy is part of the runtime contract for background work.

## Relationships to other objects

- Created by Session or Command flows and usually owned by an Agent.
- Can require Connector access for remote or MCP-backed execution.
- Often writes into Memory or transcript outputs after completion.

## Evidence from tracked repositories

- `claude-code-source`: `src/tasks/LocalAgentTask/LocalAgentTask.tsx`, `src/tasks/RemoteAgentTask/RemoteAgentTask.tsx`, `src/commands/ultraplan.tsx`
- `claude-code-Kuberwastaken`: `src-rust/crates/tools/src/tasks.rs`, `src-rust/crates/query/src/cron_scheduler.rs`
- `claude-code-instructkr`: `src/task.py`, `src/tasks.py`, `rust/crates/runtime/src/conversation.rs`
- Research layer: `04-diffs-and-indexes/symbol-index/runtime-capability-index.md`

## Open parity notes

- The source baseline contains the clearest local-versus-remote task split.
- Kuberwastaken and instructkr both keep the task idea alive but compress its lifecycle details.
