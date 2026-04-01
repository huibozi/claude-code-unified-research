# Mapping Coverage

Date: 2026-04-01

## Coverage summary

| Repository | Objects mapped | Dominant coverage level | Notes |
|---|---:|---|---|
| `claude-code-source` | 10 | primary | canonical reference for every runtime object |
| `claude-code-Kuberwastaken` | 10 | strong / partial | strongest on runtime, query, command, tool, and bridge abstractions |
| `claude-code-instructkr` | 10 | partial / minimal | strongest on migration shape and parity bookkeeping |

## Interpretation

- Mapping coverage is complete for all three non-duplicate repositories.
- Coverage does not imply parity; it only means every spec object has a documented evidence path in each mapped repository.
- The duplicate `claude-code-source-leak` baseline is intentionally excluded from mapping because it does not add independent implementation evidence.
