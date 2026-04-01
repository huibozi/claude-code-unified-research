# Manifest: claude-code-source-leak

## Identity

- Local path: `C:\Users\huibozi\claude-code-source-leak`
- Upstream: `https://github.com/alex000kim/claude-code.git`
- Commit: `1becaba`
- Role: duplicate provenance baseline

## Verified duplication status

- Top-level shape matches the canonical source snapshot: `.git`, `src`
- Counted code files: `1902`
- Counted code lines: `513237`
- `git diff --no-index --quiet src src` between this tree and `claude-code-source` returns identical for the `src/` tree

## Handling decision

This repository is retained only to document duplication and provenance. It should not be counted as an independent implementation witness in future capability or parity analysis.
