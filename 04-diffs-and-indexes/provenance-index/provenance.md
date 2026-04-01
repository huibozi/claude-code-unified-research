# Provenance Index

| Source | Local path | Upstream | Commit | Acquisition date | Type | Read-only handling | Duplication status | Publication status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `claude-code-source` | `C:\Users\huibozi\claude-code-source` | `https://github.com/alex000kim/claude-code.git` | `1becaba` | `2026-04-01` | raw baseline | yes | canonical primary baseline | metadata only | largest factual implementation snapshot, only `src/` plus git metadata |
| `claude-code-source-leak` | `C:\Users\huibozi\claude-code-source-leak` | `https://github.com/alex000kim/claude-code.git` | `1becaba` | `2026-04-01` | duplicate raw baseline | yes | duplicate of `claude-code-source` | metadata only | `src` tree verified identical to canonical baseline |
| `claude-code-Kuberwastaken` | `C:\Users\huibozi\claude-code-forks\claude-code-Kuberwastaken` | `https://github.com/Kuberwastaken/claude-code.git` | `45f7ac9` | `2026-04-01` | clean-room rewrite | no | independent derivative | repo may be cited and linked | Rust rewrite with a strong `spec/` explanation layer |
| `claude-code-instructkr` | `C:\Users\huibozi\claude-code-forks\claude-code-instructkr` | `https://github.com/instructkr/claude-code.git` | `9ade3a7` | `2026-04-01` | parity workspace | no | independent derivative | repo may be cited and linked | Python-first porting workspace plus ongoing Rust parity work |

## Handling notes

- Raw baselines are tracked as evidence but not published as code in this repository.
- `claude-code-source-leak` is retained only to document duplication and provenance, not as an independent analytical source.
- Clean-room and parity repositories are treated as derivative research inputs with their own architectural value and their own gaps.
