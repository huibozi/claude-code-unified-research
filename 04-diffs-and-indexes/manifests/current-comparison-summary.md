# Current Comparison Summary

## Repository scale snapshot

| Repository | Counted code files | Counted code lines | Dominant languages | Primary value |
|---|---:|---:|---|---|
| `claude-code-source` | 1902 | 513237 | TypeScript, TSX, JavaScript | primary factual implementation baseline |
| `claude-code-source-leak` | 1902 | 513237 | TypeScript, TSX, JavaScript | duplicate provenance baseline |
| `claude-code-Kuberwastaken` | 53 | 23847 | Rust | clean-room rewrite plus spec distillation |
| `claude-code-instructkr` | 102 | 25201 | Python, Rust | parity tracking and migration methodology |

## Top-level architectural takeaway

- `claude-code-source` is the closest thing to a ground-truth implementation snapshot.
- `claude-code-source-leak` does not add new implementation evidence because the `src/` tree is identical to `claude-code-source` at commit `1becaba`.
- `claude-code-Kuberwastaken` is the clearest clean-room reduction of the source into spec topics and Rust crate boundaries.
- `claude-code-instructkr` is the clearest example of how to preserve subsystem shape while porting into a new implementation language and maintaining parity notes.

## Most relevant module surfaces

- Primary source baseline: `src/commands`, `src/tools`, `src/services`, `src/skills`, `src/tasks`, `src/bridge`, `src/query`
- Kuberwastaken: `spec/`, `src-rust/crates/tools`, `src-rust/crates/query`, `src-rust/crates/commands`, `src-rust/crates/bridge`, `src-rust/crates/core`
- instructkr: `src/`, `src/reference_data/`, `rust/crates/runtime`, `rust/crates/tools`, `rust/crates/commands`, `PARITY.md`

## Immediate research guidance

- Use `claude-code-source` for behavioral truth and edge-case discovery.
- Use `claude-code-Kuberwastaken` for accelerated reading of architecture slices.
- Use `claude-code-instructkr` for parity bookkeeping and migration sequencing.
