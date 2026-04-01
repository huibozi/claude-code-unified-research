# Structure Diff: claude-code-source vs claude-code-instructkr

## Summary

The primary source baseline is a direct TypeScript implementation snapshot. instructkr preserves much of the subsystem naming surface but moves implementation toward Python and Rust while tracking missing parity explicitly.

| Category | claude-code-source | claude-code-instructkr |
|---|---|---|
| Languages | TypeScript, TSX, JavaScript | Python, Rust |
| Counted code files | `1902` | `102` |
| Counted code lines | `513237` | `25201` |
| Subsystem-name preservation | native | intentionally mirrored |
| Gap tracking | implicit | explicit in `PARITY.md` |
| Migration guidance | indirect | strong |

## Structural differences

- instructkr keeps many familiar subsystem names under `src/` but shrinks them to a porting workspace.
- instructkr adds `reference_data/` snapshots, making parity auditing easier than in the raw source baseline.
- instructkr carries a second Rust runtime slice under `rust/crates/`, turning it into both a migration workspace and an implementation lab.
- instructkr is best used to plan staged migration work and to make missing parity visible.
