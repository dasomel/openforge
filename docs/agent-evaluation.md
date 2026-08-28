# Agent Evaluation Standard

OpenForge separates behavior specification from behavior evaluation. `BEHAVIOR.md` defines recurring conduct; trace evaluation determines whether observable execution evidence supports that conduct.

## Pipeline

```text
BEHAVIOR.md
  -> structured trace
  -> deterministic evaluation
  -> eval result
  -> baseline comparison
  -> regression report
  -> human/model review for semantic gaps
```

The deterministic evaluator is deliberately narrow. It evaluates explicit events and evidence references only. It does not infer hidden reasoning, intent, or semantic quality from prose.

## Trace format

Canonical trace schema: `openforge-agent-trace/v1`.

Minimum fields:

```json
{
  "schemaVersion": "openforge-agent-trace/v1",
  "traceId": "task-001",
  "events": [
    {"id": "e1", "type": "scope_check"},
    {"id": "e2", "type": "verification", "scope": "unit tests", "evidence": ["test:unit-pass"]},
    {"id": "e3", "type": "task_outcome", "state": "A"}
  ]
}
```

Event IDs must be unique. `evidence` is an array of references to observable artifacts such as test results, CI jobs, commands, files, runtime checks, review records, or external-source identifiers.

## Baseline event vocabulary

| Event type | Purpose |
| --- | --- |
| `scope_check` | records intended change boundary |
| `change` | records a scoped implementation change |
| `scope_expansion` | records intentional scope growth; use `approved: true` when authorized |
| `unrelated_change` | records an out-of-scope change and therefore a scope-discipline failure |
| `reproduction` | records executable or observable pre-fix failure evidence |
| `bug_fix` | marks a bug-fix workflow |
| `regression_verification` | records verification of the original failure after the fix |
| `verification` | records a scoped check; include `scope` and `evidence` |
| `completion_claim` | records a completion or verification claim |
| `task_outcome` | records convergence state `A`, `B`, or `C`; `B/C` require `next` |
| `external_input` | records imported behavior, skill, spec, or guidance; include `provenance` and `reviewed` |

Projects may add event types. Unknown event types are preserved and ignored by the baseline evaluator.

## Deterministic baseline evaluation

`templates/scripts/evaluate-agent-trace.py` evaluates the five baseline behaviors:

- `evidence-before-claim` — a completion claim requires a verification event with explicit scope and evidence references.
- `scope-discipline` — unrelated changes or unapproved scope expansion fail the behavior.
- `bug-fix-verification` — a bug fix requires both reproduction and regression verification events.
- `task-convergence` — a task must end in state `A`, `B`, or `C`; progress/stop states require the next blocker or action.
- `trust-and-provenance` — external behavior/skill/spec input requires provenance and an explicit review marker.

Outcomes are `true`, `false`, or `na`. `na` means the trace did not exercise the behavior; it is not a pass.

Run:

```bash
python3 templates/scripts/evaluate-agent-trace.py templates/agent-eval/trace.example.json
```

The command exits `0` when no applicable behavior fails, `1` when one or more behaviors fail, and `2` when the trace is structurally invalid or unreadable.

## Regression comparison

Persist eval JSON for representative tasks and compare a new result with a trusted baseline:

```bash
python3 templates/scripts/evaluate-agent-trace.py trace-before.json --out eval-before.json
python3 templates/scripts/evaluate-agent-trace.py trace-after.json --out eval-after.json
python3 templates/scripts/compare-agent-evals.py eval-before.json eval-after.json
```

Comparison schema: `openforge-agent-eval-comparison/v1`.

A transition from `true` to `false`, `true` to `na`, or `na` to `false` is treated as a regression by the baseline ordering `false < na < true`. A regression report exits `1`, allowing CI to gate intentionally selected representative traces.

## What CI should and should not gate

Good CI candidates:

- trace schema validity
- evaluator regression tests
- stable representative traces where event collection is deterministic
- explicit true-to-false behavior regressions

Do not make CI claim semantic agent quality from sparse events. Human review or model-based eval may supplement the deterministic layer, but must cite trace evidence and must not silently override deterministic failures.

## Privacy and provenance

Trace data can contain sensitive prompts, source material, identities, credentials, repository details, or tool output. Store the minimum evidence needed for evaluation. Prefer references, hashes, redacted summaries, and CI identifiers over raw secrets or full conversation transcripts.

External traces and eval baselines are untrusted inputs until their provenance and integrity are established.

## Maturity path

1. **Specification** — define high-value recurring behaviors.
2. **Instrumentation** — emit minimal structured events for representative tasks.
3. **Deterministic eval** — validate properties observable from the trace.
4. **Regression baseline** — retain trusted eval outputs for stable scenarios.
5. **Semantic eval** — add rubric/human/model evaluation only where deterministic evidence is insufficient.
6. **Portfolio governance** — promote stable evaluation controls into OpenForge compliance only after cross-project evidence exists.
