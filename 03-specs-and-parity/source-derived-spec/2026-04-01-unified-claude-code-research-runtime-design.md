# Unified Claude Code Research And Runtime Spec Design

Date: 2026-04-01

## Goal

Create a unified research repository that preserves every useful detail from the available Claude Code source materials without merging incompatible implementations. Use that repository to derive a single runtime specification that can later guide OpenClaw, Codex, and Claude environment redesign work.

This design intentionally separates:

- raw source baselines
- clean-room rewrites and ports
- derived specifications
- parity and comparison outputs
- downstream migration blueprints

## Scope

This design covers two sequential phases:

1. Unified research repository
2. Unified runtime specification

This design does not yet cover:

- implementation of a new combined runtime
- code merging between TypeScript, Python, and Rust trees
- direct OpenClaw or Codex runtime edits
- packaging or release engineering

## Inputs

The current working comparison set is:

- `claude-code-source`
- `claude-code-source-leak`
- `claude-code-Kuberwastaken`
- `claude-code-instructkr`

Observed facts from the current local analysis:

- `claude-code-source` and `claude-code-source-leak` point to the same upstream and the `src` trees are identical.
- `claude-code-source` is the largest factual baseline and should be treated as the primary implementation reference.
- `claude-code-Kuberwastaken` is a clean-room Rust rewrite with a useful `spec/` layer.
- `claude-code-instructkr` is a parity and migration workspace that preserves architectural shape while changing implementation language and organization.

## Phase 1

### Objective

Build a unified research repository that keeps all source material in one place while preserving provenance, duplication information, and clear separation between factual baseline and derivative work.

### Repository shape

```text
claude-code-unified-research/
|-- 01-raw-baselines/
|   |-- alex000kim-source/
|   |-- alex000kim-source-leak/
|   `-- README.md
|-- 02-clean-room-rewrites/
|   |-- kuberwastaken-rust/
|   |-- instructkr-port/
|   `-- README.md
|-- 03-specs-and-parity/
|   |-- source-derived-spec/
|   |-- parity-reports/
|   |-- module-matrices/
|   `-- README.md
|-- 04-diffs-and-indexes/
|   |-- manifests/
|   |-- structure-diffs/
|   |-- symbol-index/
|   `-- provenance-index/
|-- 05-migration-blueprints/
|   |-- openclaw/
|   |-- codex/
|   |-- claude/
|   `-- shared-runtime/
|-- 06-verification/
|   |-- checks/
|   |-- snapshots/
|   `-- reports/
`-- README.md
```

### Layer rules

`01-raw-baselines/`

- Stores raw baselines only.
- Defaults to read-only handling.
- No derived summaries or edits belong here.
- Duplicate baselines are allowed only if explicitly labeled.

`02-clean-room-rewrites/`

- Stores clean-room rewrites, ports, and parity workspaces.
- Must preserve original project identity and provenance.
- May include implementation-specific documentation.

`03-specs-and-parity/`

- Stores concepts, parity analysis, and architectural reductions.
- Must reference baseline evidence instead of embedding copied source.

`04-diffs-and-indexes/`

- Stores generated or semi-generated manifests, matrices, symbol maps, and source inventories.
- Serves as the machine-readable bridge between sources and design.

`05-migration-blueprints/`

- Stores downstream plans for OpenClaw, Codex, and Claude environment work.
- Cannot overwrite or reinterpret provenance established upstream.

`06-verification/`

- Stores completion checks, health reports, snapshots, and validation outputs.
- Used as the gate for declaring a phase complete.

### Required metadata

Each imported source should have a provenance record containing at minimum:

- local path
- upstream URL
- current commit
- source type
- acquisition date
- read-only policy
- duplication status
- notes

### Required generated outputs

For each imported source, generate and store:

- top-level directory tree
- code file count
- line count
- key module inventory
- keyword surface summary
- structural notes

### Completion gate for Phase 1

Phase 1 is complete only when:

- every imported source has provenance metadata
- duplicate baselines are explicitly marked
- source manifests are present
- evidence can be traced from every derived conclusion back to a source
- verification reports indicate repository health is green

## Phase 2

### Objective

Derive one runtime specification from the research repository so future OpenClaw, Codex, and Claude work can target the same conceptual model instead of re-inventing incompatible abstractions.

### Core objects

The runtime specification is centered on ten objects:

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

### Modular grouping

The unified runtime spec is organized into five groups:

- `core-runtime`
- `execution`
- `integration`
- `governance`
- `knowledge`

`core-runtime`

- Runtime
- Session
- event and state semantics

`execution`

- Agent
- Command
- Tool
- Skill
- Task

`integration`

- Connector
- MCP
- bridge and channel semantics

`governance`

- Policy
- permission
- audit

`knowledge`

- Memory
- parity
- indexes
- specifications

### Extension families

Runtime-specific declaration families should attach to the ten core objects through adapter-aware fields rather than silently expanding the object model.

Current tracked extension families are:

- command settings surfaces attached to `Command`
- routing bindings attached to `Policy`
- channel connectors attached to `Connector`
- plugin-backed provider metadata attached near `Connector`

### Spec directory shape

```text
03-specs-and-parity/
|-- source-derived-spec/
|   |-- README.md
|   |-- concepts/
|   |   |-- runtime.md
|   |   |-- session.md
|   |   |-- agent.md
|   |   |-- command.md
|   |   |-- tool.md
|   |   |-- skill.md
|   |   |-- task.md
|   |   |-- memory.md
|   |   |-- connector.md
|   |   `-- policy.md
|   |-- schemas/
|   |   |-- runtime.schema.json
|   |   |-- session.schema.json
|   |   |-- agent.schema.json
|   |   |-- command.schema.json
|   |   |-- tool.schema.json
|   |   |-- skill.schema.json
|   |   |-- task.schema.json
|   |   |-- memory.schema.json
|   |   |-- connector.schema.json
|   |   `-- policy.schema.json
|   |-- mappings/
|   |   |-- source-to-spec.md
|   |   |-- kuber-to-spec.md
|   |   `-- instructkr-to-spec.md
|   |-- extensions/
|   |   `-- runtime-extension-families.md
|   `-- examples/
|       |-- openclaw-agent.example.json
|       |-- openclaw-command-settings.example.json
|       |-- openclaw-channel-connector.example.json
|       |-- openclaw-routing-policy.example.json
|       |-- codex-skill.example.json
|       `-- task-lifecycle.example.json
```

### Minimum fields

`Runtime`

- `id`
- `name`
- `version`
- `registries`
- `state_store`
- `policy_store`
- `connector_registry`
- `feature_flags`

Optional support fields:
- `compatibility_surfaces`

`Session`

- `id`
- `runtime_id`
- `agent_id`
- `cwd`
- `mode`
- `model`
- `permission_snapshot`
- `memory_refs`
- `transcript_ref`
- `status`

Optional support fields:
- `decl_generation`
- `snapshot_ref`

`Agent`

- `id`
- `agent_type`
- `source`
- `model`
- `compute_profile`
- `tools`
- `skills`
- `permission_mode`
- `memory_scope`
- `isolation`
- `max_turns`
- `hooks`
- `required_connectors`

Optional support fields:
- `name`
- `disallowed_tools`
- `adapter_notes`

`Command`

- `source`
- `kind`
- `description`

Variant A: named entrypoint

- `name`
- `aliases`
- `input_contract`
- `handler_ref`
- `enabled_when`

Variant B: settings surface

- `id`
- `adapter_shape`
- `settings_payload`

Optional support fields:
- `adapter_notes`

`Tool`

- `name`
- `source`
- `description`
- `input_schema`
- `output_schema`
- `permission_requirements`
- `is_concurrency_safe`
- `side_effect_level`

`Skill`

- `name`
- `source`
- `description`
- `when_to_use`
- `allowed_tools`
- `argument_hint`
- `model_override`
- `execution_context`
- `path_conditions`
- `hooks`

`Task`

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

`Memory`

- `id`
- `scope`
- `owner`
- `source`
- `content_ref`
- `last_updated_at`
- `retention_policy`

`Connector`

- `id`
- `kind`
- `transport`
- `capabilities`
- `auth_mode`
- `resource_contracts`
- `health_state`

Optional support fields:
- `description`
- `auth_refs`
- `adapter_config`
- `provider_plugin`
- `binding_refs`
- `adapter_notes`

`Policy`

- `id`
- `description`
- `scope`
- `priority`
- `allow_rules`
- `deny_rules`
- `ask_rules`
- `danger_filters`
- `audit_requirements`

Optional support fields:
- `routing_rules`
- `adapter_notes`

### Mapping requirements

The runtime spec is not considered valid until at least these mapping documents exist:

- `source-to-spec.md`
- `kuber-to-spec.md`
- `instructkr-to-spec.md`

Each mapping should record:

- what exists
- what is partial
- what is missing
- what is semantically different
- where evidence came from

### Completion gate for Phase 2

Phase 2 is complete only when:

- all ten core objects are documented
- all schema files parse and validate
- mappings exist for all current sources
- examples validate against schema
- terminology is consistent across concepts and schema
- semantic conflicts are recorded instead of silently flattened

## Verification

### Repository verification

Phase 1 verification should include:

- `verify-provenance`
- `verify-readonly-baselines`
- `verify-duplicate-baselines`
- `verify-manifest-completeness`
- `verify-cross-reference-links`

### Runtime spec verification

Phase 2 verification should include:

- concept completeness
- schema validation
- mapping coverage
- example validation
- terminology consistency
- conflict reporting
- downstream consumability review

### Report outputs

Expected reports include:

- `research-repo-health.md`
- `runtime-spec-health.md`
- `mapping-coverage.md`
- `parity-conflicts.md`

## Milestones

1. Create unified research repository skeleton.
2. Register and freeze source baselines.
3. Generate source manifests and indexes.
4. Write unified runtime concepts and schema.
5. Create source-to-spec mapping documents.
6. Run verification and publish health reports.

## Recommended next step after approval

After this design document is approved, create a detailed implementation plan for:

- building the repository skeleton
- ingesting sources with provenance
- generating indexes
- authoring the runtime spec files
- defining validation scripts and acceptance checks

## Notes

- `claude-code-source` should remain the primary factual baseline.
- `claude-code-source-leak` should be tracked as a duplicate baseline unless later evidence shows meaningful divergence.
- `Kuberwastaken` is most useful as a clean-room spec and Rust structure reference.
- `instructkr` is most useful as a parity and migration methodology reference.
- This design intentionally prefers provenance and traceability over early implementation speed.
