# User-Centric Validation Standard

OpenForge treats automated tests and green CI as necessary evidence, not sufficient proof of user-visible correctness.

This standard is intended for AI-assisted and agent-driven OSS development where implementation speed can exceed the quality of real-user verification.

## Principle

Do not ask only whether the implementation passes its tests. Ask whether a new user can exercise the intended behavior from the documented public interface and obtain independently justified results.

The target failure pattern is:

```text
implementation
  -> self-authored tests
  -> CI green
  -> real user
  -> failure
```

The preferred validation flow is:

```text
implementation
  -> independent expected behavior
  -> normal automated tests
  -> clean user journey
  -> adversarial/failure-path checks
  -> regression evidence
  -> completion
```

## Validation gates

Projects SHOULD map their verification to the following gates. A project may combine gates when appropriate, but should not silently omit user-visible validation for user-facing changes.

| Gate | Purpose | Typical evidence |
| --- | --- | --- |
| G0 Build | Artifact can be produced | build/package output |
| G1 Static / Lint | Deterministic structural checks | lint, format, type/static analysis |
| G2 Unit | Local logic behaves as specified | focused unit tests |
| G3 Integration | Components interact correctly | service/component integration tests |
| G4 E2E | System behavior works across boundaries | end-to-end automated tests |
| G5 Fresh User | Documented workflow works without developer state | clean checkout/config/runtime journey |
| G6 Adversarial | High-risk assumptions and failure paths are challenged | boundary, asymmetric, invalid, retry/recovery cases |
| G7 Upgrade / Regression | Previously supported behavior remains valid | upgrade tests and user-visible regressions |

Green CI is not a substitute for G5-G7 when those gates are relevant to the change.

## Fresh-user validation

For installation, configuration, onboarding, CLI, UI, API, authentication, storage, networking, packaging, or upgrade changes, validate from an environment that does not depend on the developer's existing state.

Use only documented/public surfaces where practical:

- README and Quick Start
- published install/upgrade documentation
- CLI `--help`
- public API contracts
- user-visible UI

A fresh-user run SHOULD avoid relying on undeclared local state such as:

- cached images or build artifacts
- existing namespaces, CRDs, releases, databases, or schemas
- pre-existing kubeconfig/context state
- hidden environment variables or local config files
- developer credentials not described in the user workflow
- stale ports, processes, volumes, or previous-install residue

If clean automation is too expensive or impractical, retain an executable reproduction checklist and record the environmental assumptions explicitly.

## Independent expected behavior

Tests SHOULD avoid using the same implementation path as the oracle when an independent expectation can be derived.

Prefer:

- expected values derived from the public contract or specification
- a second implementation or external reference when appropriate
- fresh-context review for high-risk behavior
- a different model/agent for independent review when agent-driven development is used

Avoid calculating the expected result with the implementation helper that is being tested unless the test is explicitly scoped to a different invariant.

## Inputs that reveal bugs

Do not optimize for test count. Prefer inputs that distinguish correct from subtly incorrect implementations.

For non-trivial behavior, consider:

- asymmetric inputs instead of repeated identical values
- both sides of boundaries
- state transitions and ordering changes
- invalid and partially valid inputs
- retry, timeout, cancellation, rollback, and recovery paths
- realistic structured inputs rather than undirected random bytes
- multiple independent user roles or permission levels when access control is involved

## User-reported defects

A confirmed user-visible bug SHOULD produce durable regression evidence.

Preferred sequence:

```text
user-visible reproduction
  -> failing regression evidence
  -> minimal fix
  -> same evidence passes
  -> relevant regression suite
```

A narrow unit test may complement this evidence but should not replace the user-visible reproduction when the failure crossed installation, configuration, integration, or workflow boundaries.

This complements `.agents/behaviors/bug-fix-verification/BEHAVIOR.md`.

## Completion evidence

For substantive work, completion notes SHOULD state:

1. which validation gates were relevant;
2. which checks actually ran;
3. whether a clean/fresh-user environment was used;
4. the user journey exercised;
5. any relevant gates not run and why.

Do not claim user-visible correctness solely because self-authored tests passed.

## Downstream adoption

Downstream OSS repositories can adopt this standard without copying the entire policy.

Recommended `AGENTS.md` reference:

```markdown
## User-centric validation

For user-facing, installation, configuration, upgrade, or high-risk changes, follow the OpenForge User-Centric Validation Standard:
https://github.com/dasomel/openforge/blob/main/docs/user-centric-validation.md

A green CI run is necessary but is not sufficient completion evidence. Exercise the relevant public user journey from a clean environment where practical, and convert confirmed user-visible defects into regression evidence.
```

Projects may additionally vendor `.agents/behaviors/user-centric-validation/BEHAVIOR.md` when their agent harness supports behavior specifications.

## Scope

This standard does not mandate a specific testing framework, TDD process, fuzzing library, formal method, model provider, or agent harness. Those are implementation choices. The invariant is evidence that meaningfully challenges user-visible behavior rather than mechanically satisfying a named testing technique.
