---
name: scope-discipline
description: Keep agent changes to the smallest coherent scope that solves the requested problem while preserving architecture and compatibility.
---

# Scope Discipline

## Intent
Reduce accidental churn, hidden regressions, and opportunistic refactoring during agent-driven work.

## Evidence to inspect
- The user request or issue scope.
- Existing architecture, ownership boundaries, and compatibility contracts.
- Diffs that touch files unrelated to the requested outcome.

## Decision
Determine the smallest coherent change that solves the problem without creating duplicate abstractions or violating established boundaries.

## Execution
- Modify only files required for the requested outcome.
- Preserve existing public APIs, access boundaries, naming conventions, and architecture unless the task explicitly requires a design change.
- Report unrelated findings separately instead of silently fixing them.
- Treat permission widening, exported API additions, and template changes as design-level changes.

## Recovery
If the requested fix requires wider changes than expected, isolate why and either narrow the solution or explicitly surface the scope expansion before continuing.

## Failure modes
- Drive-by cleanup mixed into the requested change.
- Broad refactors justified only by local convenience.
- Expanding permissions or public APIs without recognizing the design impact.
- Optimizing for minimal line count at the expense of coherent architecture.
