# Agent Engineering Standard

OpenForge treats repository instructions as an engineering control, not as a dumping ground for every coding preference.

## Layered instruction model

```text
AGENTS.md
  -> short execution contract
  -> scope, boundaries, verification, escalation

CODING_STANDARDS.md
  -> detailed coding and review guidance

CONTRIBUTING.md / DESIGN.md / architecture docs
  -> project-specific process and design context

formatter / linter / tests / policy-as-code / CI
  -> deterministic enforcement
```

Keep `AGENTS.md` short enough to remain salient in long sessions. Do not duplicate rules already enforced reliably by tools.

## Root AGENTS.md rules

A project-level `AGENTS.md` should normally contain only the following classes of instruction:

1. source-of-truth documents to read before editing
2. allowed and forbidden scope
3. architecture and access-boundary constraints
4. canonical build/test/verification entrypoints
5. bug-fix reproduction policy
6. evidence required before claiming completion
7. escalation/stop conditions
8. project-specific high-risk paths that cannot be inferred from code

## Scope discipline

Make the smallest **coherent** change that solves the requested problem.

- Do not modify unrelated code merely because an issue is noticed.
- Report unrelated findings separately.
- Do not optimize for minimum line count when that would create duplicate APIs, wrapper proliferation, or a worse abstraction.
- Preserve established architecture and layer boundaries.
- Treat `private -> internal/public`, exported symbol additions, API widening, RBAC widening, and permission widening as design changes.

## Coding guidance

Detailed coding preferences belong in `CODING_STANDARDS.md` or language tooling.

Recommended judgment rules:

- Prefer early returns when they improve readability and reduce nesting.
- Prefer a domain enum/type over a boolean flag when the states have semantic meaning.
- Extract repeated, meaningful, or specification-defined magic values into named constants/types.
- Leave trivial one-off values inline when extraction adds noise.
- Comments explain **why**, invariants, hazards, compatibility constraints, or non-obvious trade-offs. Do not narrate obvious code.
- Use examples or ASCII diagrams only when they materially improve understanding.
- Keep low-level hardware, filesystem, socket, storage, protocol, or database behavior behind the appropriate abstraction boundary.
- Prefer domain APIs over leaking low-level implementation details upward.
- Preserve project naming conventions rather than enforcing arbitrary universal name-length limits.

## Bug-fix workflow

Preferred sequence:

```text
reproduce
  -> failing regression test or executable evidence
  -> minimal fix
  -> same test/evidence passes
  -> relevant regression suite
```

Do not write a test that merely encodes the proposed implementation. The reproduction must demonstrate the user-visible or system-visible defect.

If an automated regression test is impractical, record the executable reproduction and explain why deterministic automation is not feasible.

## Evidence over claims

A completion statement is not evidence. Report the checks actually run and their scope.

Distinguish evidence classes:

- unit/stub/mocked tests
- integration tests
- real runtime/cluster/device/filesystem verification
- static analysis/lint
- security/policy checks
- build/package verification

Do not imply that a lower-level evidence class proves a higher-level runtime property.

## Convergence model

Every substantive task should end in one of three states:

### A — Complete
The intended behavior works on the relevant path and appropriate verification passes.

### B — Meaningful progress
The task is not complete, but one verified blocker was removed and the next blocker is isolated with evidence.

### C — Stop
Further work would require unjustified scope expansion, fragile patches, unsupported assumptions, or unacceptable risk. Report the evidence and stop.

Activity is not progress. A failed attempt is useful only when it narrows the problem, improves evidence, or justifies stopping.

## Context-dilution control

- Keep root instructions concise.
- Put detailed standards in linked files loaded when needed.
- Start a fresh session for an unrelated feature when practical.
- Reload repository instructions after long investigations when instruction adherence degrades.
- Do not duplicate formatter/linter rules in prose unless the prose explains a non-obvious reason.

## Agent-specific files

`CLAUDE.md`, `GEMINI.md`, tool-specific rules, or local skills may coexist with `AGENTS.md`.

Use them for tool-specific behavior or project-specific high-risk context. Do not fork generic engineering rules across multiple files.

Existing high-value gotcha files should be preserved and referenced rather than replaced by a generic template.

## Commit guidance

Follow the repository's existing commit convention first.

Where no convention exists, use a concise imperative subject and explain **what** and **why** in the body when context is necessary. Formatting rules that can be validated automatically should be enforced by tooling rather than repeated in agent prompts.
