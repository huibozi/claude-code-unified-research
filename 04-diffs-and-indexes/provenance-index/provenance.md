# Provenance Index

| Source | Upstream | Commit | Type | Notes |
|---|---|---|---|---|
| claude-code-source | `alex000kim/claude-code` | `1becaba` | raw baseline | primary factual baseline |
| claude-code-source-leak | `alex000kim/claude-code` | `1becaba` | duplicate raw baseline | `src` tree is identical to `claude-code-source` |
| claude-code-Kuberwastaken | `Kuberwastaken/claude-code` | `45f7ac9` | clean-room rewrite | Rust rewrite with `spec/` reference layer |
| claude-code-instructkr | `instructkr/claude-code` | `9ade3a7` | parity workspace | Python and Rust migration workspace |

## Notes

- Raw baselines are tracked as evidence but not published as code in this repository.
- Duplicate baselines are retained only as provenance facts.
