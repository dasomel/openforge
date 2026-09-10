# Agent Engineering Standard

OpenForge treats repository instructions as an engineering control, not as a dumping ground for every coding preference.

For the canonical model-independent instruction architecture, progressive disclosure, autonomy boundaries, compatibility overrides, and instruction-debt auditing, see [Model-Agnostic Agent Instruction Design](model-agnostic-agent-instructions.md).

## Layered instruction model

```text
AGENTS.md
  -> short execution contract
  -> scope, boundaries, verification, escalation

behaviors / skills
  -> task-specific conduct and workflow selection

references / scripts
  -> detail loaded only when relevant

CLAUDE.md / GEMINI.md / tool-specific rules
  -> thin runtime adapters

formatter / linter / tests / policy-as-code / CI
  -> deterministic enforcement
```

Keep `AGENTS.md` short enough to remain salient in long sessions. Inspect only guidance relevant to the current task; do not require every document to be loaded before every edit. Do not duplicate rules already enforced reliably by tools.

## Agent execution security

When an agent can call tools, APIs, Kubernetes, host operations, data-egress paths, or other side-effecting capabilities, repository instructions alone are not an authorization boundary.

Use the [Agent Execution Security Contract](agent-execution-security.md) ([한국어](agent-execution-security-ko.md)) for canonical invocation resolution, capability attenuation, exact-call approval binding, sandbox enforcement, post-state verification, and recomputable execution evidence.

## Root AGENTS.md rules

A project-level `AGENTS.md` should normally contain only instructions relevant to nearly every substantive task, such as:

1. how to locate task-relevant source-of-truth guidance
2. allowed and forbidden scope
3. architecture and access-boundary constraints
4. canonical verification expectations or entrypoints
5. bug-fix reproduction policy
6. evidence required before claiming completion
7. safe autonomy and explicit-authorization boundaries
8. escalation/stop conditions
9. project-specific high-risk paths that cannot be inferred from code

Task-specific workflows belong in behaviors/skills and supporting references rather than the root contract.

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

Preferred sequence when the defect is reproducible:

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

Verification should be proportional to the change's risk and user impact. For user-facing, installation, configuration, upgrade, integration, or high-risk changes, use the relevant portions of the [User-Centric Validation Standard](user-centric-validation.md). A trivial change does not need every validation gate; a high-risk runtime change may need several.

## Safe autonomy

Within the requested scope, safe local and reversible work may normally continue without repeated approval: relevant inspection, editing, build/lint/test execution, fixing failures caused by the change, and re-running verification.

Explicit authorization is required unless already granted for production/shared-environment mutation, destructive or irreversible external actions, credential/permission changes beyond the requested design, release/publish actions, paid-resource changes, or unrelated repository/external-system mutations.

## Convergence model

Every substantive task should end in one of three states:

### A — Complete
The intended behavior works on the relevant path and appropriate verification passes.

### B — Meaningful progress
The task is not complete, but one verified blocker was removed and the next blocker is isolated with evidence.

### C — Stop
Further work would require unjustified scope expansion, fragile patches, unsupported assumptions, or unacceptable risk. Report the evidence and stop.

Activity is not progress. A failed attempt is useful only when it narrows the problem, improves evidence, or justifies stopping.

Prefer this outcome contract over rigid universal procedures. Continue through implementation, relevant verification, and fixes caused by the change until one of these states is reached.

## Context-dilution control

- Keep root instructions concise.
- Load detailed standards and references only when relevant to the task.
- Move repeatable task workflows into narrowly triggered skills/behaviors.
- Do not duplicate formatter/linter rules in prose unless the prose explains a non-obvious reason.
- Audit stale, duplicate, or over-broad instructions periodically with `.agents/behaviors/instruction-debt-audit/BEHAVIOR.md` and `templates/scripts/audit-instruction-debt.py`.

## Agent-specific files

`CLAUDE.md`, `GEMINI.md`, tool-specific rules, or local runtime files may coexist with `AGENTS.md`.

Treat them as thin adapters: keep runtime syntax, hooks, orchestration, or unique capability guidance there, but do not fork generic engineering rules across models.

Model-specific compatibility guidance should be added only for repeated observed failures backed by an eval, issue, trace, or reproducible case, with a minimal mitigation and a review/removal condition.

Existing high-value gotcha files should be preserved and referenced rather than replaced by a generic template.

## Commit guidance

Follow the repository's existing commit convention first.

Where no convention exists, use a concise imperative subject and explain **what** and **why** in the body when context is necessary. Formatting rules that can be validated automatically should be enforced by tooling rather than repeated in agent prompts.
