# Security Readiness Evidence Contract

Korean: [security-readiness-evidence-ko.md](security-readiness-evidence-ko.md)

OpenForge defines one tool-neutral record for the security and supply-chain signals of a repository. It normalizes what upstream tools report; it does not re-implement them. **Upstream tools (OpenSSF Scorecard, SBOM generators, Sigstore, SLSA builders, GitHub itself) remain the source of the underlying checks, and a record is not a compliance or certification claim.** Every record carries that sentence as a required `disclaimer`.

## Pipeline

```text
upstream check -> normalized evidence -> gap/remediation or exception -> re-scan -> portfolio status
```

1. An upstream tool or a direct observation produces a result.
2. The result is written as a signal in `portfolio/security-readiness/<repo>.json`, with the exact command or URL in `source.ref`.
3. A gap becomes a finding plus a remediation state, or an owned exception.
4. A re-scan adds a `rescan` block that points to the previous observation and states `improved`, `unchanged` or `regressed`.
5. Portfolio-level exposure of the result is planned (see Scope).

## Files

| Path | Role |
|------|------|
| `schemas/security-readiness-evidence-v1.schema.json` | Versioned contract (`openforge-security-readiness-evidence/v1`) |
| `portfolio/security-readiness/<repo>.json` | Observed evidence, one file per repository, kept centrally in OpenForge |
| `templates/scripts/validate-security-readiness.py` | Schema plus semantic validation; run in CI |
| `tests/fixtures/security-readiness/` | Synthetic fixtures only; never copied into `portfolio/` |

## Signals

| Signal id | Maps to (OpenSSF Scorecard / OSPS Baseline area) | Typical upstream source |
|-----------|--------------------------------------------------|--------------------------|
| `scorecard` | OpenSSF Scorecard overall result | Scorecard API or action |
| `security-policy` | Scorecard `Security-Policy`; OSPS vulnerability-reporting guidance | `SECURITY.md` presence |
| `actions-pinning` | Scorecard `Pinned-Dependencies` (workflow actions) | Workflow `uses:` refs pinned to a full commit SHA |
| `sbom` | OSPS release SBOM expectations | SBOM generation step or release asset |
| `provenance` | SLSA build provenance | `attest-build-provenance`, `slsa-github-generator` |
| `release-signing` | Scorecard `Signed-Releases`; Sigstore | `cosign` / signature assets |

"Maps to" is orientation, not a conformance statement. Status is `pass`, `fail`, `partial`, `not-run` or `not-applicable`, the same vocabulary as `portfolio/status.schema.json` verification entries. A signal that was not measured is `not-run`; it is never recorded as `0` or `pass`.

## Rules

- `revision` is the full git SHA that was actually observed; `observed_at` and `source.observed_at` are UTC.
- Timestamps must be valid UTC datetimes; `observed_at` may not be in the future and `source.observed_at` may not be later than the record's `observed_at` (`--now` makes this deterministic).
- `fail` needs a finding, an exception or a remediation; `partial` needs a finding; `pass` carries no findings or exceptions; `not-run` carries neither findings nor exceptions.
- `finding_ids` in exceptions and re-scans claim a CURRENT finding and must resolve to findings in the same record.
- **Resolved findings:** a finding that no longer exists after remediation cannot be referenced by `finding_ids`. Record it in the optional `rescan.resolved_findings[]` as `{id, summary, resolved_by}` (`resolved_by` is the PR or commit that fixed it). `delta: improved` requires at least one entry; an id there must not still be an active finding or exception in the record, and ids may not repeat.
- `summary` counts are derived from `signals` and checked.
- Exceptions require `owner`, `rationale` and `expires`; `review_date` is optional.
- **Fail-closed expiry:** an exception whose `expires` date is before today is a validation error in CI, not a warning. Renew it with a new rationale or remediate. `--today YYYY-MM-DD` makes the check deterministic for tests.
- Strings are scanned for secret patterns; evidence holds references, never credentials.

## Re-scan after remediation

The `resolved_findings` field is an additive optional extension of `openforge-security-readiness-evidence/v1`, so the schema version is unchanged and existing records stay valid. The one new obligation applies only to a record that claims `delta: improved`; no committed record did before this change.

```json
"rescan": {
  "previous_ref": "<previous revision>", "previous_observed_at": "<UTC>", "delta": "improved",
  "resolved_findings": [{"id": "narwhal-pin-1", "summary": "...", "resolved_by": "https://github.com/<owner>/<repo>/pull/<n>"}]
}
```

The current record then carries the new status and no finding for what was fixed; the finding id stays correlatable through `resolved_findings`.

## Validate

```bash
python3 templates/scripts/validate-security-readiness.py            # portfolio/security-readiness/*.json
python3 templates/scripts/validate-security-readiness.py --today 2026-10-07 path/to/record.json
```

## Scope

The first slice defined the schema, validator, tests and three observed samples (`narwhal`, `kubemetal`, `clusterdeck`); the re-scan slice added `rescan.resolved_findings` and re-observed `narwhal` and `kubemetal` after their `actions-pinning` remediation. Exposing readiness in the portfolio summary or `dashboard.json` is a planned second slice and will be an additive key without an `openforge-dashboard/v1` version bump. Adapters that automatically convert upstream output into this record are not part of this slice.
