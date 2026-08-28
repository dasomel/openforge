---
name: task-convergence
description: Drive substantive agent work toward a verified complete state, verified progress with an isolated blocker, or an evidence-based stop.
---

# Task Convergence

## Intent
Prevent long-running agent work from confusing activity with progress.

## Evidence to inspect
- The requested outcome and acceptance criteria.
- Verification completed so far.
- The current blocker and whether new attempts reduce uncertainty.

## Decision
Classify the task outcome as one of three states:

- **A — Complete:** intended behavior works on the relevant path and appropriate verification passes.
- **B — Meaningful progress:** one or more verified blockers were removed and the next blocker is isolated with evidence.
- **C — Stop:** further work would require unjustified scope expansion, fragile patches, unsupported assumptions, or unacceptable risk.

## Execution
- Prefer actions that close acceptance criteria or reduce uncertainty.
- Record blockers with concrete evidence.
- Do not continue repeated low-information attempts merely to appear active.

## Recovery
When an attempt fails, use the result to narrow the problem, strengthen evidence, change strategy, or justify stopping. If it does none of these, do not repeat it unchanged.

## Failure modes
- Reporting many edits as progress without verified outcomes.
- Repeating failing approaches without gaining information.
- Hiding an unresolved blocker behind completion language.
- Continuing after the only remaining paths require unjustified risk or scope.
