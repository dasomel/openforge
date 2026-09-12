# Research Evidence Collection Standard

OpenForge projects should preserve reproducible engineering evidence during normal development so future empirical analysis, technical reports, and academic papers can be built from historical data rather than reconstructed retrospectively.

## Core evidence

Capture automatically where practical:

- Git history: commits, pull requests, issues, releases, contributors, change size, lead/cycle time.
- Verification: test/lint/build/check counts, pass/fail/skip totals, duration, retries, flaky failures, and the exact revision/environment.
- Deployment/installation: start/end timestamps, total duration, success/failure stage, retries, environment profile, and version.
- Reliability: incident/failure category, detection time, recovery time, rollback/retry outcome, and MTTR-compatible timestamps.
- Runtime: CPU, memory, storage, network, startup/response latency, and workload/environment metadata when relevant.
- Agent-assisted development: agent/tool/model identifier at a product/version level, task type, attempts, success/failure, elapsed time, human interventions, review corrections, CI retries, and final verification result.
- Releases/adoption: release cadence, upgrade/migration results, compatibility checks, and public repository/community signals when useful.

## Prospective + legacy evidence workflow

Evidence collection is not limited to newly generated records. Every normal implementation, bug-fix, verification, release, experiment, and documentation task should use a two-track workflow:

1. **New evidence:** capture new measurements/results produced by the current task when practical.
2. **Legacy evidence on discovery:** when the task encounters an existing QA report, test output, benchmark, trace, CI result, lessons log, compatibility matrix, dated implementation report, issue/PR evidence, or historical measurement, preserve the original and register/classify it for future analysis.

The portfolio-level legacy evidence catalog is tracked by `dasomel/openforge#89`. A legacy catalog entry should identify the repository and source/path, evidence date when known, evidence class, evidence strength (`measured`, `observed`, `derived`, or `contextual`), environment scope, useful metrics/facts, limitations, likely paper use, and public-data review state.

Do not rewrite a historical artifact simply to conform to the current schema. The original format remains evidence; the catalog provides the normalization/mapping layer. Never backfill duration, resource use, agent intervention, token use, or any other value that was not actually recorded. Preserve failures, partial/skipped outcomes, superseded versions, and obsolete results when they retain longitudinal value.

## Recording rules

1. Prefer machine-generated structured records (JSON/JSONL/CSV or CI artifacts) over manually curated claims.
2. Every new measurement must be attributable to a timestamp, repository revision, test/workload definition, schema version, and enough environment metadata to interpret it.
3. Preserve failed attempts and negative results. Do not keep only successful runs.
4. Keep metric definitions stable. When a definition changes, bump the schema/metric version and document the change.
5. Do not fabricate missing historical values or infer measurements that were not actually observed.
6. Avoid measurement work that materially slows normal development unless the task explicitly requires a benchmark/experiment.
7. Raw high-volume logs may use bounded CI artifact retention; durable aggregate/experiment records should remain reproducible from source or be committed when small and appropriate.
8. Prefer append-only JSONL for longitudinal records. Never rewrite old evidence merely to improve later results; corrections should be new linked records when practical.

## Public-data safety

The current portfolio is primarily personal/home OSS and test environments. Reproducibility-relevant technical identifiers intentionally used by the public project may be retained, including RFC1918 test addresses, `*.local.*` domains, synthetic/local hostnames, pod/node/namespace/service names, local test topology, component versions, and hardware/runtime specifications. These are not automatically sensitive merely because they look internal.

Evidence intended for public storage MUST NOT contain actual secrets or credentials such as passwords, API/PAT/OAuth tokens, cookies/session secrets, private keys, authorization headers, signed credentials, secret-bearing kubeconfig data, or accidental personal data. If evidence is ever sourced from an employer, customer, partner, or otherwise non-public third-party environment, perform a separate review before publication and exclude non-public organizational or security-sensitive information.

Use structured fields rather than uncontrolled raw dumps. Raw logs can be retained when useful and demonstrably safe, but secret scanning should precede publication.

### Public evidence gate

Before committing or uploading structured evidence publicly:

1. Validate it against the versioned evidence schema when the artifact uses the canonical schema.
2. Run secret/pattern checks for credentials, keys, tokens, cookies, personal data, and other genuinely sensitive values.
3. Review free-form fields so `metadata` does not become an unrestricted log sink.
4. For third-party/non-public environment evidence, perform an additional environment-specific disclosure review.
5. If an artifact cannot be safely reviewed, retain a safe summary/measurement rather than publishing secret-bearing raw content.

## Canonical schema

The canonical prospective public record is JSON/JSONL and starts with these fields:

```text
schema_version, timestamp, repository, revision, event_type, task_or_test,
result, duration_ms, environment, attempt, human_interventions,
review_corrections, ci_retries, metadata
```

Required characteristics:

- `schema_version`: explicit semantic/schema version, beginning with `1.0`.
- `timestamp`: UTC ISO-8601.
- `repository`: public repository slug only.
- `revision`: immutable git commit SHA when available.
- `event_type`: controlled category such as `build`, `test`, `install`, `deploy`, `runtime`, `recovery`, `agent_task`, `release`, or `benchmark`.
- `result`: controlled value such as `pass`, `fail`, `partial`, `cancelled`, or `skipped`.
- `duration_ms`: measured wall-clock duration, never estimated.
- `environment`: interpretable environment label.
- `attempt`, `human_interventions`, `review_corrections`, `ci_retries`: non-negative measured counters when applicable.
- `metadata`: documented project-specific allowlisted scalar/object values only; no credentials or arbitrary secret-bearing environment dumps.

Projects may extend the schema for domain-specific measurements, but extensions must be documented, machine-readable, reviewed, and backward compatible within a schema version.

## Recommended repository layout

```text
research/
  README.md                 # metric definitions, legacy workflow, environment notes
  evidence/
    YYYY-MM.jsonl           # durable prospective longitudinal records
  experiments/
    <experiment-id>/        # explicit benchmarks with protocol + summarized results
```

Legacy evidence may remain in its historical location and format. Reference it from the catalog rather than moving or rewriting it solely for research organization.

## Research integrity

Evidence collection is observational by default. A later paper may select a subset and define hypotheses, baselines, experimental controls, exclusion criteria, and statistical analysis separately. Do not optimize or selectively discard development records merely to improve a future result. Preserve schema versions, source references, limitations, failures, and exclusion reasons so future analysis can distinguish unavailable data from intentionally excluded data.