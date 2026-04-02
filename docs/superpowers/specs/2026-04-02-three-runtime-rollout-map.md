# Three Runtime Rollout Map

Date: 2026-04-02

## Purpose

Provide one decision-oriented map across the three live downstream runtimes:

- `C:\Users\huibozi\.claude`
- `C:\Users\huibozi\.codex`
- `C:\Users\huibozi\.openclaw`

This document is not an external-facing narrative. It is a working decision tool that combines:

- current rollout state
- validation health
- architectural maturity
- adapter complexity
- the highest-value next move

## Current validated baseline

The current live validation baseline used for this map is:

- `.claude`: `validate_full.py` rerun on 2026-04-02, `exit_code = 2`, overall `warn`
- `.codex`: `validate_full_codex.py` rerun on 2026-04-02, `exit_code = 0`, overall `pass`
- `.openclaw`: `validate_full_openclaw.py` rerun on 2026-04-02, `exit_code = 0`, overall `pass`

This means the three lines are no longer hypothetical:

- Claude Code has the richest declaration surface but still carries historical-state backfill warnings.
- Codex has a clean canonical Phase 1 baseline with lower semantic breadth.
- OpenClaw has the most advanced routing surface and the heaviest adapter layer.

## Decision matrix

| Dimension | `.claude` | `.codex` | `.openclaw` |
|---|---|---|---|
| Canonical declaration roots | `agents / skills / commands / rules / mcp` | `agents / skills / rules / commands / mcp` | `agents / skills / commands / bindings / channels / gateway / plugins / cron / rules / mcp` |
| Declaration maturity | High | Medium | High |
| State normalization | High | Medium | Medium-high |
| Generated layer | Mature | Mature | Mature |
| Validation status | `warn` | `pass` | `pass` |
| Validation cause | historical backfill drift only | no current issues | no current issues |
| Routing surface maturity | Low-medium | Low | High |
| Connector / policy maturity | Medium | Low-medium | High |
| Memory maturity | Low | Low-medium | Low-medium |
| Adapter complexity | Medium | Low-medium | High |
| Runtime risk if changed | Medium | Low-medium | High |
| Best next step | clean historical traceability or widen compatibility | add memory and richer runtime semantics | deepen memory / runtime policy after routing success |

## Per-runtime snapshot

### 1. Claude Code

Current strengths:

- strongest declaration inventory of the three runtimes
- managed canonical roots for:
  - `agents = 9`
  - `commands = 15`
  - `rules = 8`
  - `skills = 7`
  - `mcp = 1`
- state normalization is already broad:
  - project views
  - session views
  - shell snapshots
  - history normalization
- compatibility mirroring is already in place and drift check is currently clean

Current constraint:

- the line still validates as `warn`, not `pass`
- the warnings are not declaration errors
- the warnings are historical traceability gaps:
  - `3` session records could not be mapped back to current declaration ids
  - `15` history lines could not be backfilled with `decl_generation`

Interpretation:

- `.claude` is the most complete declarative runtime config layer
- but it is not the cleanest decision target for a new feature push right now
- the remaining value is more in cleanup and fidelity than in unlocking a new subsystem

### 2. Codex

Current strengths:

- canonical Phase 1 baseline is clean and low-risk
- current validation is fully green:
  - `decl = pass`
  - `state = pass`
  - `full = pass`
- state normalization is simple and contained:
  - session index
  - SQLite metadata index
- adapter complexity is still relatively low

Current constraint:

- semantic breadth is still narrow compared with `.claude` and `.openclaw`
- routing and channel semantics are still thin
- `memories/` exists as a native root but remains effectively unused
- most value from Codex now lies in deepening capability, not in more decl-state cleanup

Interpretation:

- `.codex` is the cleanest place to add the next isolated subsystem
- especially if we want a lower-risk implementation target
- but it is not the best place if the goal is to learn more about rich multi-surface runtime semantics

### 3. OpenClaw

Current strengths:

- now has the richest live routing surface of the three runtimes
- current validation is fully green:
  - `decl = pass`
  - `state = pass`
  - `full = pass`
- canonical routing graph is no longer implicit
- current managed counts:
  - `agents = 6`
  - `skills = 2`
  - `commands = 1`
  - `bindings = 3`
  - `channels = 3`
  - `gateway = 1`
  - `plugins = 3`
  - `cron = 1`
  - `rules = 3`
  - `mcp = 3`

Current constraint:

- adapter complexity is the highest of the three runtimes
- one live binding surface required a synthetic canonical internal channel (`tailscale`)
- provider connector discovery spans multiple native config surfaces
- routing policy refs had to be materialized canonically because the native runtime expresses them only implicitly

Interpretation:

- `.openclaw` is currently the best source of new semantic learning
- it is also the most dangerous runtime to change casually
- after Phase 2, it has become the strongest candidate for the next "meaningful architecture" phase rather than another decl-state cleanup phase

## Cross-runtime reading

### What is already solved across all three lines

- canonical `decl / state / generated` layering exists in practice
- registry and snapshot generation are no longer theoretical
- `compute_profile` and compatibility-surface semantics have been proven useful
- adapter-aware declaration work is viable without replacing the live runtime config surfaces

### What is solved in some lines but not all

- broad declaration inventory:
  - strongest in `.claude`
  - moderate in `.openclaw`
  - still selective in `.codex`
- routing surface:
  - strongest in `.openclaw`
  - not yet a major layer in `.claude` or `.codex`
- connector / policy linking:
  - strongest in `.openclaw`
  - partial in `.claude`
  - thinner in `.codex`

### What is still open across the portfolio

- canonical memory integration is still incomplete everywhere
- historical traceability is still imperfect in `.claude`
- `.codex` still lacks a richer second-wave runtime surface
- `.openclaw` still carries the highest adapter burden and therefore needs careful scoping per phase

## Portfolio recommendation

If the next move is chosen for maximum architectural learning value, the recommendation is:

1. `OpenClaw Phase 3`
2. `Codex Phase 2`
3. `Claude cleanup / traceability hardening`

If the next move is chosen for minimum implementation risk, the recommendation is:

1. `Codex Phase 2`
2. `Claude cleanup / traceability hardening`
3. `OpenClaw Phase 3`

Given the work completed so far, the best blended recommendation is:

1. **Use OpenClaw as the primary next design target**
2. **Use Codex as the secondary low-risk proving ground**
3. **Treat Claude Code as the reference-grade baseline that now mostly needs traceability cleanup, not a new semantic frontier**

## Why OpenClaw is the strongest next design target

- It now has the richest validated routing surface.
- It forced the most useful adapter clarifications back into the unified spec.
- It is the only line where `bindings + channels + gateway + rules + connectors` already form one validated declaration graph.
- The next major unresolved surface there is meaningful:
  - memory
  - deeper runtime policy
  - connector/provider semantics beyond Phase 2 routing

That makes OpenClaw the best place to learn something new, not just to tidy what already exists.

## Why Codex is still strategically important

- It is the cleanest low-risk line.
- It can absorb proven semantics after OpenClaw makes them real.
- It is the best candidate for validating whether a newly learned concept is genuinely portable or only adapter-local.

In practice, this means:

- OpenClaw should lead semantic exploration
- Codex should follow as the portability check

## Why Claude Code should not lead the next phase

- Claude Code is already the strongest declarative baseline.
- Its current warnings are historical-traceability warnings, not architecture failures.
- A new phase there is less likely to reveal fresh runtime semantics than a focused cleanup phase or a later consolidation phase.

This does not make Claude unimportant. It makes it the baseline to preserve while the other two runtimes continue teaching us where the shared model still needs to grow.

## Recommended next decision

The strongest next move is:

- write `OpenClaw Phase 3` as a memory-and-runtime-policy phase

The fallback if we want lower implementation risk is:

- write `Codex Phase 2` first and use it to prove the next portable memory layer

## Summary

The three rollout lines are no longer at the same stage:

- `.claude` is the most complete declaration baseline
- `.codex` is the cleanest low-risk implementation baseline
- `.openclaw` is the richest semantic frontier

That makes the portfolio strategy clear:

- preserve `.claude`
- use `.codex` to stabilize portable ideas
- use `.openclaw` to discover the next important ones
