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
2. Every measurement must be attributable to a timestamp, repository revision, test/workload definition, schema version, and enough normalized environment metadata to interpret it.
3. Preserve failed attempts and negative results. Do not keep only successful runs.
4. Keep metric definitions stable. When a definition changes, bump the schema/metric version and document the change.
5. Do not fabricate missing historical values or infer measurements that were not actually observed.
6. Avoid measurement work that materially slows normal development unless the task explicitly requires a benchmark/experiment.
7. Raw high-volume logs may use bounded CI artifact retention; durable aggregate/experiment records should remain reproducible from source or be committed when small and appropriate.
8. Prefer append-only JSONL for longitudinal records. Never rewrite old evidence merely to improve later results; corrections should be new records linked to the superseded record when practical.

## Public-data safety

Public repositories may publish engineering measurements only after they pass a public-data review. Evidence intended for public storage MUST NOT contain:

- secrets, credentials, tokens, cookies, API keys, private keys, authorization headers, or signed URLs;
- private/internal URLs, routable or private IP addresses, hostnames, VPN/bastion details, account IDs, cloud resource IDs, cluster/node names tied to a real environment, or filesystem paths containing user names;
- customer, employer, partner, tenant, or other company-identifying data unless it is already intentionally public and relevant;
- personal data, email addresses, usernames tied to a person, directory contents, user-provided payloads, or sensitive media;
- proprietary datasets, confidential prompts, private source excerpts, unpublished product details, or non-public issue content;
- security-sensitive infrastructure details such as firewall rules for real environments, topology that materially aids targeting, credential scope, exploit traces, or raw security scanner output that exposes actionable private details.

Use allowlisted structured fields instead of dumping raw logs. Prefer normalized environment labels such as `linux-vm-small`, `mac-arm64-32gb`, `kind-3node`, or `github-hosted-runner` over machine/user identifiers. Bucket or aggregate resource values when exact hardware identity is unnecessary. Strip query strings from URLs and never persist environment variables by default.

### Public evidence gate

Before committing or uploading evidence publicly:

1. Validate it against the versioned evidence schema.
2. Run secret scanning and pattern checks for tokens, credentials, email addresses, absolute home paths, IP addresses, internal domains, and likely customer/company identifiers.
3. Review free-form fields manually or omit them entirely. `metadata` must be a controlled object, not an unrestricted log sink.
4. Keep raw logs private/ephemeral when redaction cannot be proven safe; publish only normalized aggregates or derived measurements.
5. Treat screenshots, traces, stack dumps, kubectl output, LDAP output, CI logs, prompts, and model transcripts as sensitive-by-default.
6. If uncertain whether a field is safe, do not publish it. Record a coarse category or null instead.

## Canonical schema

The canonical public record is JSON/JSONL and starts with these fields:

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
- `environment`: normalized non-identifying label.
- `attempt`, `human_interventions`, `review_corrections`, `ci_retries`: non-negative measured counters when applicable.
- `metadata`: documented project-specific allowlisted scalar/object values only; no raw logs, arbitrary environment dumps, prompts, source, payloads, or credentials.

Projects may extend the schema for domain-specific measurements, but extensions must be documented, machine-readable, privacy-reviewed, and backward compatible within a schema version.

## Recommended repository layout

```text
research/
  README.md                 # metric definitions, environment labels, exclusions
  evidence/
    YYYY-MM.jsonl           # durable sanitized longitudinal records
  experiments/
    <experiment-id>/        # explicit benchmarks with protocol + summarized results
```

CI may retain raw artifacts temporarily, but only sanitized schema-valid records should be committed to a public repository.

## Research integrity

Evidence collection is observational by default. A later paper may select a subset and define hypotheses, baselines, experimental controls, exclusion criteria, and statistical analysis separately. Do not optimize or selectively discard development records merely to improve a future result. Preserve schema versions and exclusion reasons so future analysis can distinguish unavailable data from intentionally excluded data.
