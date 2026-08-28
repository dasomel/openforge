# Agent Evaluation Operations

This document defines how OpenForge Agent Behavior traces move from examples into day-to-day engineering without turning every change into mandatory logging.

## Operational model

```text
selected agent-heavy or high-risk task
  -> record structured events incrementally
  -> commit trace under .agents/evals/traces/
  -> deterministic evaluation
  -> compare with trusted baseline
  -> fail only on behavior regression
```

The operational profile is opt-in per task. Ordinary low-risk changes do not need a trace merely to satisfy process.

## When to record a trace

Prefer a trace when at least one condition applies:

- an AI agent performs a multi-step bug fix, migration, release, or incident task
- runtime evidence is materially different from unit or mocked evidence
- the change touches permissions, credentials, privileged host access, GitOps ownership, destructive operations, or another design-level boundary
- a previous agent failure is being reproduced or guarded against
- a behavior regression would be costly to diagnose after merge

Do not record hidden reasoning, chain-of-thought, credentials, customer data, tokens, raw secrets, or unnecessary prompt content.

## Recording events

Use `record-agent-event.py` (or the repository-local `record.py`) to append only observable events. Evidence entries should be references such as test names, CI checks, sanitized logs, issue/PR references, or runtime verification identifiers.

A minimal bug-fix trace usually records:

1. `scope_check`
2. `reproduction`
3. `bug_fix`
4. `regression_verification`
5. `verification`
6. `completion_claim`
7. `task_outcome`

Additional `external_input`, `scope_expansion`, or recovery events should be added only when they actually occurred.

## Trusted baseline policy

A baseline eval is a reviewed expectation, not an automatically refreshed snapshot.

Baseline changes require a deliberate engineering reason, for example:

- a behavior specification intentionally changed
- a behavior became newly applicable or no longer applicable
- representative evidence improved and the stronger expectation should become permanent
- a false-positive pattern was demonstrated with review evidence

Never update the baseline merely to make a failing regression gate green.

## CI gate policy

The regression gate compares outcomes using:

```text
false < na < true
```

Downward transitions are regressions. In particular, `true -> false`, `true -> na`, and `na -> false` fail the gate.

A current trace may contain an absolute failed behavior without failing the regression gate if the trusted baseline already records the same known limitation. This keeps the gate focused on degradation while the underlying eval output still exposes the unresolved weakness.

## Repository adoption profile

The first operational pilot uses three repositories:

- Narwhal: Kubernetes/GitOps/RBAC and cluster-runtime evidence
- KubeMetal: macOS/Tauri/MLX/native capability evidence
- nfs-quota-agent: quota/filesystem/privileged-host evidence

Each repository keeps the same portable behavior names and canonical trace/eval schema while retaining project-specific evidence boundaries.

## Promotion criteria for AGENT-005

Do not create a portfolio-wide trace/eval compliance metric from file presence alone. Consider `AGENT-005` only after longitudinal operational evidence shows that:

- real engineering tasks produce useful traces without excessive ceremony
- at least one genuine behavior regression is caught before merge
- false-positive and maintenance costs are acceptable
- privacy/provenance rules hold across repositories
- baseline updates remain deliberate rather than rubber-stamped
- project-specific evidence classes do not fragment the portable behavior vocabulary
