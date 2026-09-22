---
name: project-task
description: Perform a specific repeatable project task. Use when the requested work matches this project workflow or its owned paths.
license: Apache-2.0
compatibility: Requires the repository checkout and the documented project toolchain.
metadata:
  openforge-scope: project
  openforge-owner: owner/repository
  openforge-maturity: draft
  openforge-version: "1"
---

# Project Task

## Use When

- The task is specific to this repository or domain workflow.
- Repeating the task would otherwise require rediscovering project conventions or failure modes.

## Do Not Use When

- The task is generic and the model/tool already handles it reliably without project knowledge.
- The task is fully enforced by an existing script, test, formatter, linter, or policy; call that executable control instead.

## Inputs

- Requested outcome and relevant issue/spec.
- Repository state and owned paths.
- Any runtime/environment prerequisites required by this workflow.

## Workflow

1. Read the source-of-truth documents and inspect the current repository state.
2. Classify non-trivial work. For Class C/D or complex cross-component work, confirm an accepted Change Package defines requirements, acceptance scenarios, tasks, verification and recovery before broad implementation.
3. Reproduce or establish executable evidence before changing behavior when fixing a defect.
4. Make the smallest coherent change inside the owned scope.
5. Use deterministic scripts/tools for repeatable steps instead of rewriting them in prose.
6. Run the verification appropriate to the changed path and map the result back to the acceptance scenarios.

## Verification

- State exactly which checks ran and their scope.
- Distinguish unit/stub evidence from real runtime/integration evidence.
- Name any important path that remains unverified.

## Stop / Escalate When

- The task would widen permissions, APIs, destructive scope, or architecture boundaries without an approved design.
- Required evidence cannot be obtained without unsupported assumptions or unsafe execution.
- Continued patching is no longer converging on the requested outcome.

## References

- `AGENTS.md`
- `docs/change-management.md`
- `templates/change/CHANGE.md`
- `templates/change/TASKS.md`
- Relevant architecture/design/development documentation
- Relevant scripts/tests/Makefile targets
