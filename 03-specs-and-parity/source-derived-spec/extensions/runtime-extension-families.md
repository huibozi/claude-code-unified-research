# Runtime Extension Families

## Purpose

Keep the unified runtime model centered on ten core objects while still giving runtime-specific declaration families a formal place to live.

These extensions do not expand the core object count. They attach to the existing objects through clearly defined adapter-aware fields.

## Current extension families

### 1. Command settings surfaces

Some runtimes do not expose one declaration file per named command. Instead, they expose one settings-shaped command control surface.

Current mapping:

- modeled as a `Command` variant with `adapter_shape = settings-surface`
- canonical example: OpenClaw `decl/commands/_settings.json`

## 2. Routing bindings

Some runtimes expose routing declarations that match an incoming channel or event and dispatch work to an agent.

Current mapping:

- modeled as `Policy`-adjacent routing extensions using `routing_rules`
- stable promoted routing fields include:
  - `match.channel`
  - `match.account`
  - `match.pattern`
  - `match.pattern_mode = literal | glob | regex`
  - `match.context`
  - `action.type = forward_to_agent`
  - `action.agent_id`
- canonical example: OpenClaw `decl/bindings/*/binding.json`

## 3. Channel connectors

Some runtimes expose channels with nested account, group, and auth-routing semantics that cannot be flattened cleanly into the base connector fields.

Current mapping:

- modeled as `Connector` variants with `kind = channel`
- nested runtime-specific fields remain under `adapter_config`
- channel-like adapter surfaces may carry runtime-owned sub-surfaces such as `accounts` or `groups`, but those names remain adapter examples rather than promoted shared fields
- channel-like adapter surfaces may reference shared connectors with `connector_refs[]`
- channel-like adapter surfaces may reference shared policies with `policy_refs[]`
- canonical example: OpenClaw `decl/channels/*/channel.json`

## 4. Plugin-backed providers

Some runtimes expose plugin entries that back connectors or capability surfaces without being a full transport object on their own.

Current mapping:

- modeled as connector-adjacent extension metadata through `provider_plugin`
- canonical example: OpenClaw `decl/plugins/*/plugin.json` feeding channel or provider surfaces

## Rules

- Core ten objects remain the semantic center of the spec.
- Extension families must identify which core object they attach to.
- Extension-specific nested config should stay in adapter fields rather than contaminating core fields.
- If an extension becomes broadly cross-runtime, promote it by revisiting the core model deliberately rather than silently expanding it.
