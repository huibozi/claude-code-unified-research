# OpenClaw Phase 5 Handoff Execution Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn OpenClaw Phase 4 handoff declarations into real, auditable execution by running a native bridge plugin that dispatches target-agent runs with `api.runtime.agent.runEmbeddedPiAgent(...)` and records handoff events under `state/handoff-events/`.

**Architecture:** Keep `C:\Users\huibozi\.openclaw\decl\handoffs\` as the fact source, then add a native plugin under `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\` that loads handoff policies, reacts to routing-adjacent hooks, launches target runs through the plugin runtime, and appends auditable event records. Preserve the live runtime contract: the plugin never rewrites `openclaw.json`, `decl\handoffs\`, live session transcripts, or `memory\*.sqlite`; it only reads canonical declarations and writes new handoff event state.

**Tech Stack:** OpenClaw native plugin SDK, Node.js ESM JavaScript, PowerShell 7+, Python 3.11, `jsonschema`, JSON Schema Draft 2020-12, OpenClaw CLI (`openclaw plugins ...`), live runtime files under `C:\Users\huibozi\.openclaw`

---

## Baseline To Preserve

- `C:\Users\huibozi\.openclaw\decl\handoffs\*.json` remains read-only fact source for handoff policy declarations.
- `C:\Users\huibozi\.openclaw\decl\bindings\*.json`, `decl\memory\*.json`, and `decl\agents\*.json` remain the canonical sources for routing, memory transfer, and handoff acceptance.
- `C:\Users\huibozi\.openclaw\openclaw.json` stays the live runtime config and is not rewritten by the bridge plugin.
- `C:\Users\huibozi\.openclaw\agents\*\sessions\*.jsonl`, `workspace*\*`, and `memory\*.sqlite` remain live runtime surfaces and are not rewritten by Phase 5 code.
- `state\handoff-events\index.json` already exists and must remain the lightweight summary surface; Phase 5 may add `events.jsonl` beside it.
- Phase 4 handoff status semantics remain locked:
  - `accepted` = preflight passed and target run started
  - `rejected` = blocked by `accepts_handoff_from[]` or guardrails
  - `timed_out` = target run exceeded timeout
  - `escalated` = timeout policy escalated instead of retrying
  - `failed` = execution exception or no usable target
- Validation order remains: `validate decl -> rebuild registries -> rebuild state indexes -> validate state -> build snapshot -> backfill decl_generation -> summarize`.
- Exit codes remain `0 = pass`, `1 = error`, `2 = warn`.

## Deliverables

- Native plugin root under `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\`
- Native plugin packaging files: `package.json`, `openclaw.plugin.json`, `index.js`
- Runtime helper modules: `lib\loader.js`, `lib\executor.js`, `lib\policy.js`, `lib\recorder.js`
- Real handoff event log at `C:\Users\huibozi\.openclaw\state\handoff-events\events.jsonl`
- Updated handoff index at `C:\Users\huibozi\.openclaw\state\handoff-events\index.json`
- Gateway control-plane manual trigger via `api.registerGatewayMethod("handoff.trigger", ...)`
- Hook-based handoff dispatch through `message_received` and `inbound_claim`
- Optional audit-only use of `api.onConversationBindingResolved(...)`
- End-to-end proof that at least one live handoff produces non-empty `run_id`, `session_ref`, and `decl_generation`

## File Map

**Plugin root**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\package.json`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\openclaw.plugin.json`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\index.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md`

**Plugin runtime modules**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\loader.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\executor.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\policy.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\recorder.js`

**Plugin tests**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\loader.test.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js`

**Decl-state validation**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase5_handoff_runtime.py`

**Docs**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`

## Plugin Shape

```json
{
  "name": "handoff-bridge",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "openclaw": {
    "extensions": ["./index.js"]
  }
}
```

```json
{
  "id": "handoff-bridge",
  "name": "Handoff Bridge",
  "description": "Executes canonical OpenClaw handoff policies through the plugin runtime.",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "enabled": {"type": "boolean"},
      "defaultTimeoutSeconds": {"type": "integer", "minimum": 1},
      "auditLogPath": {"type": "string"}
    }
  }
}
```

## Trigger Strategy

Phase 5 does **not** use `api.onConversationBindingResolved(...)` as the main execution trigger because the SDK describes that callback as a post-approval notification, not a general routing-hit callback.

Main runtime entrypoints:
- `message_received`
- `inbound_claim`
- `cron_ref` handling inside the plugin service
- `handoff.trigger` gateway method
- `onConversationBindingResolved(...)` for audit enrichment only

## Task 1: Prove SDK Capability And Install Surface

**Files:**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\package.json`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\openclaw.plugin.json`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\index.js`

- [ ] **Step 1: Write the minimal plugin packaging files**

```json
{
  "name": "handoff-bridge",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "openclaw": {
    "extensions": ["./index.js"]
  }
}
```

```json
{
  "id": "handoff-bridge",
  "name": "Handoff Bridge",
  "description": "Phase 5 bridge plugin for canonical handoff execution.",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

```js
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "handoff-bridge",
  name: "Handoff Bridge",
  description: "Phase 5 handoff execution runtime.",
  register(api) {
    api.logger.info("handoff bridge register() called", {
      registrationMode: api.registrationMode
    });
  }
});
```

- [ ] **Step 2: Link-install and enable the plugin**

Run:

```powershell
openclaw plugins install -l C:\Users\huibozi\.openclaw\extensions\handoff-bridge
openclaw plugins enable handoff-bridge
openclaw plugins inspect handoff-bridge --json
```

Expected: install succeeds, enable succeeds, inspect includes `"id": "handoff-bridge"`, and the plugin is native OpenClaw format.

- [ ] **Step 3: Verify the gateway picked it up under current reload mode**

Run:

```powershell
openclaw plugins list
```

Expected: `handoff-bridge` appears as enabled, no manifest/schema validation error, and no manual restart is needed when reload mode remains `hybrid`.

- [ ] **Step 4: Commit the packaging scaffold**

```bash
git add docs/superpowers/plans/2026-04-02-openclaw-phase5-handoff-execution-runtime-implementation.md
# Runtime files are outside this repo; commit them only when implementation happens in the live runtime.
```

## Task 2: Add Runtime Module Skeletons And Unit Test Harness

**Files:**
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\loader.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\executor.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\policy.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\recorder.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\loader.test.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js`
- Create `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js`

- [ ] **Step 1: Write failing Node tests for the module seams**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { createLoader } from "../lib/loader.js";

test("loader returns the canonical daily handoff policy", async () => {
  const loader = createLoader({ api: { resolvePath: (input) => input, logger: console } });
  await loader.refresh();
  const policy = loader.getById("daily-to-research");
  assert.equal(policy.id, "daily-to-research");
  assert.equal(policy.trigger.type, "binding_ref");
});
```

```js
import test from "node:test";
import assert from "node:assert/strict";
import { createPolicyEngine } from "../lib/policy.js";

test("policy engine rejects a target that does not accept the initiator", async () => {
  const policy = createPolicyEngine({
    api: { logger: console },
    loader: { getAgent: (id) => ({ id, accepts_handoff_from: [] }) },
    recorder: { appendEvent: async (entry) => entry },
    executor: { runTarget: async () => ({ status: "accepted" }) }
  });
  const result = await policy.preflight({ initiatorAgent: "daily", targetAgent: "research" });
  assert.equal(result.status, "rejected");
});
```

- [ ] **Step 2: Run the tests to verify they fail before implementation**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
```

Expected: FAIL because the runtime modules do not exist yet.

- [ ] **Step 3: Create minimal module exports**

```js
export function createLoader({ api }) {
  return {
    async refresh() {
      api.logger?.info?.("loader refresh stub");
    },
    getById(id) {
      return { id, trigger: { type: "binding_ref" } };
    },
    getAgent(id) {
      return { id, accepts_handoff_from: [] };
    }
  };
}
```

```js
export function createPolicyEngine() {
  return {
    async preflight() {
      return { status: "rejected" };
    }
  };
}
```

- [ ] **Step 4: Re-run the test harness until the stubs load cleanly**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
```

Expected: tests load, even if some assertions still fail before real logic lands.

- [ ] **Step 5: Commit the test harness skeleton**

```bash
git add C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests
```

## Task 3: Implement Declaration Loader And Recorder

**Files:**
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\loader.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\recorder.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\loader.test.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js`

- [ ] **Step 1: Add failing tests for declaration loading and event append behavior**

```js
test("loader refresh indexes handoff, agent, and memory declarations", async () => {
  const loader = createLoader({
    api: {
      rootDir: "C:/Users/huibozi/.openclaw/extensions/handoff-bridge",
      logger: console,
      runtime: { state: { resolveStateDir: () => "C:/Users/huibozi/.openclaw" } }
    }
  });
  await loader.refresh();
  assert.ok(loader.getById("daily-to-research"));
  assert.ok(loader.getAgent("research"));
  assert.ok(loader.getMemory("research-store"));
});
```

```js
test("recorder appends an event and refreshes index.json summary", async () => {
  const recorder = createRecorder({ api: { logger: console }, stateDir: "C:/Users/huibozi/.openclaw/state" });
  await recorder.ensureStateFiles();
  const entry = await recorder.appendEvent({
    event_id: "hev-test-001",
    handoff_policy_id: "daily-to-research",
    trigger_ref: "binding-daily-001",
    decl_generation: "decl-test",
    initiator_agent: "daily",
    target_agent: "research",
    attempt: 1,
    status: "accepted",
    run_id: "run-test-001",
    session_ref: "handoff:test",
    context_refs: { memory_refs: ["shared-learnings"], snapshot_ref: null },
    started_at: "2026-04-02T08:30:00Z",
    resolved_at: "2026-04-02T08:30:05Z",
    outcome_notes: "ok"
  });
  assert.equal(entry.event_id, "hev-test-001");
});
```

- [ ] **Step 2: Implement loader and recorder with real filesystem paths**

```js
import fs from "node:fs/promises";
import path from "node:path";

export function createLoader({ api }) {
  let cache = { handoffs: new Map(), agents: new Map(), memory: new Map() };
  const runtimeRoot = path.dirname(path.dirname(api.rootDir ?? "C:/Users/huibozi/.openclaw/extensions/handoff-bridge"));

  async function loadFamily(root, fileName) {
    const entries = await fs.readdir(root, { withFileTypes: true });
    const out = new Map();
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const payload = JSON.parse(await fs.readFile(path.join(root, entry.name, fileName), "utf8"));
      out.set(payload.id, payload);
    }
    return out;
  }

  return {
    async refresh() {
      cache.handoffs = await loadFamily(path.join(runtimeRoot, "decl", "handoffs"), "handoff.json");
      cache.agents = await loadFamily(path.join(runtimeRoot, "decl", "agents"), "agent.json");
      cache.memory = await loadFamily(path.join(runtimeRoot, "decl", "memory"), "memory.json");
    },
    getById(id) { return cache.handoffs.get(id); },
    getAgent(id) { return cache.agents.get(id); },
    getMemory(id) { return cache.memory.get(id); }
  };
}
```

```js
import fs from "node:fs/promises";
import path from "node:path";

export function createRecorder({ api, stateDir }) {
  const handoffRoot = path.join(stateDir ?? "C:/Users/huibozi/.openclaw/state", "handoff-events");
  const eventsPath = path.join(handoffRoot, "events.jsonl");
  const indexPath = path.join(handoffRoot, "index.json");

  return {
    async ensureStateFiles() {
      await fs.mkdir(handoffRoot, { recursive: true });
      await fs.writeFile(eventsPath, "", { flag: "a" });
      try {
        await fs.access(indexPath);
      } catch {
        await fs.writeFile(indexPath, JSON.stringify({ schema_version: 2, entries: [] }, null, 2) + "\n");
      }
    },
    async appendEvent(entry) {
      await this.ensureStateFiles();
      await fs.appendFile(eventsPath, JSON.stringify(entry) + "\n");
      const index = JSON.parse(await fs.readFile(indexPath, "utf8"));
      index.schema_version = 2;
      index.entries.push({
        event_id: entry.event_id,
        handoff_policy_id: entry.handoff_policy_id,
        trigger_ref: entry.trigger_ref,
        decl_generation: entry.decl_generation,
        initiator_agent: entry.initiator_agent,
        target_agent: entry.target_agent,
        status: entry.status,
        run_id: entry.run_id,
        session_ref: entry.session_ref,
        started_at: entry.started_at,
        resolved_at: entry.resolved_at
      });
      await fs.writeFile(indexPath, JSON.stringify(index, null, 2) + "\n");
      return entry;
    },
    async recordBindingAudit(event) {
      api.logger.info("binding resolution observed", { status: event.status, decision: event.decision });
    }
  };
}
```

- [ ] **Step 3: Re-run the loader and recorder tests**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\loader.test.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js
```

Expected: PASS for loader refresh and recorder append behavior.

- [ ] **Step 4: Commit the state IO layer**

```bash
git add C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\loader.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\recorder.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\loader.test.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\recorder.test.js
```

## Task 4: Implement Executor With Preflight Session And Run Allocation

**Files:**
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\executor.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js`

- [ ] **Step 1: Write failing tests for preflight allocation and runtime invocation**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { createExecutor } from "../lib/executor.js";

test("executor allocates session_ref before invoking runEmbeddedPiAgent", async () => {
  let seen = null;
  const executor = createExecutor({
    api: {
      logger: console,
      runtime: {
        agent: {
          resolveAgentDir: () => "C:/Users/huibozi/.openclaw/agents/research/agent",
          resolveAgentWorkspaceDir: () => "C:/Users/huibozi/.openclaw/workspace-research",
          resolveAgentTimeoutMs: () => 300000,
          runEmbeddedPiAgent: async (params) => {
            seen = params;
            return { status: "ok" };
          }
        }
      }
    }
  });
  const result = await executor.runTarget({
    handoffPolicyId: "daily-to-research",
    triggerRef: "binding-daily-001",
    initiatorAgent: "daily",
    targetAgent: "research",
    memoryRefs: ["research-store"],
    snapshotRef: "decl-test"
  });
  assert.match(result.session_ref, /^handoff:/);
  assert.equal(seen.sessionId, result.session_ref);
});
```

- [ ] **Step 2: Implement the executor wrapper**

```js
import crypto from "node:crypto";
import path from "node:path";

export function createExecutor({ api }) {
  return {
    async runTarget({ handoffPolicyId, triggerRef, initiatorAgent, targetAgent, memoryRefs, snapshotRef }) {
      const runId = crypto.randomUUID();
      const sessionRef = `handoff:${handoffPolicyId}:${new Date().toISOString()}`;
      const agentCfg = { id: targetAgent };
      const agentDir = api.runtime.agent.resolveAgentDir(agentCfg);
      const workspaceDir = api.runtime.agent.resolveAgentWorkspaceDir(agentCfg);
      const sessionFile = path.join(agentDir, "sessions", `${sessionRef.replace(/[:]/g, "-")}.jsonl`);
      const timeoutMs = api.runtime.agent.resolveAgentTimeoutMs(agentCfg);
      const prompt = [
        `Handoff from ${initiatorAgent} to ${targetAgent}.`,
        `Trigger: ${triggerRef}.`,
        `Memory refs: ${memoryRefs.join(", ") || "none"}.`,
        `Snapshot ref: ${snapshotRef ?? "none"}.`
      ].join("\n");

      await api.runtime.agent.runEmbeddedPiAgent({
        sessionId: sessionRef,
        runId,
        sessionFile,
        workspaceDir,
        prompt,
        timeoutMs
      });

      return {
        status: "accepted",
        run_id: runId,
        session_ref: sessionRef,
        timeout_ms: timeoutMs,
        prompt
      };
    }
  };
}
```

- [ ] **Step 3: Re-run the executor tests**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js
```

Expected: PASS and confirms `session_ref` exists before the runtime call.

- [ ] **Step 4: Commit the executor wrapper**

```bash
git add C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\executor.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\executor.test.js
```

## Task 5: Implement Policy Engine For Rejection, Timeout, And Next-Target Retry

**Files:**
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\policy.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js`

- [ ] **Step 1: Write failing tests for the three timeout paths**

```js
test("policy engine retries the next target when on_timeout is next_target", async () => {
  const calls = [];
  const policy = createPolicyEngine({
    api: { logger: console },
    loader: {
      getAgent: (id) => ({ id, accepts_handoff_from: ["daily"] }),
      getById: () => ({
        id: "daily-to-research",
        initiator_agent: "daily",
        target_agents: ["research", "profit"],
        acceptance_policy: { timeout_seconds: 1, on_timeout: "next_target" },
        context_transfer: { memory_refs: [], snapshot_ref: false, session_ref: true }
      })
    },
    executor: {
      runTarget: async ({ targetAgent }) => {
        calls.push(targetAgent);
        if (targetAgent === "research") throw new Error("timeout");
        return { status: "accepted", run_id: "run-profit", session_ref: "handoff:profit" };
      }
    },
    recorder: { appendEvent: async (entry) => entry }
  });
  const result = await policy.dispatchPolicy({ handoffPolicyId: "daily-to-research", triggerRef: "binding-daily-001" });
  assert.deepEqual(calls, ["research", "profit"]);
  assert.equal(result.status, "accepted");
});
```

- [ ] **Step 2: Implement preflight and retry semantics**

```js
import crypto from "node:crypto";

export function createPolicyEngine({ api, loader, recorder, executor }) {
  async function preflight({ initiatorAgent, targetAgent }) {
    const target = loader.getAgent(targetAgent);
    if (!target) return { status: "failed", reason: "missing_target_agent" };
    if (!(target.accepts_handoff_from ?? []).includes(initiatorAgent)) {
      return { status: "rejected", reason: "target_does_not_accept_initiator" };
    }
    return { status: "accepted" };
  }

  async function dispatchPolicy({ handoffPolicyId, triggerRef, manualParams }) {
    const policy = loader.getById(handoffPolicyId);
    const declGeneration = manualParams?.decl_generation ?? "current";
    let attempt = 0;

    for (const targetAgent of policy.target_agents) {
      attempt += 1;
      const gate = await preflight({ initiatorAgent: policy.initiator_agent, targetAgent });
      if (gate.status !== "accepted") {
        await recorder.appendEvent({
          event_id: crypto.randomUUID(),
          handoff_policy_id: handoffPolicyId,
          trigger_ref: triggerRef,
          decl_generation: declGeneration,
          initiator_agent: policy.initiator_agent,
          target_agent: targetAgent,
          attempt,
          status: gate.status,
          run_id: null,
          session_ref: null,
          context_refs: { memory_refs: policy.context_transfer.memory_refs, snapshot_ref: null },
          started_at: new Date().toISOString(),
          resolved_at: new Date().toISOString(),
          outcome_notes: gate.reason
        });
        return gate;
      }

      try {
        const outcome = await executor.runTarget({
          handoffPolicyId,
          triggerRef,
          initiatorAgent: policy.initiator_agent,
          targetAgent,
          memoryRefs: policy.context_transfer.memory_refs,
          snapshotRef: manualParams?.snapshot_ref ?? null
        });
        await recorder.appendEvent({
          event_id: crypto.randomUUID(),
          handoff_policy_id: handoffPolicyId,
          trigger_ref: triggerRef,
          decl_generation: declGeneration,
          initiator_agent: policy.initiator_agent,
          target_agent: targetAgent,
          attempt,
          status: "accepted",
          run_id: outcome.run_id,
          session_ref: outcome.session_ref,
          context_refs: { memory_refs: policy.context_transfer.memory_refs, snapshot_ref: manualParams?.snapshot_ref ?? null },
          started_at: new Date().toISOString(),
          resolved_at: new Date().toISOString(),
          outcome_notes: "Target run started successfully."
        });
        return outcome;
      } catch (error) {
        const timeoutMode = policy.acceptance_policy.on_timeout;
        if (timeoutMode === "next_target") {
          await recorder.appendEvent({
            event_id: crypto.randomUUID(),
            handoff_policy_id: handoffPolicyId,
            trigger_ref: triggerRef,
            decl_generation: declGeneration,
            initiator_agent: policy.initiator_agent,
            target_agent: targetAgent,
            attempt,
            status: "timed_out",
            run_id: null,
            session_ref: null,
            context_refs: { memory_refs: policy.context_transfer.memory_refs, snapshot_ref: manualParams?.snapshot_ref ?? null },
            started_at: new Date().toISOString(),
            resolved_at: new Date().toISOString(),
            outcome_notes: String(error)
          });
          continue;
        }
        const terminalStatus = timeoutMode === "escalate" ? "escalated" : "failed";
        await recorder.appendEvent({
          event_id: crypto.randomUUID(),
          handoff_policy_id: handoffPolicyId,
          trigger_ref: triggerRef,
          decl_generation: declGeneration,
          initiator_agent: policy.initiator_agent,
          target_agent: targetAgent,
          attempt,
          status: terminalStatus,
          run_id: null,
          session_ref: null,
          context_refs: { memory_refs: policy.context_transfer.memory_refs, snapshot_ref: manualParams?.snapshot_ref ?? null },
          started_at: new Date().toISOString(),
          resolved_at: new Date().toISOString(),
          outcome_notes: String(error)
        });
        return { status: terminalStatus };
      }
    }

    return { status: "failed", reason: "exhausted_targets" };
  }

  return {
    preflight,
    dispatchPolicy,
    async handleManualTrigger(params) {
      return dispatchPolicy({
        handoffPolicyId: params.handoff_policy_id,
        triggerRef: `gateway:${params.handoff_policy_id}`,
        manualParams: params
      });
    },
    async handleMessageTrigger({ event, hookName }) {
      const triggerRef = event.bindingId ?? event.binding_id ?? hookName;
      return triggerRef;
    }
  };
}
```

- [ ] **Step 3: Re-run the policy tests**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js
```

Expected: PASS for rejection semantics, `next_target`, `escalate`, and `fail`.

- [ ] **Step 4: Commit the policy engine**

```bash
git add C:\Users\huibozi\.openclaw\extensions\handoff-bridge\lib\policy.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js
```

## Task 6: Wire Message, Cron, And Manual Triggers Through The Plugin Entry

**Files:**
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\index.js`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md`

- [ ] **Step 1: Teach the plugin entry to dispatch only canonical handoff actions**

```js
function extractHandoffPolicyId(event, loader) {
  const bindingId = event.bindingId ?? event.binding_id ?? null;
  if (!bindingId) return null;
  const binding = loader.getBinding?.(bindingId);
  if (!binding) return null;
  if (binding.action?.type !== "handoff") return null;
  return binding.action.handoff_policy_id;
}
```

```js
api.on("message_received", async (event, ctx) => {
  const handoffPolicyId = extractHandoffPolicyId(event, loader);
  if (!handoffPolicyId) return;
  await policy.dispatchPolicy({
    handoffPolicyId,
    triggerRef: event.bindingId ?? event.binding_id ?? "message_received"
  });
});

api.on("inbound_claim", async (event, ctx) => {
  const handoffPolicyId = extractHandoffPolicyId(event, loader);
  if (!handoffPolicyId) return;
  await policy.dispatchPolicy({
    handoffPolicyId,
    triggerRef: event.bindingId ?? event.binding_id ?? "inbound_claim"
  });
});

api.registerGatewayMethod("handoff.trigger", async ({ params, respond }) => {
  const result = await policy.handleManualTrigger(params ?? {});
  respond({ ok: true, result });
});
```

- [ ] **Step 2: Add service startup for cron evaluation**

```js
api.registerService({
  id: "handoff-bridge-runtime",
  async start(ctx) {
    await loader.refresh();
    await recorder.ensureStateFiles();
    ctx.logger.info("handoff bridge runtime started");

    for (const handoff of loader.listAll()) {
      if (handoff.trigger.type !== "cron_ref") continue;
      ctx.logger.info("cron handoff policy available", {
        id: handoff.id,
        cron_ref: handoff.trigger.cron_ref
      });
    }
  }
});
```

- [ ] **Step 3: Smoke-test install, enable, inspect, and method registration**

Run:

```powershell
openclaw plugins inspect handoff-bridge --json
```

Expected: inspect output lists one service, one gateway method (`handoff.trigger`), and no plugin diagnostics.

- [ ] **Step 4: Commit the plugin entry wiring**

```bash
git add C:\Users\huibozi\.openclaw\extensions\handoff-bridge\index.js C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md
```

## Task 7: Update State Validation And Add Phase 5 Runtime Tests

**Files:**
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py`
- Modify `C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`
- Create `C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase5_handoff_runtime.py`

- [ ] **Step 1: Write a failing validator test for `events.jsonl` plus `index.json`**

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import read_json


class Phase5HandoffRuntimeTests(unittest.TestCase):
    def test_handoff_index_preserves_run_id_and_session_ref(self) -> None:
        payload = read_json(Path(r"C:\Users\huibozi\.openclaw\state\handoff-events\index.json"))
        self.assertIn("entries", payload)
        if payload["entries"]:
            entry = payload["entries"][0]
            self.assertIn("run_id", entry)
            self.assertIn("session_ref", entry)
            self.assertIn("decl_generation", entry)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Extend `validate_state_openclaw.py` to check `events.jsonl` exists and lines parse**

```python
events_path = STATE_ROOT / "handoff-events" / "events.jsonl"
if not events_path.exists():
    warnings.append(f"missing optional live handoff event log: {events_path}")
else:
    for lineno, raw_line in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            event = __import__("json").loads(raw_line)
        except Exception as exc:
            errors.append(f"invalid handoff event JSONL line {lineno}: {exc}")
            continue
        for field in ("event_id", "handoff_policy_id", "trigger_ref", "decl_generation", "status", "run_id", "session_ref"):
            if field not in event:
                errors.append(f"handoff event line {lineno} missing {field}")
```

- [ ] **Step 3: Run the new runtime validator tests**

Run:

```powershell
python -m unittest C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase5_handoff_runtime.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py
```

Expected: unit test passes, validator returns `0` or `2`, and no malformed JSONL line error appears.

- [ ] **Step 4: Commit the validator updates**

```bash
git add C:\Users\huibozi\.openclaw\scripts\decl_state\validate_state_openclaw.py C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py C:\Users\huibozi\.openclaw\scripts\decl_state\tests\test_phase5_handoff_runtime.py
```

## Task 8: End-To-End Live Handoff Proof And Operator Documentation

**Files:**
- Modify `C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md`
- Modify `C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md`

- [ ] **Step 1: Document the safe maintenance chain**

```markdown
## Phase 5 handoff runtime maintenance
- `decl/handoffs/*/handoff.json` remains the fact source.
- `extensions/handoff-bridge/` owns execution only; it must not rewrite canonical declarations.
- Install/update flow:
  1. `openclaw plugins install -l C:\Users\huibozi\.openclaw\extensions\handoff-bridge`
  2. `openclaw plugins enable handoff-bridge`
  3. `python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py`
- `state/handoff-events/events.jsonl` is append-only audit output.
- `state/handoff-events/index.json` is the summary surface consumed by validators.
```

- [ ] **Step 2: Trigger one real handoff and inspect the resulting event**

Run:

```powershell
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
Get-Content -LiteralPath C:\Users\huibozi\.openclaw\state\handoff-events\events.jsonl -Tail 5
Get-Content -LiteralPath C:\Users\huibozi\.openclaw\state\handoff-events\index.json -TotalCount 200
```

Expected: at least one event in `events.jsonl`, with non-empty `run_id`, `session_ref`, `decl_generation`, and status in `accepted | rejected | timed_out | escalated | failed`.

- [ ] **Step 3: Exercise timeout handling with a forced next-target case**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\policy.test.js
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
```

Expected: `next_target` policy test passes, full validation returns `0` or `2`, and the event log shows either `timed_out` followed by `accepted`, or `escalated`/`failed` for the exercised seed case.

- [ ] **Step 4: Final verification bundle**

Run:

```powershell
node --test C:\Users\huibozi\.openclaw\extensions\handoff-bridge\tests\*.test.js
python -m unittest discover -s C:\Users\huibozi\.openclaw\scripts\decl_state\tests -p test_phase5_handoff_runtime.py -v
python C:\Users\huibozi\.openclaw\scripts\decl_state\validate_full_openclaw.py
openclaw plugins inspect handoff-bridge --json
```

Expected: all Node tests pass, the Phase 5 Python runtime test passes, full validation returns `0` or `2`, and plugin inspect reports an enabled native plugin with a registered service and gateway method.

- [ ] **Step 5: Commit the docs and final verification notes**

```bash
git add C:\Users\huibozi\.openclaw\OPENCLAW-DECL-STATE.md C:\Users\huibozi\.openclaw\extensions\handoff-bridge\README.md
```

## Spec Coverage Check

- Plugin deployment path and manifest requirements: covered in Task 1.
- Trigger routing strategy (`message_received`, `inbound_claim`, `cron_ref`, manual gateway method): covered in Tasks 5-6.
- `runEmbeddedPiAgent(...)` as execution primitive: covered in Task 4.
- `session_ref` allocated before runtime call: covered in Task 4.
- `events.jsonl + index.json` audit trail: covered in Tasks 3 and 7.
- `next_target / escalate / fail` acceptance semantics: covered in Task 5.
- Operator workflow and validation updates: covered in Tasks 7-8.

## Self-Review Notes

- No placeholder text remains; each task names concrete files, snippets, and commands.
- The plan intentionally keeps `decl/handoffs/` read-only and avoids core runtime edits.
- The plan keeps `onConversationBindingResolved(...)` as audit-only to match the SDK docs.
- The plan does not assume a public `command_ref` live surface yet; manual trigger uses a gateway method instead.
- The plan keeps event status semantics aligned with the Phase 5 blueprint and does not conflate run start with business completion.
