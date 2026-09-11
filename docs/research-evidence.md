# Research Evidence Collection Standard

OpenForge projects should preserve reproducible, privacy-safe engineering evidence during normal development so future empirical analysis, technical reports, and academic papers can be built from historical data rather than reconstructed retrospectively.

## Core evidence

Capture automatically where practical:

- Git history: commits, pull requests, issues, releases, contributors, change size, lead/cycle time.
- Verification: test/lint/build/check counts, pass/fail/skip totals, duration, retries, flaky failures, and the exact revision/environment.
- Deployment/installation: start/end timestamps, total duration, success/failure stage, retries, environment profile, and version.
- Reliability: incident/failure category, detection time, recovery time, rollback/retry outcome, and MTTR-compatible timestamps.
- Runtime: CPU, memory, storage, network, startup/response latency, and workload/environment metadata when relevant.
- Agent-assisted development: agent/tool/model identifier at a non-sensitive product/version level, task type, attempts, success/failure, elapsed time, human interventions, review corrections, CI retries, and final verification result.
- Releases/adoption: release cadence, upgrade/migration results, compatibility checks, and public repository/community signals when useful.

## Recording rules

1. Prefer machine-generated structured records (JSON/JSONL/CSV or CI artifacts) over manually curated claims.
2. Every measurement must be attributable to a timestamp, repository revision, test/workload definition, and enough environment metadata to reproduce or interpret it.
3. Preserve failed attempts and negative results. Do not keep only successful runs.
4. Keep metric definitions stable. When a definition changes, version the schema/metric and document the change.
5. Do not fabricate missing historical values or infer measurements that were not actually observed.
6. Avoid measurement work that materially slows normal development unless the task explicitly requires a benchmark/experiment.
7. Raw high-volume logs may use bounded CI artifact retention; durable aggregate/experiment records should remain reproducible from source or be committed when small and appropriate.

## Public-data safety

Public repositories may publish engineering measurements when they contain no secrets, credentials, tokens, private URLs/IPs, customer/company data, personal data, proprietary datasets, confidential prompts, private source excerpts, or security-sensitive infrastructure details.

Prefer normalized environment labels and aggregate statistics over machine/user identifiers. Before committing generated evidence, redact sensitive fields and review artifacts/logs for accidental disclosure.

## Suggested schema

A minimal record should include:

```text
timestamp, repository, revision, event_type, task_or_test, result,
duration_ms, environment, attempt, human_interventions, metadata
```

Projects may extend this schema for domain-specific measurements. Keep extensions documented and machine-readable.

## Research integrity

Evidence collection is observational by default. A later paper may select a subset and define hypotheses, baselines, experimental controls, exclusion criteria, and statistical analysis separately. Do not optimize or selectively discard development records merely to improve a future result.
