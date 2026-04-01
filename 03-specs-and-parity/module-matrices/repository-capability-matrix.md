# Repository Capability Matrix

Coverage meanings:

- `primary`: canonical implementation witness
- `strong`: substantial implementation or distilled behavior coverage
- `partial`: meaningful but incomplete coverage
- `minimal`: naming or placeholder coverage only
- `duplicate`: not an independent witness

| Runtime object | claude-code-source | claude-code-source-leak | claude-code-Kuberwastaken | claude-code-instructkr |
|---|---|---|---|---|
| Runtime | primary | duplicate | strong | partial |
| Session | primary | duplicate | strong | partial |
| Agent | primary | duplicate | strong | partial |
| Command | primary | duplicate | strong | partial |
| Tool | primary | duplicate | strong | partial |
| Skill | primary | duplicate | partial | partial |
| Task | primary | duplicate | partial | partial |
| Memory | primary | duplicate | partial | minimal |
| Connector | primary | duplicate | partial | partial |
| Policy | primary | duplicate | partial | partial |

## Notes

- `claude-code-source` is the canonical evidence base for every object.
- `claude-code-source-leak` confirms duplication only and should not affect coverage scoring.
- `claude-code-Kuberwastaken` is strongest on runtime, query, command, tool, and bridge abstractions.
- `claude-code-instructkr` is strongest on parity bookkeeping and migration scaffolding rather than full runtime breadth.
