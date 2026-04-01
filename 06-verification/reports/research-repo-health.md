# Research Repo Health

Status: green

Date: 2026-04-01

Verification command:

```powershell
python .\06-verification\checks\verify_phase1_phase2.py
```

## Phase 1 checks

- provenance records exist for all tracked repositories
- duplicate baseline is explicitly marked
- per-repository manifests exist for `source`, `source-leak`, `Kuberwastaken`, and `instructkr`
- structure diff notes exist for the three comparison pairs
- capability index and repository capability matrix exist
- raw leaked source code is still excluded from this published repository

## Assessment

Phase 1 is complete. The repository now has a traceable evidence layer for the current comparison set, and every derived runtime-spec conclusion can point back to recorded provenance or comparison artifacts.
