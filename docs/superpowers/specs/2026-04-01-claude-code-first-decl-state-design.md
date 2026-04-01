# Claude Code-First Decl And State Layer Design

Date: 2026-04-01

## Goal

Redesign the local Claude Code runtime directory at `C:\Users\huibozi\.claude` into a declarative configuration layer plus a separated runtime-state layer, without breaking compatibility with the official Claude Code runtime that still expects the legacy top-level paths.

This design treats `~/.claude` as the first concrete downstream consumer of the unified runtime spec already captured in the research repository.

## Scope

This design covers:

1. declarative layout for `agents`, `skills`, `commands`, `rules`, and `mcp`
2. state-layer boundaries for `sessions`, `projects`, `history`, snapshots, cache, telemetry, and debug artifacts
3. generated registries, reports, and snapshots
4. validation, drift detection, and migration sequencing

This design does not yet cover:

- direct modification of the official Claude Code executable
- `.codex` or `.openclaw` migration work
- adapter implementation details for every existing Claude Code feature gate

## Target

Current active local runtime root:

- `C:\Users\huibozi\.claude`

Observed current top-level surfaces include:

- `agents`
- `commands`
- `plugins`
- `rules`
- `sessions`
- `skills`
- `projects`
- `cache`
- `debug`
- `telemetry`
- `shell-snapshots`
- `statsig`
- runtime settings files and caches

## Design Principles

- declaration and runtime state must be separated
- declaration is the stable fact source
- runtime state is a derived operational byproduct
- generated artifacts must remain disposable
- compatibility with the existing top-level Claude Code layout must be preserved during migration
- downstream runtimes should be able to map this layout into the unified runtime objects: `Agent`, `Skill`, `Command`, `Policy`, and `Connector`

## Section 1: Top-Level Architecture

The local Claude Code directory is redefined into two semantic layers and one generated layer.

### A. Declaration layer

This layer expresses how the system should behave.

It contains:

- `agents/`
- `skills/`
- `commands/`
- `rules/`
- `mcp/`

These directories must be schema-valid, indexable, and mappable to the unified runtime spec.

### B. State layer

This layer stores what happened at runtime.

It contains:

- `sessions/`
- `projects/`
- `history.jsonl`
- `shell-snapshots/`
- `cache/`
- `telemetry/`
- `statsig/`
- `debug/`
- other runtime-local caches or lock files

These directories are not fact sources. They are runtime residue, operational history, or cache material.

### C. Generated layer

This layer stores registries, reports, and snapshots derived from the declaration and state layers.

It is disposable and never hand-edited.

## Section 2: Declaration Layer Schema

The declaration layer is normalized into directory-scoped units. Each unit is one declarative object with one stable metadata file as its entrypoint.

### Agents

Suggested shape:

```text
decl/agents/
  coder/
    agent.json
    prompt.md
    hooks.json
```

`agent.json` minimum fields:

- `id`
- `description`
- `model`
- `compute_profile`
- `tools`
- `skills`
- `permission_mode`
- `memory_scope`
- `isolation`
- `max_turns`
- `required_mcp_servers`

Rules:

- `compute_profile` replaces any Claude Code-specific `effort` concept in the core schema
- `compute_profile` allowed values: `low | balanced | high`
- Claude Code-specific effort values belong in an adapter layer, not in the core declaration schema
- `isolation` allowed values: `none | sandboxed | container`

### Skills

Suggested shape:

```text
decl/skills/
  research-web/
    skill.json
    skill.md
```

`skill.json` minimum fields:

- `id`
- `description`
- `when_to_use`
- `allowed_tools`
- `argument_hint`
- `model_override`
- `path_conditions`
- `hooks`

Rules:

- `skill.json` is machine-facing and defines behavior
- `skill.md` is human-facing and stores scenarios, caveats, and examples
- `skill.md` must not duplicate fields that already exist in `skill.json`
- `description` stays concise and canonical in `skill.json`
- `id` is the unique identifier used by state and registry references
- `name` may exist as an optional display label, but it is not the stable identity field

### Commands

Suggested shape:

```text
decl/commands/
  review/
    command.json
    README.md
```

`command.json` minimum fields:

- `name`
- `aliases`
- `description`
- `kind`
- `input_contract`
- `enabled_when`
- `handler_type`

`handler_type` allowed values:

- `builtin`
- `skill`
- `pipeline`
- `external`

### Rules

Suggested shape:

```text
decl/rules/
  safety/
    policy.json
    policy.md
```

`policy.json` minimum fields:

- `id`
- `scope`
- `priority`
- `allow_rules`
- `deny_rules`
- `ask_rules`
- `danger_filters`
- `audit_requirements`

Conflict rules:

- higher numeric `priority` wins
- if two rules have equal priority, default precedence is `deny > ask > allow`

### MCP

Suggested shape:

```text
decl/mcp/
  codex/
    connector.json
    README.md
```

`connector.json` minimum fields:

- `id`
- `kind`
- `transport`
- `command`
- `args`
- `env_policy`
- `capabilities`
- `auth_mode`
- `healthcheck`

Constraints:

- `kind`: `stdio | sse | http`
- `env_policy`: stores environment-variable names only, never secret values
- `auth_mode`: `none | token | oauth`

### Declaration registries

Registries remain derived artifacts, but their physical location is moved out of declaration directories and into the generated layer.

Registry outputs:

- `generated/registries/agents.registry.json`
- `generated/registries/skills.registry.json`
- `generated/registries/commands.registry.json`
- `generated/registries/rules.registry.json`
- `generated/registries/mcp.registry.json`

Registry update triggers:

- a unit directory is added or removed
- any declaration `*.json` metadata file changes
- the validation script is run explicitly

## Section 3: Declaration And State Boundaries

Core rule:

- declaration does not depend on state
- state references declaration in one direction only

That means:

- `agent.json` never contains `session_id`
- a session record may contain `agent_id`

Declaration is the stable fact source. State is the runtime byproduct.

### State categories

#### A. Run-bound state

Strongly tied to one run:

- `sessions/`
- `history.jsonl`
- `shell-snapshots/`

Recommended references:

- `agent_id`
- `command_id` when relevant
- `skill_id` or `skill_ids` when relevant
- `connector_id` or `connector_ids` when relevant
- timestamps

Cleanup policy:

- TTL-based cleanup
- or count-based retention limits

#### B. Project-bound state

Bound to a workspace or project:

- `projects/`

Recommended references:

- `agent_id` for default agent choice
- `connector_ids[]` for active project-level MCP usage

Cleanup policy:

- deleted with the project record or project removal workflow

#### C. System byproducts

Not worth wiring into the declaration graph:

- `cache/`
- `telemetry/`
- `statsig/`
- `debug/`
- `*.cache`
- `settings.local`

These do not reference declaration objects. They are operational noise and should stay isolated and disposable.

### Reference model

State records reference declaration objects by stable ids only.

- use ids
- do not use names
- do not use filesystem paths
- do not inline declaration content

Example:

```json
{
  "session_id": "sess_20260401_001",
  "agent_id": "coder",
  "skill_ids": ["research-web"],
  "connector_ids": ["codex"],
  "started_at": "2026-04-01T12:00:00Z",
  "ended_at": "2026-04-01T12:18:00Z"
}
```

If historical traceability requires more than ids, state may record:

- `decl_generation`
or
- `snapshot_ref`

This preserves traceability without copying declaration content into state.

### Boundary validation rule

Validation should scan state for references such as:

- `agent_id`
- `skill_id`
- `skill_ids`
- `command_id`
- `connector_id`
- `connector_ids`

If the referenced declaration object no longer exists:

- emit a `warning`
- do not emit an `error`

Historical state cannot always be rewritten, so stale references must be visible without breaking the entire runtime.

## Section 4: Physical Layout And Compatibility

Because the official Claude Code runtime still expects the legacy top-level layout under `~/.claude`, physical migration must preserve compatibility while establishing a new canonical structure.

### Canonical structure

Add three logical top-level groups under `~/.claude`:

```text
.claude/
  decl/
    agents/
    skills/
    commands/
    rules/
    mcp/
  state/
    sessions/
    projects/
    history/
    shell-snapshots/
    cache/
    telemetry/
    statsig/
    debug/
  generated/
    registries/
    reports/
    snapshots/
```

Semantics:

- `decl/` is the fact source
- `state/` is the normalized runtime-state view
- `generated/` stores disposable derived outputs

### Legacy compatibility paths

Keep the existing top-level directories for now:

- `agents/`
- `skills/`
- `commands/`
- `rules/`
- `mcp/`
- `sessions/`
- `projects/`
- and related legacy paths

These remain compatibility entrypoints for the official runtime. They are not the new semantic center of the system.

### Source of truth

People and validators should read:

- `decl/`
- `state/`
- `generated/`

The official runtime may continue to read:

- legacy top-level paths

### Mirror strategy

Declaration data is mirrored in one direction:

- `decl/` -> legacy top-level compatibility paths

The compatibility mirror must stamp generated files with provenance, for example:

- a top comment saying the file was generated
- or an internal `_source` field

That marker should explicitly say the file is mirrored from `decl/` and manual edits are not authoritative.

If a user manually edits a mirrored compatibility file:

- the next validation or sync pass should warn about drift
- the mirrored file should still be overwritten by the canonical declaration source

### Generated cleanup policy

`generated/` remains a disposable layer and must not become a hidden third state system.

Rules:

- `generated/registries/` is fully overwritten on every validation run
- `generated/reports/` is fully overwritten on every validation run
- `generated/snapshots/` keeps only the most recent `5` snapshots
- all `generated/` content must be ignored by git

## Section 5: Validate, Registry, Snapshot, And Migration Mechanisms

The system needs one operational mechanism set to keep declaration, state, and compatibility outputs coherent over time.

### Validation commands

Use three validation scopes:

- `validate decl`
- `validate state`
- `validate full`

#### `validate decl`

Checks:

- declaration schemas parse and validate
- required fields exist
- enum values are valid
- ids are unique
- declaration directory layout matches conventions
- declaration cross-references are resolvable

Typical examples:

- agent skill references must resolve
- required MCP server references must resolve
- rule priorities and scopes must be valid

#### `validate state`

Checks:

- state records parse
- state references point to known declaration ids when possible
- stale references are surfaced as warnings
- TTL and retention policies are checked
- stale generated snapshots can be pruned

#### `validate full`

Sequence:

1. run `validate decl`
2. run `validate state`
3. rebuild registries
4. build a declaration snapshot
5. backfill registry metadata
6. regenerate reports
7. prune generated snapshots to the most recent `5`
8. scan compatibility mirrors for drift and emit warnings

### Error levels

`error` conditions:

- invalid schema
- missing required fields
- duplicate ids
- malformed registry output
- failed snapshot build

`warning` conditions:

- stale historical references
- expired sessions
- compatibility-mirror drift
- old runtime byproducts pending cleanup

### Registry contents

Every generated registry entry should include at minimum:

- `id`
- `source_path`
- `hash`
- `last_updated_at`
- `decl_generation`

### Snapshot model

Snapshots record declaration-layer traceability and live under:

- `generated/snapshots/decl-<timestamp>.json`

Each snapshot should include:

- a `decl_generation` value
- generation timestamp
- generation reason such as `validate`, `sync`, or `migrate`
- registry hashes
- declaration-unit hashes

### Registry and snapshot generation order

To avoid circular dependence between registries and snapshots:

1. generate registries first with `decl_generation` unset or marked pending
2. generate the snapshot from registry hashes
3. derive the final `decl_generation`
4. backfill `decl_generation` into the registries

This order is fixed and should not vary across implementations.

### Migration sequence

Recommended order:

1. `inventory`
   - classify current top-level `.claude` contents into declaration, state, or byproduct buckets
2. `bootstrap`
   - create `decl/`, `state/`, and `generated/`
   - add git ignore rules for `generated/`
   - install schema and validation entrypoints
3. `import-decl`
   - normalize current top-level `agents`, `skills`, `commands`, `rules`, and `mcp` into `decl/`
   - assign or normalize stable ids
4. `mirror-decl`
   - regenerate legacy compatibility directories from `decl/`
   - stamp mirrored files with source markers
5. `import-state`
   - normalize `sessions`, `projects`, history, and shell snapshots into `state/`
   - for historical records that can be traced to the first declaration snapshot, write the initial `decl_generation` or `snapshot_ref`
   - for historical records that cannot be traced reliably, leave those fields empty and emit a warning during validation
   - keep legacy runtime entrypoints alive as needed
6. `steady-state`
   - users edit `decl/`
   - validation rebuilds `generated/`
   - compatibility mirrors remain disposable outputs

## Recommended Next Step

After approval, write a Phase 3 implementation plan that creates:

- the `decl/`, `state/`, and `generated/` directory skeleton in `~/.claude`
- declaration schemas for the five declaration directories
- validation scripts for declaration and state
- mirror generation for top-level compatibility paths
- drift detection and generated-layer cleanup routines

## Notes

- this design intentionally makes `decl/` the only authoritative configuration source
- the legacy top-level Claude Code directories are preserved for compatibility, not for authorship
- generated registries replace per-directory `_registry.json` files as the canonical index output location
- `generated/` is disposable by design and must never become a new persistent state authority
