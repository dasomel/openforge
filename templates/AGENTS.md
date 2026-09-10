# AGENTS.md

Read the repository's README, CONTRIBUTING, DESIGN/architecture docs, and project-specific instruction files before editing.

## Work contract

- Make the smallest coherent change that solves the requested problem.
- Do not modify unrelated code. Report unrelated findings instead.
- Preserve architecture/layer boundaries and existing access restrictions.
- Treat public/internal visibility, exported APIs, permissions, RBAC, and destructive behavior as design changes.
- Follow existing naming/style conventions; let formatter/linter rules own deterministic style.
- Comments explain why, invariants, hazards, or non-obvious constraints; do not narrate obvious code.

## Documentation impact

For substantive changes, explicitly review whether README, architecture, operations, security, API/configuration, supported-version, or user-facing documentation must change in the same work unit.

- Do not describe planned/experimental behavior as implemented.
- Prefer generated/canonical sources for repeated numeric or version claims.
- If documentation cannot safely be updated in the same change, identify the tracked follow-up rather than silently leaving known drift.
- Review whether the change is also a blog/portfolio update candidate when it adds a user capability, architecture/operations lesson, platform support, or material security improvement.

## Bugs

When feasible: reproduce -> failing regression test/evidence -> fix -> same test passes -> relevant regression suite.

If an automated regression test is impractical, record executable reproduction evidence and why automation is not feasible.

## Verification

Do not claim completion without relevant verification. State what was actually run and distinguish mocked/unit evidence from real integration/runtime evidence.

For user-facing, installation, configuration, upgrade, integration, or high-risk changes, also follow the OpenForge User-Centric Validation Standard:
https://github.com/dasomel/openforge/blob/main/docs/user-centric-validation.md

A green CI run or self-authored test suite is necessary evidence but is not sufficient proof of user-visible correctness. Exercise the relevant public user journey from a clean environment where practical, derive expected behavior independently from the implementation, challenge likely failure paths, and convert confirmed user-visible defects into regression evidence.

## Convergence

End substantive work as one of:

- A: complete and verified
- B: meaningful verified progress with the next blocker isolated
- C: stop because further work needs unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk

Activity is not progress. Do not keep patching when the work is no longer converging.
