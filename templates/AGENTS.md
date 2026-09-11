# AGENTS.md

Inspect repository guidance and documentation relevant to the current task before editing. Load detailed references only when they are needed.

## Work contract

- Make the smallest coherent change that solves the requested problem.
- Do not modify unrelated code. Report unrelated findings instead.
- Preserve architecture/layer boundaries and existing access restrictions.
- Treat public/internal visibility, exported APIs, permissions, RBAC, and destructive behavior as design changes.
- Follow existing naming/style conventions; let formatter/linter rules own deterministic style.
- Keep generic engineering rules model-agnostic. Tool/model-specific instruction files should be thin adapters rather than policy forks.
- Preserve reproducible, privacy-safe engineering evidence during normal development. Capture machine-readable test/build/deploy/runtime/reliability and agent-assistance measurements when practical, including failures and human interventions; follow the OpenForge Research Evidence Collection Standard.

## Autonomy boundary

Safe local and reversible work already within the requested scope may proceed without repeated approval, including relevant inspection, editing, build/lint/test execution, fixing failures caused by the change, and re-running verification.

Require explicit authorization unless already granted for production/shared-environment mutation, destructive or irreversible external actions, credential/permission changes beyond the requested design, release/publish actions, paid-resource changes, or unrelated repository/external-system mutations.

## Documentation impact

For substantive changes, review documentation relevant to the changed behavior. Do not require unrelated documentation to be read or updated.

- Do not describe planned/experimental behavior as implemented.
- Prefer generated/canonical sources for repeated numeric or version claims.
- If relevant documentation cannot safely be updated in the same change, identify the tracked follow-up rather than silently leaving known drift.

## Bugs

When feasible: reproduce -> failing regression test/evidence -> fix -> same evidence passes -> relevant regression suite.

If automated regression is impractical, record executable reproduction evidence and why automation is not feasible.

## Verification

Perform verification appropriate to the change's risk and user impact. Do not run broad suites by habit when narrower evidence is sufficient, and do not claim completion without stating what was actually run.

For user-facing, installation, configuration, upgrade, integration, or high-risk changes, apply the relevant portions of the OpenForge User-Centric Validation Standard:
https://github.com/dasomel/openforge/blob/main/docs/user-centric-validation.md

A green CI run or self-authored test suite is necessary evidence but is not sufficient proof of user-visible correctness when the changed behavior depends on a real user journey or runtime integration.

For agent instruction design and maintenance, follow:
https://github.com/dasomel/openforge/blob/main/docs/model-agnostic-agent-instructions.md

For durable development/research measurements, follow:
https://github.com/dasomel/openforge/blob/main/docs/research-evidence.md

## Convergence

End substantive work as one of:

- A: complete and verified
- B: meaningful verified progress with the next blocker isolated
- C: stop because further work needs unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk

Activity is not progress. Continue through implementation, relevant verification, and fixes caused by the change until one of these states is reached.
