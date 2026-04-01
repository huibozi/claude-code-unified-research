# Specs And Parity

This layer stores the unified runtime concepts, schemas, mappings, parity reports, and comparison matrices derived from the recorded sources.

## Subdirectories

- `source-derived-spec/`: canonical concept docs, JSON schemas, mappings, and examples
- `parity-reports/`: reserved for future deeper parity audits
- `module-matrices/`: cross-repository capability matrices and summaries

## Rules

- Reference evidence instead of embedding copied source.
- Keep conflicts visible instead of silently flattening them.
- Treat the source-derived spec as a semantic reduction of the evidence layer, not a replacement for it.
