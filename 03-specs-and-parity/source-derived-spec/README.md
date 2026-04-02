# Source-Derived Runtime Spec

This directory turns the recorded source evidence into one unified runtime model.

## Core objects

- Runtime
- Session
- Agent
- Command
- Tool
- Skill
- Task
- Memory
- Connector
- Policy

## Module groups

- `core-runtime`: Runtime, Session
- `execution`: Agent, Command, Tool, Skill, Task
- `integration`: Connector, MCP, bridge, transport semantics
- `governance`: Policy, permissions, audit
- `knowledge`: Memory, parity, indexes, spec maintenance

## Contents

- `concepts/`: semantic definitions for the ten objects
- `schemas/`: JSON Schema Draft 2020-12 contracts for the ten objects
- `mappings/`: source-to-spec alignment for the three non-duplicate repositories
- `extensions/`: runtime-specific extension families that attach to the ten-object model without expanding the core object count
- `examples/`: schema-valid example payloads for downstream runtime work
- `2026-04-01-unified-claude-code-research-runtime-design.md`: the approved design record

## Downstream feedback

Live downstream implementations in `~/.codex` and `~/.openclaw` feed back into this layer when they clarify real cross-runtime adapter needs.

Current clarified adapter semantics include:

- normalized `compute_profile` instead of runtime-specific reasoning-effort labels
- runtime compatibility surfaces that coexist with canonical declarations
- logical agent identities that may differ from physical runtime directories
- declaration snapshots and `decl_generation` metadata for state manifests
- command settings surfaces and routing/channel/plugin extension families carried through adapter-aware core objects

## Reading order

1. Read `../module-matrices/repository-capability-matrix.md`
2. Read the concept file for the object you care about
3. If the object participates in runtime-specific extension families, read `extensions/runtime-extension-families.md`
4. Open the matching schema
5. Check the corresponding mapping table for source, Kuberwastaken, and instructkr
6. Use an example payload as the starting point for downstream runtime design
