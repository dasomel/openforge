# Experimental Agent Harness Evaluation Profile

[한국어](agent-harness-evaluation-ko.md)

> Status: **Experimental and non-normative.** This profile supports controlled pilots. It does not select or recommend a default harness, model, provider, or subscription.

The same model can behave differently when a coding harness changes its initial instructions, tool schemas, context management, retry behavior, or execution loop. Correctness alone can hide those differences. OpenForge therefore provides a separate experiment dataset for comparing correctness, efficiency, reliability, and safety under a controlled cohort.

This profile complements the [Agent Evaluation Standard](agent-evaluation.md). Behavior traces answer whether observable conduct satisfied a contract. Harness datasets answer how much context, tool activity, time, intervention, and estimated API cost were used. A run may reference its behavior trace through `traceId`, but the two schemas remain independent.

## Artifacts

- Dataset schema: [`schemas/agent-harness-dataset-v1.schema.json`](../schemas/agent-harness-dataset-v1.schema.json)
- Neutral example: [`templates/agent-eval/harness-dataset.example.json`](../templates/agent-eval/harness-dataset.example.json)
- Comparison CLI: [`templates/scripts/compare-agent-harness-runs.py`](../templates/scripts/compare-agent-harness-runs.py)

The dataset schema is `openforge-agent-harness-dataset/v1`. Comparison output is `openforge-agent-harness-comparison/v1`.

## Controlled cohort

Only aggregate runs when all of these fields are identical:

| Control | Why it is fixed |
|---|---|
| Task ID and task class | Prevents a simpler workload from appearing more efficient |
| Repository and immutable revision | Prevents codebase drift |
| Provider, model, version, and reasoning effort | Isolates the harness rather than a model change |
| Operating system and network access | Controls environmental capability and latency |
| Tool profile and maximum turns | Controls available actions and execution budget |

Harness name, version, and configuration are the intended independent variables. If another controlled field changes, create a new cohort. The comparison CLI fails closed when multiple input datasets have different cohort objects.

## Pilot protocol

1. Define the task, executable success criteria, evaluator, safety checks, and turn budget before running any harness.
2. Use a fresh checkout of the same immutable revision for every attempt. Hold model settings, network access, credentials, tool availability, and evaluator constant.
3. Use at least three independent attempts per harness for an exploratory pilot. More attempts are necessary for high-variance tasks or decision-grade claims.
4. Interleave or randomize harness order when shared caches, service load, or evaluator drift could bias results.
5. Preserve failed, partial, timed-out, and intervention-heavy attempts. Do not rerun selectively until the preferred harness succeeds.
6. Record unavailable telemetry as `null` and explain important gaps in `measurementNotes`. Never reconstruct unobserved token, duration, or intervention values.
7. Compare trade-offs inside one cohort. Do not combine success rates or cost ratios across different tasks as if they were one controlled experiment.

Use a workload set that represents the intended operating environment:

- `simple` — bounded documentation or local code edit
- `bug-fix` — reproduce, fix, and verify a defect
- `cross-component` — coordinated changes across interfaces or packages
- `runtime-ops` — deployment, Kubernetes, or live-environment verification
- `multi-session` — interrupted or compacted work that must resume correctly

A short benchmark with a small task count does not establish production reliability, long-running context behavior, or cross-project generality. Treat those as separate hypotheses and cohorts.

## Measures and interpretation

| Axis | Measures |
|---|---|
| Correctness | success rate and optional evaluator score |
| Efficiency | input/cached/output/reasoning tokens, initial context, instruction characters, tool-schema bytes, turns, tool calls, elapsed time, estimated API cost |
| Reliability | failed tool calls and rate, human interventions, context compactions |
| Safety | observed safety pass rate, preferably backed by a referenced behavior trace or explicit evaluator evidence |

Every nullable aggregate includes `observedRuns` and `totalRuns`. Zero coverage produces a `null` mean; the CLI does not impute a value. The tool-failure rate uses total failed calls divided by total tool calls only where both counters were observed.

`estimatedApiCostUsd` is an API list-price estimate tied to `pricingDate`. Keep its calculation method stable within a cohort. Subscription fees, bundled quotas, enterprise discounts, engineering labor, and wall-clock opportunity cost are different measures; do not convert them into an API estimate or claim they are equivalent. Record them separately in experiment notes when relevant.

The report deliberately emits `winnerSelected: false`. A lower token or dollar mean does not override failed correctness or safety, and a higher success rate may not justify operational complexity. Maintainers interpret the dimensions against the task's risk and constraints.

## Run the comparison

One dataset may contain all harness runs:

```bash
python3 templates/scripts/compare-agent-harness-runs.py \
  templates/agent-eval/harness-dataset.example.json
```

Separate files are also supported when they describe the exact same cohort:

```bash
python3 templates/scripts/compare-agent-harness-runs.py \
  results/harness-a.json results/harness-b.json \
  --out results/comparison.json
```

The command exits `0` after a valid comparison and `2` for unreadable, structurally invalid, semantically invalid, duplicate, or mixed-cohort input. It never exits with a regression or winner judgment.

## CI, privacy, and promotion

CI may validate the schema, semantic invariants, and deterministic summarizer. Do not gate a repository on a universal harness ranking or a sparse cost delta. A project may define a task-specific gate only after it records the rationale, stable evaluator, sample size, and acceptable trade-offs.

Harness datasets are public evidence when committed. Do not store raw prompts, credentials, private repository content, personal data, or unrestricted tool output. Prefer trace IDs, hashes, redacted notes, and aggregate counters. Follow the [Research Evidence Collection Standard](research-evidence.md).

Promotion from experimental guidance to an OpenForge default requires repeatable evidence across multiple task classes and projects, a review of failures and missing telemetry, and a separate decision review. Until then, no harness-specific result changes normative agent instructions.
