# Engineering Judgment for Agent Work

Status: human-judgment guidance. It is not enforced by any script, test, or CI check, and it has **no measured effect yet**. Treat it as a reviewed starting point, not as evidence that agents behave better when they follow it. If a measurement is ever made, it must follow [Research Evidence](research-evidence.md).

This page distills nine habits of judgment for agent-assisted engineering. It adds to, and does not restate, the existing OpenForge standards: where a standard or behavior already owns a rule, this page links to it. Per [AGENTS.md](../AGENTS.md), anything here that can be enforced reliably should move into a script, test, or CI rather than grow as prose (see principle 4).

## Provenance

The principles are a distillation of the pstack skill collection by Lauren Tan (`poteto`), published at <https://github.com/cursor/plugins/tree/main/pstack> under the MIT License, Copyright (c) 2026 Lauren Tan. The pstack version read for this distillation was 0.15.36. The wording here is OpenForge's own; no pstack text is reproduced, so the MIT notice is not required to travel with this page, but the origin is credited here. Applying the ideas to OpenForge was done by the maintainer on 2026-11-13.

## How to use this page

Apply the principles the task actually touches; most tasks touch two or three. Each entry gives when it applies and how it relates to existing standards.

## The nine principles

### 1. Smallest change, subtraction first
Name the smallest change that meets the goal and remove dead weight before adding anything. No speculative guards, layers, or abstractions beyond what the requirement demands. If the evidence shows the requested change is unnecessary, show the evidence and stop.
- Applies: any edit, especially when the first idea adds code.
- Relates to: [`scope-discipline`](../.agents/behaviors/scope-discipline/BEHAVIOR.md) and the "smallest coherent change" rule in [AGENTS.md](../AGENTS.md). This principle adds the explicit permission to conclude "no change".

### 2. Root cause, not symptom
Reproduce first, fix the first place the system went wrong, and look for other instances of the same fault. A guard, retry, clamp, or swallowed error counts as a fix only when the state it handles is legitimate.
- Applies: bug fixes and flaky behavior.
- Relates to: [`bug-fix-verification`](../.agents/behaviors/bug-fix-verification/BEHAVIOR.md) (reproduce, minimal fix, regression evidence). New here: sweep for sibling instances.

### 3. Attack the premise
After two failed fixes that share an assumption, write the assumption down and test it directly before a third attempt.
- Applies: repeated failure on one problem.
- Relates to: [`task-convergence`](../.agents/behaviors/task-convergence/BEHAVIOR.md), which asks for an evidence-based stop rather than blind retries.

### 4. Build the lever
For non-trivial or repeated work, write a re-runnable script, codemod, or check that does or proves the work. A lesson written twice should become a lint, check, or script instead of more prose.
- Applies: repetitive edits, anything a reviewer would want to re-run.
- Relates to: the separation of declarative standards, executable checks, and judgment in [AGENTS.md](../AGENTS.md) and [Model-Agnostic Agent Instruction Design](model-agnostic-agent-instructions.md); [`instruction-debt-audit`](../.agents/behaviors/instruction-debt-audit/BEHAVIOR.md).

### 5. Verifiable units
Work in small steps that each end in a check, and verify one before starting the next. Failing test first, then the fix.
- Applies: multi-step changes.
- Relates to: [`evidence-before-claim`](../.agents/behaviors/evidence-before-claim/BEHAVIOR.md) and `bug-fix-verification`.

### 6. Test behavior, not implementation
A test should fail when the behavior breaks and survive a refactor. Expected values come from the requirement, never from running the code under test.
- Applies: writing or reviewing tests.
- Relates to: `bug-fix-verification`. No existing standard forbids deriving expected values from the implementation; this page does.

### 7. Explain the number
Before trusting or reporting a measurement, state what result would change a decision, the run count and spread, what limits the number, and what else it could be measuring (errors, cached or skipped work, code that never ran).
- Applies: benchmarks, coverage, timings, pass rates.
- Relates to: [Research Evidence](research-evidence.md), which owns how OpenForge measurements are recorded; this principle is the pre-report sanity check.

### 8. Shared state: separate before serializing, idempotent operations
Concurrent lanes get their own files, branches, and keys, merged at the read boundary; serialize only when a single write target is truly required. Operations should converge when re-run or resumed after a crash.
- Applies: parallel agents, migrations, retried CI or release steps.
- Relates to: no dedicated OpenForge standard owns this today; [Change Management](change-management.md) and [CI/CD Resilience](ci-resilience.md) are the nearest context.

### 9. Candor
"No" and "this does not earn its place" are valid answers. Agreement is not the default.
- Applies: reviews, plan feedback, requests whose premise looks wrong.
- Relates to: `evidence-before-claim` and [`trust-and-provenance`](../.agents/behaviors/trust-and-provenance/BEHAVIOR.md) in spirit; no behavior owns pushback explicitly.

## Evidence additions

Three additions complement `evidence-before-claim` and `trust-and-provenance`:

- **Real artifact, not a proxy.** Check the thing itself, not file mtimes, a worker's self-report, or cached output. When a check fails, suspect the observation method before the system.
- **Label claims.** State in the same sentence whether a claim is measured, inferred, or a guess.
- **Never cite what you did not read.** Do not cite a link or reference that was not read or produced in this session, and do not hand over a check you could have run yourself.

## Orchestrator guidance

For sessions that delegate to worker agents. These are practices, not requirements on every repository.

- Restate the user's goal in every worker brief. The orchestrator owns each worker's output: review the diff or evidence and write its own summary instead of passing "done" through.
- Send a new round (fix, retry, follow-up) to a fresh worker with consolidated scope (original brief, later directives, prior report, branch). Resume a worker only when the state lives in it, such as its checkout or a running process.
- A deterministic script beats a fan-out. When fanning out, give every lane one shared recipe and verification contract outside its write scope.
- A second opinion is the same prompt sent to a different vendor; agreement is a high-signal result.
- Before asking the user, classify the fork. A fact observable by running something is not theirs to answer: run it. Reversible work proceeds and is reported. Ask only for a product or preference call no experiment can settle, or before an irreversible or outward-facing action.

## One conflict, resolved

Principle 2 warns that a clamp can hide a bug, while the common habit of distrusting external input says to clamp untrusted values. Resolution: **validate and clamp at system boundaries (external input, tampered data) and trust internal types past them**. A clamp deeper inside the system is suspected of masking a defect and should be justified by legitimate state. Boundary cases (normal, mapped, none, tampered) still get tests.

## Deliberately not adopted

- **Model routing to a specific vendor or tier.** OpenForge stays model-agnostic; see [Model-Agnostic Agent Instruction Design](model-agnostic-agent-instructions.md).
- **Cursor-only features** (plugin commands, agents, and setup flows). They are tool-specific adapter material, not portfolio standards.
- **English prose-style rules.** OpenForge docs are bilingual; style is governed by [Documentation Standard](documentation.md).
- **The 23 playbooks.** Task workflows belong in narrowly scoped skills ([Agent Skills](agent-skills.md)), added when a repeated need is shown.
- **Autonomy to commit and take external actions without asking.** This conflicts with OpenForge's authorization boundaries ([Agent Execution Security Contract](agent-execution-security.md), [Agent Engineering Standard](agent-engineering.md)). Commits, pushes, and outward-facing actions stay subject to explicit authorization; the "classify the fork" guidance above applies only to reversible, local work.

## Not included

No enforced check, no new `.agents/behaviors/` entry, and no change to `templates/` accompanies this page. If a principle proves valuable, candidates for promotion are: a behavior for principle 9 or 8 (currently unowned), and a test-quality lint for principle 6.
