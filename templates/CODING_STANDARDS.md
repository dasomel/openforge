# CODING_STANDARDS.md

Use this file for detailed coding guidance that should not occupy the always-loaded root `AGENTS.md` context.

## Readability

- Prefer early returns or `continue` when they reduce nesting and clarify the main path.
- Preserve established naming conventions. Do not impose arbitrary universal name-length limits.
- Add whitespace between logical blocks when it improves scanability.
- Extract repeated, meaningful, or specification-defined magic values into named constants/types.
- Keep trivial one-off values inline when extraction would only add indirection.

## Interfaces

- Prefer a domain enum/type over a boolean flag when states have meaningful semantics.
- Keep access as narrow as the design permits.
- Treat visibility widening and exported API additions as design changes.
- Do not proliferate near-duplicate methods merely to minimize changed lines; prefer the smallest coherent API.

## Comments and documentation

- Comments explain **why**, invariants, hazards, compatibility constraints, or surprising trade-offs.
- Do not narrate what straightforward code already says.
- Use examples or ASCII diagrams when they materially improve understanding of a workflow, protocol, state machine, or architecture.
- Update documentation when behavior, architecture, interfaces, or operational procedures change.

## Architecture boundaries

- Keep low-level hardware, filesystem, database, socket, protocol, cloud-provider, or external-tool behavior behind the appropriate abstraction.
- UI/controllers should use domain/service APIs instead of directly reaching lower infrastructure layers.
- Respect adjacent-layer communication and repository-specific boundaries.
- Do not bypass an existing service/adapter solely because a direct call is shorter.

## Change scope

- Make the smallest coherent change that solves the requested problem.
- Do not modify unrelated code or documentation; report unrelated findings separately.
- Avoid opportunistic cleanup in a bug fix unless it is necessary for the fix or explicitly requested.
- A small diff is desirable, but not when it causes duplicate APIs, hidden coupling, fragile wrappers, or worse maintainability.

## Tests and bugs

Preferred bug workflow:

```text
reproduce -> failing test/evidence -> minimal fix -> same test passes -> regression suite
```

Tests should reproduce the externally observable defect or violated invariant, not merely assert the intended implementation.

Distinguish mocked/unit evidence from integration and real runtime evidence.

## Deterministic rules

Formatter/linter/static-analysis rules should be implemented in tooling and CI rather than duplicated here where practical.

Examples:

- formatting/braces
- import order
- language-supported naming restrictions
- static analysis
- dependency/security policy
- generated-file checks
- schema validation

Document the reason here only when the rule represents a non-obvious engineering invariant.
