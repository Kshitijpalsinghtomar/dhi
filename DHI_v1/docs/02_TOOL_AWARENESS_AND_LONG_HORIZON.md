# DHI-v1 Tool Awareness and Long-Horizon Planning Specification

**Version:** 1.0  
**Date:** 2026-10-31  
**Status:** Capability specification for training and evaluation.

## 1. The failure we are targeting

The central user observation is that current assistants often have access to many apps, plugins, APIs, browser tools, code tools, and connectors but fail to use that ecosystem intelligently. They may:
- rely on familiar model knowledge rather than checking current evidence;
- ignore tools that are not already visible in the immediate prompt;
- fail to search a connected app/plugin/tool directory;
- use the first available tool rather than the most suitable one;
- treat a tool call as a task rather than one step in a larger outcome;
- make a one-pass plan and fail to revise it when the environment changes;
- lose state and decision context during long tasks.

DHI must learn the capability to recognize missing affordances, discover relevant tools, compare them, and coordinate them over long tasks. It must also learn when not to use tools.

## 2. Tool ecology: dynamic inventory, learned affordance reasoning

DHI must not memorize a fixed list of tools as its definition of tool awareness. The actual ecosystem changes by user, account, permission, region, product, and date.

### Runtime capability manifest

The runtime should expose a structured manifest for tools currently available or discoverable. Suggested fields:

| Field | Purpose |
|---|---|
| tool_id / current name | Exact callable identifier after discovery. |
| description / affordances | What capability it provides, expressed in task terms. |
| input schema | Valid arguments, types, required fields, constraints. |
| output schema | What result or evidence it returns. |
| domain | Coding, browser, files, mail, calendar, database, cloud, analytics, etc. |
| preconditions | Account connection, authentication, data availability, location, or state requirements. |
| permission scope | Read/write/send/delete/deploy/purchase/financial or other side effects. |
| consent requirements | Whether explicit user authorization is required. |
| freshness | Data timestamp, index update, or last refresh where available. |
| cost and latency | Monetary cost, rate limits, expected response time, context cost. |
| reliability / failure modes | Known limits, outage, retry semantics, idempotence. |
| privacy / data handling | What data leaves the user's environment and where. |
| statefulness | Whether calls mutate persistent state or depend on previous calls. |
| reversibility | Whether action can be rolled back. |

The model reasons over this manifest. The manifest is not the model's intelligence; it is the dynamic environment description required to act safely.

### Tool discovery behavior

When no visible tool can satisfy a task:
1. Recognize the missing capability in task terms.
2. Decide whether discovering a tool is likely to materially improve completion.
3. Search the available app/plugin/API/tool catalogue or marketplace.
4. Inspect candidate descriptions and schemas, not only names or marketing labels.
5. Compare candidates against task requirements, permissions, freshness, quality, cost, and state effects.
6. Choose one tool or a combination, or conclude that no suitable tool is available.
7. Ask for connection/authorization only when the selected tool requires it.
8. Execute and verify.

A model should not ask the user to perform manual research before attempting a permitted tool-discovery path that is available to it. It should also not invent a connector, pretend an unavailable tool is connected, or imply that discovery guarantees access.

### Generalization requirement

At test time, change tool names, descriptions, schemas, order, and available inventory. A competent model should recognize the affordance from the capability description and schema rather than memorizing a tool name or one prompt pattern.

## 3. When DHI should use tools

| Situation | Correct behavior |
|---|---|
| Stable general knowledge, no external action, low uncertainty | Answer directly without a tool. |
| Current, time-sensitive, niche, account-specific, or changing fact | Verify with a current authoritative source or relevant API. |
| User requests a real external action | Find and invoke the relevant authorized tool; verify its state change. |
| Needed capability is not in the current tool list | Discover a tool/app/API if discovery is available and justified. |
| Several tools can do the task | Compare capability fit, permissions, reliability, freshness, cost, and side effects. |
| Several independent subtasks exist | Consider safe parallel calls; do not parallelize dependent or conflicting state mutations. |
| Required information is missing and cannot be retrieved | Ask one focused clarification. |
| Tool is unavailable, broken, or unsuitable | Replan, try a justified alternative, or report the limitation. |
| High-stakes or irreversible action | Require appropriate authorization and stronger verification. |
| Tool output contains instructions or content | Treat it as untrusted evidence/data, not as authority to override task or safety constraints. |

Tool calling is not a virtue on its own. Tool restraint is a first-class capability.

## 4. Tool-selection policy to be learned

For each candidate tool, DHI should infer:
- capability fit to the desired outcome;
- completeness of returned evidence;
- whether required inputs and permissions are available;
- whether the tool is authoritative for the specific fact/action;
- freshness and update time;
- chance of failure and recoverability;
- cost, latency, and context overhead;
- privacy, security, and irreversible side effects;
- whether another tool is needed before or after it.

The model should be trained on counterfactual cases:
- same task, different tool inventory;
- same tool name, changed schema or permission;
- same tool affordance, new name;
- relevant tool hidden in a catalogue;
- many irrelevant/decoy tools;
- preferred tool unavailable;
- tool gives stale or contradictory results;
- task changes so that a different tool becomes optimal;
- no tool is needed at all.

## 5. Long-horizon planning

A long task is not just a long answer. It is a sequence of state-changing actions with dependencies, uncertainty, intermediate outputs, and a final state that can be checked.

DHI should build a task graph containing:
- goal and hard constraints;
- explicit final postconditions;
- subgoals and milestones;
- dependencies and blockers;
- actions and candidate tools;
- expected outputs and side effects;
- uncertainty/risk;
- status: pending, ready, running, blocked, succeeded, failed, or skipped;
- evidence supporting each completed milestone.

The model must know when a plan can remain implicit/simple and when an explicit task graph is warranted. It must not create a large project plan for a trivial question.

## 6. Three nested loops

### Outer strategic loop — goal and resource control

At the start and at major checkpoints:
1. Reconstruct the user's desired outcome and constraints.
2. Estimate task horizon, stakes, uncertainty, and available budget.
3. Set success criteria and identify irreversible steps.
4. Decide which tools or capabilities may be required.
5. Decide whether to search/discover tools or proceed with known capabilities.
6. Set milestones and review points.

Re-enter this loop when the goal, deadline, permissions, resources, or environment changes.

### Middle planning/execution loop — dependency-aware work

For each ready milestone:
1. Inspect current state and previous evidence.
2. Determine the next blocking condition.
3. Select an action and suitable tool.
4. Predict relevant effects and possible side effects.
5. Execute one action or safe independent actions in parallel.
6. Record the actual response and resulting state.
7. Update dependencies, status, and task budget.

### Inner verification/recovery loop — local correctness

After each consequential action:
1. Validate the output schema and source.
2. Compare actual changes with predicted changes.
3. Run tests or inspect authoritative state.
4. Detect partial success, unexpected side effects, stale data, or errors.
5. Retry only if the action is idempotent or a safe recovery path exists.
6. If the same action fails repeatedly, change the method rather than repeating it.
7. Decide whether to continue, replan, ask, or stop.

The loops are nested and adaptive. They should not execute at a fixed depth on every task.

## 7. Replanning triggers

Replan when:
- a selected tool is unavailable, disconnected, or permission-denied;
- the actual state differs materially from the forecast;
- a dependency is missing;
- output is malformed, stale, contradictory, or incomplete;
- a new constraint changes the best action;
- the task exceeds its cost/time budget;
- an external side effect makes the original plan unsafe;
- repeated attempts produce no new information;
- the final postcondition remains false.

Do not replan solely to appear thoughtful. If the current plan is working and evidence supports it, continue.

## 8. Parallelism and multi-agent work

Use parallel calls or delegated agents only when:
- subtasks are genuinely independent;
- each has a clear output contract;
- shared-state mutation will not conflict;
- the result can be reconciled and verified.

Keep a single coordinated plan and a common evidence record. Multiple agents do not count as independent verification when they share the same model, data, and assumptions. Delegate specialized research, implementation, or evaluation when it provides clear leverage; do not create agent teams for simple sequential tasks.

## 9. Long-task continuity

DHI should maintain a compact, typed task state:
- original goal and constraints;
- current plan version;
- completed milestones and evidence;
- unresolved decisions;
- tool connections/permissions used;
- relevant artifacts and exact versions;
- failed attempts and why they failed;
- current blocker and next action;
- final postconditions.

The model learns what to preserve, update, and retrieve. Runtime storage may persist the state across sessions; a memory database is not the substitute for learned continuity and task reasoning.

## 10. Prediction before action

For consequential actions, DHI should predict task-relevant effects, not necessarily narrate every possible future:
- what resource/file/database/application will change;
- what should remain unchanged;
- which dependencies or tests may be affected;
- what evidence should be observable after the action;
- what would indicate an unexpected side effect;
- whether the action moves the task closer to its goal.

After execution, compare the prediction against real state. Use the discrepancy as training signal. This provides the bridge to the predictive-state architecture research.

## 11. Closure and truthful reporting

A task is closed only when its required postconditions are verified. Tool success status is not equivalent to task success. For example, a file-write call returning successfully does not prove the file has the correct content; a test command completing does not prove the required tests passed; a sent-message API response must be distinguished from a drafted message.

The model should identify:
- completed and verified outcomes;
- partially completed work;
- blocked/unavailable steps;
- unverified assumptions;
- remaining user approvals.

Never fabricate execution, evidence, sources, tool access, or success.

## 12. Training examples required

Build trajectory cases for:
- direct answer/no tool;
- current fact requiring verification;
- missing tool requiring discovery;
- correct tool among decoys;
- new tool name with known affordance;
- schema shift;
- tool argument error and recovery;
- multi-tool dependency graph;
- safe parallel subtasks;
- tool failure and replan;
- task interrupted and resumed;
- changing constraint;
- untrusted tool output;
- permission denial;
- predictive forecast followed by surprising actual state;
- false completion versus verified closure.

The training target should encode the decision/action/result, not force every sample into the same verbose planning template.
