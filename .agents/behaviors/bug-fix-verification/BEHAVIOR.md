---
name: bug-fix-verification
description: Require reproducible evidence of a defect, a minimal fix, and regression verification for agent-driven bug fixes.
---

# Bug Fix Verification

## Intent
Ensure bug fixes address an observed defect rather than merely matching an assumed implementation.

## Evidence to inspect
- A user-visible or system-visible reproduction.
- A failing regression test or equivalent executable evidence.
- The same evidence after the change.
- Relevant regression-suite results.

## Decision
Confirm that the proposed test or reproduction demonstrates the defect itself rather than encoding the intended implementation.

## Execution
Use the preferred sequence:

```text
reproduce
  -> failing regression test or executable evidence
  -> minimal fix
  -> same test/evidence passes
  -> relevant regression suite
```

If deterministic automation is impractical, keep the reproduction executable and document why automation is not feasible.

## Recovery
If the issue cannot be reproduced, do not guess at a fix. Narrow the environment, inputs, logs, or assumptions until the failure is isolated, or stop with the missing evidence stated clearly.

## Failure modes
- Writing a test that passes only because it mirrors the proposed implementation.
- Fixing from symptoms without reproducing the defect.
- Skipping post-fix regression checks.
- Claiming a root cause that has not been isolated.
