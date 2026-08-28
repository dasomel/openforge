---
name: evidence-before-claim
description: Require explicit, scoped evidence before an agent claims a task is complete or a property is verified.
---

# Evidence Before Claim

## Intent
Prevent completion language from outrunning the evidence actually produced during the task.

## Evidence to inspect
- Tests, builds, static checks, policy checks, or runtime verification actually executed.
- Scope of each check and the environment where it ran.
- Known gaps between mocked, integration, and real-runtime evidence.

## Decision
Before making a completion or verification claim, decide whether the available evidence directly supports that claim at the required level.

## Execution
- State the checks that actually ran.
- Qualify the claim to match the evidence class.
- Distinguish unit/stub, integration, static, build/package, security/policy, and real-runtime verification.
- Prefer a narrower accurate claim over a broad unsupported one.

## Recovery
If evidence is insufficient, run the smallest appropriate verification that can close the gap. If that is unavailable or unjustified, report the gap explicitly and use a progress or stop outcome instead of claiming completion.

## Failure modes
- Saying "done" because code was edited successfully.
- Treating a lint or unit-test pass as proof of runtime behavior.
- Omitting failed or unexecuted checks that materially limit confidence.
- Inferring production safety from a mocked or partial environment.
