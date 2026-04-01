# Current Comparison Summary

## Baselines

- `claude-code-source`: about 1902 source files and about 477439 lines in the captured source tree
- `claude-code-source-leak`: same upstream and identical `src` tree as `claude-code-source`

## Rewrites

- `claude-code-Kuberwastaken`: centers on a clean-room Rust rewrite and a `spec/` layer
- `claude-code-instructkr`: centers on parity tracking and migration structure, with Python and Rust workspaces

## Comparison takeaways

- Use `claude-code-source` as the primary factual implementation baseline.
- Use `Kuberwastaken` as the strongest clean-room spec and Rust structure reference.
- Use `instructkr` as the strongest parity and migration methodology reference.
