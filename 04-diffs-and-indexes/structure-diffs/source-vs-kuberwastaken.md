# Structure Diff: claude-code-source vs claude-code-Kuberwastaken

## Summary

The primary source baseline is a large TypeScript implementation snapshot. Kuberwastaken is a much smaller Rust clean-room rewrite with an explicit spec layer that distills behavior before implementation.

| Category | claude-code-source | claude-code-Kuberwastaken |
|---|---|---|
| Languages | TypeScript, TSX, JavaScript | Rust |
| Counted code files | `1902` | `53` |
| Counted code lines | `513237` | `23847` |
| Behavioral truth | highest | derived |
| Reading speed | lowest | highest |
| Architectural reduction | implicit in code | explicit in `spec/` |

## Structural differences

- Source keeps nearly every subsystem under one very large `src/` tree.
- Kuberwastaken splits reasoning into `spec/` topics and a `src-rust/crates/` implementation tree.
- Kuberwastaken preserves many capability names but compresses or re-expresses implementation details.
- Kuberwastaken is strongest when used as an architecture reading aid, not as a parity oracle.
