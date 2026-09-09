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
2. Reproduce or establish executable evidence before changing behavior when fixing a defect.
3. Make the smallest coherent change inside the owned scope.
4. Use deterministic scripts/tools for repeatable steps instead of rewriting them in prose.
5. Run the verification appropriate to the changed path.

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
- Relevant architecture/design/development documentation
- Relevant scripts/tests/Makefile targets
