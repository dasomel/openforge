---
name: user-centric-validation
description: Require clean-user, independent-oracle, and failure-path evidence before claiming user-visible correctness for substantive agent-driven changes.
---

# User-Centric Validation

## Intent
Prevent green CI and self-authored tests from being treated as sufficient proof of user-visible correctness.

## Evidence to inspect
- The public user workflow affected by the change.
- Whether expected behavior was derived independently from the implementation.
- Whether local developer state could hide failures.
- Boundary, asymmetric, state-transition, and recovery cases relevant to the change.
- Existing user-reported regressions in the affected area.

## Decision
For substantive user-facing, install, configuration, upgrade, integration, or high-risk changes, require evidence beyond self-authored tests when a clean user journey or independent check is practical.

## Execution
Prefer this sequence:

```text
identify public behavior
  -> derive expected behavior independently
  -> run normal automated checks
  -> exercise a clean/fresh-user journey
  -> challenge likely failure paths
  -> retain regression evidence
```

Use documented/public surfaces such as README, Quick Start, CLI help, public APIs, and UI. Do not rely on hidden developer configuration, cached state, previous installs, or implementation helpers as the expected-value oracle when an independent expectation is practical.

Favor bug-revealing inputs over test volume: asymmetric values, both sides of boundaries, ordering/state transitions, realistic invalid inputs, retries, recovery, and permission differences.

For high-risk changes, prefer fresh-context review or an independent agent/model when available.

## Recovery
If fresh-user automation is impractical, preserve an executable manual reproduction and state the environmental assumptions. If the expected result cannot be independently justified, narrow the completion claim rather than treating passing tests as proof.

## Failure modes
- Declaring success because all self-authored tests pass.
- Reusing the implementation under test to calculate expected results.
- Running only in a developer environment with stale or hidden state.
- Increasing test count without targeting likely failure modes.
- Converting a cross-system user bug into only a narrow unit test.
- Calling a smoke test, random-byte loop, or superficial UI assertion sufficient user validation.
