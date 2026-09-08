# Agent Trace Evidence Correlation

Operational traces are useful only when they are connected to the change they claim to verify. OpenForge therefore treats trace presence, change coverage, evidence quality, and behavior regression as separate gates.

## Contract

For a pull request classified as high risk:

1. a trace must be added or modified in the same diff;
2. at least one relevant trace must declare `changeContext.paths` that covers every high-risk changed path;
3. relevant traces must include `verification` or `regression_verification` events;
4. at least one verification event must declare a non-empty `scope`;
5. verification must reference typed evidence using one of `test:`, `ci:`, `runtime:`, `artifact:`, or `policy:`;
6. the trace is then evaluated against the trusted behavior baseline.

A historical trace that does not cover any current high-risk path is `not-applicable` and is not forced to migrate to the newest operational fields. This prevents a new governance rule from invalidating unrelated historical evidence while keeping the current change strict.

## Example

```json
{
  "schemaVersion": "openforge-agent-trace/v1",
  "traceId": "change-001",
  "task": "Harden release workflow",
  "changeContext": {
    "paths": [
      ".github/workflows/**",
      "scripts/ci/**"
    ]
  },
  "events": [
    {
      "id": "e4",
      "type": "regression_verification",
      "scope": "release workflow and governance checks",
      "evidence": ["ci:release-pass", "test:guard-regression"]
    }
  ]
}
```

## Why path correlation is required

A repository-level trace can otherwise become a ceremonial artifact: a maintainer can add a generic trace while changing an unrelated privileged or release-critical file. `changeContext.paths` makes the claimed scope machine-checkable against the actual PR diff.

The patterns should be narrow enough to communicate the affected boundary. They may use globs when a change genuinely spans a coherent subsystem, but broad patterns must not be used merely to silence the gate.

## Evidence classes

Typed evidence identifiers are intentionally lightweight. They identify the class and stable human-readable reference without embedding logs, secrets, customer data, or hidden reasoning.

- `test:` — deterministic test or regression suite
- `ci:` — CI workflow/job/step result
- `runtime:` — explicit runtime or environment validation
- `artifact:` — digest, manifest, generated report, or immutable evidence artifact
- `policy:` — deterministic policy finding or policy decision

A path string by itself is not verification evidence. Source files can explain what changed, but they do not prove that the changed behavior works.

## Historical traces

Only traces that cover at least one current high-risk path are evaluated by the evidence-quality gate. Unrelated historical traces are reported as `not-applicable`.

This behavior was added after the first downstream rollout exposed that an older `pilot-001` trace, unrelated to the current maintenance change, was being rejected for lacking the newer `changeContext` field. The gate was narrowed to current-change relevance and reverified in OpenForge, Narwhal, KubeMetal, and nfs-quota-agent.

## CI sequence

```text
PR diff
  -> risk classification
  -> same-diff trace requirement
  -> trace/change evidence correlation
  -> behavior baseline regression gate
  -> repository-specific tests/runtime evidence
```

Each stage answers a different question. Passing the Agent Behavior workflow must not be reported as proof that unrelated repository CI or runtime validation passed.

## AGENT-005

This contract strengthens operational evidence but does not by itself justify a new portfolio compliance metric. OpenForge still requires naturally occurring behavior-regression evidence before deciding whether an `AGENT-005` metric should be promoted.
