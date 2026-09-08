# Agent Outcome / Evidence Consistency

OpenForge operational traces distinguish historical compatibility from strict completion semantics.

## Modes

- `legacy` (or omitted): preserves previously collected traces.
- `strict`: required for traces that cover current high-risk changes.

## Strict completion contract

A strict trace may report convergence state `A` only when:

1. a `completion_claim` exists;
2. at least one scoped verification event has typed evidence;
3. relevant verification has an explicit passing status such as `passed`, `success`, `ok`, or `verified`;
4. no relevant verification is failed, pending, unknown, skipped, unverified, or missing a status.

If those conditions are not met, `task-convergence` evaluates to `false`. A completion claim with failed or non-passed verification also evaluates `evidence-before-claim` to `false`.

For a strict bug fix, `regression_verification` must also be explicitly passed. Merely recording that a regression check exists is not sufficient.

## B / C convergence

States `B` and `C` remain valid when they identify the next blocker or action. In strict mode they must not coexist with a completion claim, because progress/stop and completion are contradictory outcomes.

## Verification status

Verification events should use a structured `status` field instead of encoding status only in prose.

```json
{
  "type": "verification",
  "status": "passed",
  "scope": "release workflow and immutable inputs",
  "evidence": ["ci:agent-behavior"]
}
```

## High-risk enforcement

The trace/change evidence correlation gate requires current high-risk traces to set `consistencyMode: strict` and include at least one explicitly passed verification event. Unrelated historical traces remain `not-applicable` and do not require migration.

This keeps old evidence readable while preventing new high-risk work from claiming completion against pending or failed checks.

## Regression semantics

Because strict inconsistency is mapped into the existing five Behavior results, the existing trusted-baseline comparator detects it without a new scoring system. For example, a previously valid `evidence-before-claim: true` or `task-convergence: true` becomes `false` when completion is asserted against failed/pending verification.

This is intentionally stronger than checking for trace-file presence: the claimed outcome and the recorded evidence must agree.
