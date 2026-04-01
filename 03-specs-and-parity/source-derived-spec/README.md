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
- `examples/`: schema-valid example payloads for downstream runtime work
- `2026-04-01-unified-claude-code-research-runtime-design.md`: the approved design record

## Reading order

1. Read `../module-matrices/repository-capability-matrix.md`
2. Read the concept file for the object you care about
3. Open the matching schema
4. Check the corresponding mapping table for source, Kuberwastaken, and instructkr
5. Use an example payload as the starting point for downstream runtime design
