# OpenClaw Phase 6 Shared Context / Joint Session Lite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade OpenClaw handoff execution from raw reference passing to auditable structured context relay by enriching runtime handoff payloads, generating deterministic session summaries, and declaring shared-write memory rules without sharing a live transcript.

**Architecture:** Keep `C:\Users\huibozi\.openclaw\decl\handoffs\` as the read-only fact source, but split Phase 6 data into two layers: declarative `context_transfer` templates in `decl\handoffs\*\handoff.json`, and realized context payloads in `state\handoff-events\events.jsonl` plus `state\sessions\summaries\`. Extend the existing `handoff-bridge` plugin so it can generate deterministic source-session summaries, compute a runtime `context_hash`, inject `prompt_prefix` into target runs, and preserve the rule that source and target agents keep separate sessions even when they share memory surfaces.

**Tech Stack:** OpenClaw native plugin SDK, Node.js ESM JavaScript, PowerShell 7+, Python 3.11, JSON Schema Draft 2020-12, OpenClaw CLI, live runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `C:\Users\huibozi\.openclaw\decl\handoffs\*.json` remains the read-only declaration layer; no runtime field is written back into those files.
- `C:\Users\huibozi\.openclaw\state\handoff-events\events.jsonl` and `index.json` remain the runtime audit layer for realized handoff execution.
- `C:\Users\huibozi\.openclaw\state\sessions\index.json` remains the normalized session surface; Phase 6 adds summaries beside it and does not rewrite live `agents\*\sessions\*.jsonl` transcripts.
- `C:\Users\huibozi\.openclaw\decl\memory\*.json` remains the canonical memory declaration layer. `shared_write_policy` must never widen access beyond `writer_refs[]`.
- `C:\Users\huibozi\.openclaw\memory\main.sqlite` and `memory\research.sqlite` remain read-only index stores for this phase.
- Handoff execution continues to mean "target run launched," not "business task completed."
- Session boundaries remain separate: source and target agents do not share one live session transcript.
- Validation order remains `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`.
- Exit codes remain `0 = pass`, `1 = error`, `2 = warn`.

## Phase 6 Boundaries

- Declarative `context_transfer` holds only template intent:
  - `memory_refs[]`
  - `include_session_ref`
  - `include_snapshot_ref`
  - `prompt_prefix`
  - `include_source_session_summary`
  - optional `tool_state_ref`
- Runtime event/context payload holds realized values:
  - `session_ref`
  - `snapshot_ref`
  - `source_session_summary_ref`
  - `context_hash`
- `source_session_summary_ref` is generated only when the bridge can identify a source session in this order:
  1. explicit `source_session_ref`
  2. hook context session
  3. otherwise leave null
- `shared_write_policy` is a secondary coordination hint bounded by `writer_refs[]`; it never overrides writer access.
- Phase 6 summary generation is deterministic and extractive, not LLM-authored.

## Deliverables

- Updated handoff declaration schema with template-only `context_transfer`
- Updated memory declaration schema with `shared_write_policy`
- Updated canonical handoff declarations under `C:\Users\huibozi\.openclaw\decl\handoffs\`
- Updated canonical memory declarations under `C:\Users\huibozi\.openclaw\decl\memory\`
- New plugin module `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\summarizer.js`
- Runtime summary directory `C:\Users\huibozi\.openclaw\state\sessions\summaries\`
- Handoff events enriched with runtime `source_session_summary_ref` and `context_hash`
- Updated state rebuild/validation coverage for summaries
- End-to-end proof that a target handoff session transcript contains the declared `prompt_prefix`

## File Map

**Canonical declarations and importers**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\handoff.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\memory.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_handoffs_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_memory_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\handoffs\daily-to-research\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\handoffs\research-to-profit\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\handoffs\scheduled-daily-to-research\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\memory\research-learnings\memory.json`
- Modify `C:\Users\huibozi\.openclaw\decl\memory\shared-learnings\memory.json`
- Modify the remaining `C:\Users\huibozi\.openclaw\decl\memory\*\memory.json` files so every surface has an explicit `shared_write_policy`

**Plugin runtime**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\summarizer.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\executor.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\policy.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\recorder.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\index.js`

**Plugin tests**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\summarizer.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\index.test.js`

**State rebuild and validation**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py`

**Docs**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md`

## Runtime Data Shapes To Land

**Declarative `context_transfer` template**

```json
{
  "memory_refs": ["research-store", "research-learnings"],
  "include_session_ref": true,
  "include_snapshot_ref": true,
  "prompt_prefix": "You are continuing a research task initiated by the daily agent.",
  "include_source_session_summary": true,
  "tool_state_ref": null
}
```

**Runtime event payload fragment**

```json
{
  "context_refs": {
    "memory_refs": ["research-store", "research-learnings"],
    "session_ref": "handoff:daily-to-research:2026-04-02T20-10-00Z",
    "snapshot_ref": "C:\\Users\\huibozi\\.openclaw\\generated\\snapshots\\decl-20260402T195500Z.json",
    "source_session_summary_ref": "C:\\Users\\huibozi\\.openclaw\\state\\sessions\\summaries\\sess-daily-001.json",
    "tool_state_ref": null
  },
  "context_hash": "2bf820e3c8d7f4c8b49f2c80e3ffef2e0686a89916f4a7ea2b4f4ef466bde2e0"
}
```

**Deterministic session summary**

```json
{
  "session_id": "sess-daily-001",
  "agent_id": "daily",
  "summary_type": "handoff_context",
  "generated_at": "2026-04-02T20:10:00Z",
  "decl_generation": "286393de3b8fa840",
  "source_session_ref": "sess-daily-001",
  "last_user_text_excerpt": "Please hand off the pricing research task.",
  "last_assistant_text_excerpt": "I will route this research task to the research agent.",
  "recent_tool_names": ["web.search", "shell_command"],
  "memory_refs": ["research-store", "research-learnings"]
}
```
## Task 1: Land Template-Only Handoff Context And Explicit Shared-Write Policies

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\handoff.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\schemas\memory.schema.json`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_handoffs_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\import_memory_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\decl\handoffs\daily-to-research\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\handoffs\research-to-profit\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\handoffs\scheduled-daily-to-research\handoff.json`
- Modify `C:\Users\huibozi\.openclaw\decl\memory\*\memory.json`
- Test: `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py`

- [ ] **Step 1: Write the failing declaration test for template-only handoff context and shared-write policies**

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(r"C:\Users\huibozi\.openclaw")
sys.path.insert(0, str(ROOT / "scripts" / "decl_state"))

from common import read_json


class Phase6SharedContextDeclTests(unittest.TestCase):
    def test_handoff_context_transfer_uses_template_fields_only(self) -> None:
        payload = read_json(ROOT / "decl" / "handoffs" / "daily-to-research" / "handoff.json")
        ctx = payload["context_transfer"]
        self.assertIn("include_session_ref", ctx)
        self.assertIn("include_snapshot_ref", ctx)
        self.assertIn("include_source_session_summary", ctx)
        self.assertIn("prompt_prefix", ctx)
        self.assertNotIn("context_hash", ctx)
        self.assertNotIn("source_session_summary_ref", ctx)

    def test_memory_surfaces_have_explicit_shared_write_policy(self) -> None:
        roots = sorted((ROOT / "decl" / "memory").glob("*/memory.json"))
        self.assertEqual(len(roots), 9)
        for path in roots:
            payload = read_json(path)
            self.assertIn("shared_write_policy", payload)
        research = read_json(ROOT / "decl" / "memory" / "research-learnings" / "memory.json")
        shared = read_json(ROOT / "decl" / "memory" / "shared-learnings" / "memory.json")
        self.assertEqual(research["shared_write_policy"], "both")
        self.assertEqual(shared["shared_write_policy"], "read_only")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the declaration test and schema validation to see it fail first**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
```

Expected: FAIL because `handoff.schema.json`, handoff declarations, and memory declarations do not yet contain the Phase 6 fields.

- [ ] **Step 3: Update the handoff and memory schemas plus importers**

```json
{
  "context_transfer": {
    "type": "object",
    "additionalProperties": false,
    "required": [
      "memory_refs",
      "include_session_ref",
      "include_snapshot_ref",
      "prompt_prefix",
      "include_source_session_summary"
    ],
    "properties": {
      "memory_refs": { "type": "array", "items": { "type": "string" } },
      "include_session_ref": { "type": "boolean" },
      "include_snapshot_ref": { "type": "boolean" },
      "prompt_prefix": { "type": "string" },
      "include_source_session_summary": { "type": "boolean" },
      "tool_state_ref": { "type": ["string", "null"] }
    }
  }
}
```

```json
{
  "shared_write_policy": {
    "type": "string",
    "enum": ["source_only", "target_only", "both", "read_only"]
  }
}
```

```python
CONTEXT_TEMPLATES = {
    "daily-to-research": {
        "memory_refs": ["research-store", "research-learnings"],
        "include_session_ref": True,
        "include_snapshot_ref": True,
        "prompt_prefix": "You are continuing a research task initiated by the daily agent.",
        "include_source_session_summary": True,
        "tool_state_ref": None,
    },
    "research-to-profit": {
        "memory_refs": ["research-store", "research-learnings", "shared-learnings"],
        "include_session_ref": True,
        "include_snapshot_ref": True,
        "prompt_prefix": "Continue the active research thread and produce the profit-oriented follow-up.",
        "include_source_session_summary": True,
        "tool_state_ref": None,
    },
    "scheduled-daily-to-research": {
        "memory_refs": ["research-store"],
        "include_session_ref": False,
        "include_snapshot_ref": True,
        "prompt_prefix": "Continue the scheduled daily research sweep.",
        "include_source_session_summary": False,
        "tool_state_ref": None,
    },
}
```

```python
SHARED_WRITE_POLICIES = {
    "research-learnings": "both",
    "shared-learnings": "read_only",
}
DEFAULT_SHARED_WRITE_POLICY = "read_only"
```

- [ ] **Step 4: Re-run declaration validation until it passes**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py
```

Expected: PASS, with `research-learnings = both`, `shared-learnings = read_only`, and no declaration file containing runtime `context_hash` or `source_session_summary_ref`.

- [ ] **Step 5: Commit the declaration-layer changes**

```bash
git -C C:\Users\huibozi\claude-code-unified-research add docs/superpowers/plans/2026-04-02-openclaw-phase6-shared-context-joint-session-lite-implementation.md
# Runtime files live under C:\Users\huibozi\.openclaw; create a backup checkpoint before editing additional tasks.
```

## Task 2: Add Deterministic Session Summaries

**Files:**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\summarizer.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\summarizer.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\index.test.js`

- [ ] **Step 1: Write the failing Node test for deterministic summary generation**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { createSummarizer } from "../lib/summarizer.js";

test("summarizer emits deterministic excerpts and tool names", async () => {
  const root = "C:/Users/huibozi/.openclaw";
  const summarizer = createSummarizer({ api: { logger: console }, runtimeRoot: root });
  const summary = await summarizer.buildSummary({
    sourceSessionRef: "1e49a56c-f079-4027-a41a-44596df2126a",
    agentId: "research",
    memoryRefs: ["research-store", "research-learnings"],
    declGeneration: "286393de3b8fa840"
  });
  assert.equal(summary.summary.summary_type, "handoff_context");
  assert.equal(summary.summary.agent_id, "research");
  assert.ok(Array.isArray(summary.summary.recent_tool_names));
  assert.ok(summary.summary.last_user_text_excerpt !== undefined);
});
```

- [ ] **Step 2: Run the summarizer test to verify it fails before the module exists**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\summarizer.test.js
```

Expected: FAIL because `lib\summarizer.js` does not exist yet.

- [ ] **Step 3: Implement a deterministic summarizer that never guesses the source session**

```js
import fs from "node:fs/promises";
import path from "node:path";

function extractText(message) {
  if (!message) return null;
  const blocks = Array.isArray(message.content) ? message.content : [];
  const textBlock = blocks.find((block) => block?.type === "text" && typeof block.text === "string");
  return textBlock?.text ?? null;
}

export function createSummarizer({ api, runtimeRoot }) {
  const root = runtimeRoot ?? "C:/Users/huibozi/.openclaw";
  const summariesRoot = path.join(root, "state", "sessions", "summaries");

  return {
    async buildSummary({ sourceSessionRef, agentId, memoryRefs, declGeneration }) {
      if (!sourceSessionRef) return null;
      const sessionPath = path.join(root, "state", "sessions", "index.json");
      const sessionIndex = JSON.parse(await fs.readFile(sessionPath, "utf8"));
      const match = (sessionIndex.entries ?? []).find((entry) => entry.session_id === sourceSessionRef);
      if (!match?.source_path) return null;
      const lines = (await fs.readFile(match.source_path, "utf8"))
        .split(/\r?\n/)
        .filter(Boolean)
        .map((line) => JSON.parse(line));
      const userMessage = [...lines].reverse().find((line) => line?.message?.role === "user");
      const assistantMessage = [...lines].reverse().find((line) => line?.message?.role === "assistant");
      const recentToolNames = [...new Set(lines.filter((line) => line?.toolCall?.name).slice(-5).map((line) => line.toolCall.name))];
      const summary = {
        session_id: sourceSessionRef,
        agent_id: agentId,
        summary_type: "handoff_context",
        generated_at: new Date().toISOString(),
        decl_generation: declGeneration,
        source_session_ref: sourceSessionRef,
        last_user_text_excerpt: extractText(userMessage?.message)?.slice(0, 400) ?? null,
        last_assistant_text_excerpt: extractText(assistantMessage?.message)?.slice(0, 400) ?? null,
        recent_tool_names: recentToolNames,
        memory_refs: memoryRefs,
      };
      await fs.mkdir(summariesRoot, { recursive: true });
      const outPath = path.join(summariesRoot, `sess-${sourceSessionRef}.json`);
      await fs.writeFile(outPath, JSON.stringify(summary, null, 2) + "\n");
      return { summary, path: outPath };
    }
  };
}
```

- [ ] **Step 4: Re-run the summarizer test and verify the summary file is created**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\summarizer.test.js
Get-ChildItem C:\Users\huibozi\.openclaw\state\sessions\summaries
```

Expected: PASS, and at least one `sess-*.json` file exists under `state\sessions\summaries\`.

- [ ] **Step 5: Commit the summarizer module**

```bash
git -C C:\Users\huibozi\claude-code-unified-research add docs/superpowers/plans/2026-04-02-openclaw-phase6-shared-context-joint-session-lite-implementation.md
# Runtime checkpoint: back up C:\Users\huibozi\.openclaw\state\sessions\summaries after creation.
```
## Task 3: Upgrade Executor To Build Runtime Context Payloads And Prompt Prefixes

**Files:**
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\executor.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\policy.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js`

- [ ] **Step 1: Write failing tests for runtime context realization and no-guess summary behavior**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { createExecutor } from "../lib/executor.js";

test("executor realizes session_ref, snapshot_ref, summary_ref, and context_hash at runtime", async () => {
  let seenPrompt = null;
  const executor = createExecutor({
    api: {
      logger: console,
      runtime: {
        agent: {
          resolveAgentDir: () => "C:/Users/huibozi/.openclaw/agents/research/agent",
          resolveAgentWorkspaceDir: () => "C:/Users/huibozi/.openclaw/workspace-research",
          runEmbeddedPiAgent: async (params) => {
            seenPrompt = params.prompt;
            return { status: "ok" };
          }
        },
        state: { resolveStateDir: () => "C:/Users/huibozi/.openclaw/state" }
      }
    },
    loader: { getAgent: () => ({ id: "research", model: "minimax-portal/abab6.5" }) },
    summarizer: {
      buildSummary: async () => ({
        summary: { session_id: "sess-1" },
        path: "C:/Users/huibozi/.openclaw/state/sessions/summaries/sess-sess-1.json"
      })
    }
  });
  const result = await executor.runTarget({
    handoffPolicyId: "daily-to-research",
    triggerRef: "binding-daily-001",
    initiatorAgent: "daily",
    targetAgent: "research",
    contextTemplate: {
      memory_refs: ["research-store"],
      include_session_ref: true,
      include_snapshot_ref: true,
      prompt_prefix: "Continue the active research thread.",
      include_source_session_summary: true,
      tool_state_ref: null
    },
    sourceSessionRef: "sess-1",
    snapshotRef: "decl-test"
  });
  assert.ok(result.context_hash);
  assert.equal(result.context_refs.source_session_summary_ref.includes("sess-sess-1.json"), true);
  assert.match(seenPrompt, /Continue the active research thread\./);
});
```

- [ ] **Step 2: Implement runtime context realization in `executor.js`**

```js
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

function hashContextPayload(payload) {
  return crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
}

export function createExecutor({ api, loader, summarizer }) {
  return {
    async runTarget({ handoffPolicyId, triggerRef, initiatorAgent, targetAgent, contextTemplate, sourceSessionRef, snapshotRef, timeoutSeconds }) {
      const runId = crypto.randomUUID();
      const sessionRef = `handoff:${handoffPolicyId}:${new Date().toISOString().replace(/[:.]/g, "-")}`;
      const agentDecl = loader?.getAgent?.(targetAgent) ?? { id: targetAgent, _adapter_notes: {} };
      const agentDir = agentDecl?._adapter_notes?.physical_agent_dir ?? api.runtime.agent.resolveAgentDir(agentDecl);
      const workspaceDir = agentDecl?._adapter_notes?.workspace ?? api.runtime.agent.resolveAgentWorkspaceDir(agentDecl);
      const sessionsDir = path.join(agentDir, "sessions");
      const sessionFile = path.join(sessionsDir, `${sessionRef.replace(/[:]/g, "-")}.jsonl`);
      const summaryResult = contextTemplate.include_source_session_summary && sourceSessionRef
        ? await summarizer.buildSummary({
            sourceSessionRef,
            agentId: initiatorAgent,
            memoryRefs: contextTemplate.memory_refs,
            declGeneration: snapshotRef ?? null
          })
        : null;
      const contextRefs = {
        memory_refs: contextTemplate.memory_refs,
        session_ref: contextTemplate.include_session_ref ? sourceSessionRef ?? null : null,
        snapshot_ref: contextTemplate.include_snapshot_ref ? snapshotRef ?? null : null,
        source_session_summary_ref: summaryResult?.path ?? null,
        tool_state_ref: contextTemplate.tool_state_ref ?? null
      };
      const contextHash = hashContextPayload(contextRefs);
      const prompt = [
        contextTemplate.prompt_prefix,
        `Handoff from ${initiatorAgent} to ${targetAgent}.`,
        `Trigger: ${triggerRef}.`,
        `Memory refs: ${contextRefs.memory_refs.join(", ") || "none"}.`,
        `Source session ref: ${contextRefs.session_ref ?? "none"}.`,
        `Snapshot ref: ${contextRefs.snapshot_ref ?? "none"}.`,
        `Source session summary ref: ${contextRefs.source_session_summary_ref ?? "none"}.`,
        `Context hash: ${contextHash}.`
      ].join("\n");

      await fs.mkdir(sessionsDir, { recursive: true });
      await api.runtime.agent.runEmbeddedPiAgent({
        sessionId: sessionRef,
        agentId: targetAgent,
        agentDir,
        runId,
        sessionFile,
        workspaceDir,
        prompt,
        timeoutMs: Math.max(1000, Math.trunc((timeoutSeconds ?? 300) * 1000)),
        provider: agentDecl.model?.split("/")[0],
        model: agentDecl.model?.split("/").slice(1).join("/") || agentDecl.model
      });

      return {
        status: "accepted",
        run_id: runId,
        session_ref: sessionRef,
        prompt,
        context_refs: contextRefs,
        context_hash: contextHash
      };
    }
  };
}
```

- [ ] **Step 3: Re-run the executor and policy tests**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js
```

Expected: PASS, and the executor test proves `context_hash` plus `prompt_prefix` are realized at runtime without guessing a source session.

- [ ] **Step 4: Commit the runtime context builder changes**

```bash
git -C C:\Users\huibozi\claude-code-unified-research add docs/superpowers/plans/2026-04-02-openclaw-phase6-shared-context-joint-session-lite-implementation.md
# Runtime checkpoint: back up C:\Users\huibozi\.openclaw\extensions\handoff-bridge after executor/policy updates.
```

## Task 4: Persist Context Hashes And Summary Refs In Handoff Events

**Files:**
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\recorder.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js`
- Modify `C:\Users\huibozi\.openclaw\state\handoff-events\index.json` through runtime rebuild only

- [ ] **Step 1: Write the failing recorder test for Phase 6 event enrichment**

```js
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { createRecorder } from "../lib/recorder.js";

test("recorder stores context_hash and summary ref in both events and index", async () => {
  const recorder = createRecorder({ api: { logger: console }, stateDir: "C:/Users/huibozi/.openclaw/state" });
  await recorder.ensureStateFiles();
  await recorder.appendEvent({
    event_id: "hev-phase6-001",
    handoff_policy_id: "daily-to-research",
    trigger_ref: "binding-daily-001",
    decl_generation: "decl-test",
    initiator_agent: "daily",
    target_agent: "research",
    attempt: 1,
    status: "accepted",
    run_id: "run-phase6-001",
    session_ref: "handoff:phase6:test",
    context_refs: {
      memory_refs: ["research-store"],
      session_ref: "sess-source-001",
      snapshot_ref: "decl-test",
      source_session_summary_ref: "C:/Users/huibozi/.openclaw/state/sessions/summaries/sess-source-001.json",
      tool_state_ref: null
    },
    context_hash: "hash-phase6-001",
    started_at: "2026-04-02T12:00:00Z",
    resolved_at: "2026-04-02T12:00:05Z",
    outcome_notes: "ok"
  });
  const index = JSON.parse(await fs.readFile("C:/Users/huibozi/.openclaw/state/handoff-events/index.json", "utf8"));
  const latest = index.entries.at(-1);
  assert.equal(latest.context_hash, "hash-phase6-001");
  assert.equal(latest.context_refs.source_session_summary_ref.includes("sess-source-001.json"), true);
});
```

- [ ] **Step 2: Extend the recorder payload and index summary shape**

```js
index.entries.push({
  event_id: entry.event_id,
  handoff_policy_id: entry.handoff_policy_id,
  trigger_ref: entry.trigger_ref,
  decl_generation: entry.decl_generation,
  initiator_agent: entry.initiator_agent,
  target_agent: entry.target_agent,
  attempt: entry.attempt,
  status: entry.status,
  run_id: entry.run_id,
  session_ref: entry.session_ref,
  context_refs: entry.context_refs ?? {},
  context_hash: entry.context_hash ?? null,
  started_at: entry.started_at,
  resolved_at: entry.resolved_at,
  outcome_notes: entry.outcome_notes ?? ""
});
```

- [ ] **Step 3: Re-run the recorder test and inspect the latest event output**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js
Get-Content C:\Users\huibozi\.openclaw\state\handoff-events\events.jsonl -Tail 3
Get-Content C:\Users\huibozi\.openclaw\state\handoff-events\index.json -TotalCount 200
```

Expected: PASS, and the latest event/index entries contain non-empty `context_hash` plus `source_session_summary_ref` when a source session was available.

- [ ] **Step 4: Commit the recorder updates**

```bash
git -C C:\Users\huibozi\claude-code-unified-research add docs/superpowers/plans/2026-04-02-openclaw-phase6-shared-context-joint-session-lite-implementation.md
# Runtime checkpoint: back up C:\Users\huibozi\.openclaw\state\handoff-events after recorder changes.
```
## Task 5: Rebuild And Validate The New Summary State Surface

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\rebuild_state_indexes_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_decl_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py`

- [ ] **Step 1: Add failing state-validation tests for summaries and context hashes**

```python
import json

class Phase6SharedContextStateTests(unittest.TestCase):
    def test_summary_directory_exists_when_context_summary_is_emitted(self) -> None:
        summaries_root = ROOT / "state" / "sessions" / "summaries"
        self.assertTrue(summaries_root.exists())
        summary_files = list(summaries_root.glob("sess-*.json"))
        self.assertGreaterEqual(len(summary_files), 1)

    def test_latest_handoff_event_has_context_hash(self) -> None:
        events_path = ROOT / "state" / "handoff-events" / "events.jsonl"
        lines = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        latest = lines[-1]
        self.assertIn("context_hash", latest)
        self.assertTrue(latest["context_hash"])
```

- [ ] **Step 2: Extend state rebuild and validators to scan summaries**

```python
summaries_root = STATE_ROOT / "sessions" / "summaries"
summary_entries = []
if summaries_root.exists():
    for path in sorted(summaries_root.glob("sess-*.json")):
        payload = read_json(path)
        summary_entries.append({
            "session_id": payload.get("session_id"),
            "agent_id": payload.get("agent_id"),
            "summary_type": payload.get("summary_type"),
            "generated_at": payload.get("generated_at"),
            "source_path": str(path),
        })
```

```python
if summaries_root.exists():
    for path in sorted(summaries_root.glob("sess-*.json")):
        payload = read_json(path)
        for field in (
            "session_id",
            "agent_id",
            "summary_type",
            "generated_at",
            "decl_generation",
            "source_session_ref",
            "recent_tool_names",
            "memory_refs",
        ):
            if field not in payload:
                errors.append(f"summary {path} missing {field}")
```

- [ ] **Step 3: Re-run Python tests and full validation**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Expected: PASS, with `validate_full_openclaw.py` returning `0` or `2`, and the state health report counting summary files under `state\sessions\summaries\`.

- [ ] **Step 4: Commit the validation chain changes**

```bash
git -C C:\Users\huibozi\claude-code-unified-research add docs/superpowers/plans/2026-04-02-openclaw-phase6-shared-context-joint-session-lite-implementation.md
# Runtime checkpoint: back up C:\Users\huibozi\.openclaw\scripts\decl_state after validation updates.
```

## Task 6: Prove End-To-End Context Relay And Update Operator Docs

**Files:**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md`
- Test: `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\index.test.js`

- [ ] **Step 1: Document the Phase 6 maintenance chain and summary rules**

```markdown
## Phase 6 shared context rules
- `decl/handoffs/*/handoff.json` stores template intent only; runtime values stay in `state/handoff-events/`.
- `state/sessions/summaries/` is deterministic extractive state, not an LLM-authored summary store.
- `source_session_summary_ref` is generated only when the bridge can identify a source session explicitly or from hook context.
- `shared_write_policy` is enforced inside `writer_refs[]` boundaries and does not widen write access.
- Verification for `prompt_prefix` must read the target handoff session transcript, not infer from logs.
```

- [ ] **Step 2: Trigger a live handoff and capture the target transcript proof**

Run:

```powershell
$script = @"
const { spawnSync } = require('node:child_process');
const exe = 'C:/Users/huibozi/AppData/Roaming/npm/node_modules/openclaw/openclaw.mjs';
const args = [exe, 'gateway','call','handoff.trigger','--json','--timeout','180000','--params', JSON.stringify({ handoff_policy_id: 'daily-to-research', source_session_ref: '3161ce96-ba3a-4ce1-932a-5602fe441295' })];
const result = spawnSync('node', args, { stdio: 'pipe', shell: false, encoding: 'utf8' });
process.stdout.write(result.stdout || '');
process.stderr.write(result.stderr || '');
process.exit(result.status ?? 1);
"@
$script | node -
```

Expected: gateway call succeeds and yields a non-empty `run_id` plus `session_ref`.

- [ ] **Step 3: Verify summary generation, event enrichment, and prompt prefix in the target transcript**

Run:

```powershell
Get-ChildItem C:\Users\huibozi\.openclaw\state\sessions\summaries
Get-Content C:\Users\huibozi\.openclaw\state\handoff-events\events.jsonl -Tail 3
$latest = Get-Content C:\Users\huibozi\.openclaw\state\handoff-events\events.jsonl -Tail 1 | ConvertFrom-Json
Get-Content (Join-Path 'C:\Users\huibozi\.openclaw\agents\research\sessions' (($latest.session_ref -replace ':','-') + '.jsonl')) -TotalCount 20
```

Expected: there is at least one summary file, the latest event contains non-empty `context_hash`, and the first user prompt in the target handoff session includes the declared `prompt_prefix`.

- [ ] **Step 4: Run the final verification bundle**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase6_shared_context.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
openclaw plugins inspect handoff-bridge --json
```

Expected: all Node tests pass, the Phase 6 Python test passes, full validation returns `0` or `2`, and plugin inspect still shows a healthy handoff-bridge extension.

- [ ] **Step 5: Commit the docs and final verification notes**

```bash
git -C C:\Users\huibozi\claude-code-unified-research add docs/superpowers/plans/2026-04-02-openclaw-phase6-shared-context-joint-session-lite-implementation.md
# Runtime checkpoint: archive C:\Users\huibozi\.openclaw\backups\decl-state\phase6-<timestamp> after end-to-end verification.
```

## Spec Coverage Check

- Template-only handoff context vs runtime-realized context: covered in Task 1 and Task 4.
- Optional `source_session_summary_ref` with explicit provenance and no recent-session guessing: covered in Tasks 2-3.
- Runtime-only `context_hash`: covered in Tasks 3-4.
- `shared_write_policy` bounded by `writer_refs[]`: covered in Task 1.
- Deterministic summary generation and summary directory validation: covered in Tasks 2 and 5.
- Prompt-prefix transcript verification through the target handoff session: covered in Task 6.

## Self-Review Notes

- No placeholder text remains; each task names concrete runtime files, code snippets, and commands.
- The plan preserves the declaration/runtime split and never stores `context_hash` or realized summary refs in `decl\handoffs\`.
- The plan keeps source and target sessions separate while allowing richer context relay.
- The plan keeps `shared_write_policy` subordinate to `writer_refs[]` so policy hints do not widen write access.
- The plan uses deterministic summary extraction instead of an LLM summarization pass.
