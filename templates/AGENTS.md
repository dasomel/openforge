# AGENTS.md

Read the repository's README, CONTRIBUTING, DESIGN/architecture docs, and project-specific instruction files before editing.

## Work contract

- Make the smallest coherent change that solves the requested problem.
- Do not modify unrelated code. Report unrelated findings instead.
- Preserve architecture/layer boundaries and existing access restrictions.
- Treat public/internal visibility, exported APIs, permissions, RBAC, and destructive behavior as design changes.
- Follow existing naming/style conventions; let formatter/linter rules own deterministic style.
- Comments explain why, invariants, hazards, or non-obvious constraints; do not narrate obvious code.

## Bugs

When feasible: reproduce -> failing regression test/evidence -> fix -> same test passes -> relevant regression suite.

If an automated regression test is impractical, record executable reproduction evidence and why automation is not feasible.

## Verification

Do not claim completion without relevant verification. State what was actually run and distinguish mocked/unit evidence from real integration/runtime evidence.

## Convergence

End substantive work as one of:

- A: complete and verified
- B: meaningful verified progress with the next blocker isolated
- C: stop because further work needs unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk

Activity is not progress. Do not keep patching when the work is no longer converging.
