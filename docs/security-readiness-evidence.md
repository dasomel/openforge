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
- `fail` needs a finding, an exception or a remediation; `not-run` carries no findings; `pass` carries no exceptions.
- `summary` counts are derived from `signals` and checked.
- Exceptions require `owner`, `rationale` and `expires`; `review_date` is optional.
- **Fail-closed expiry:** an exception whose `expires` date is before today is a validation error in CI, not a warning. Renew it with a new rationale or remediate. `--today YYYY-MM-DD` makes the check deterministic for tests.
- Strings are scanned for secret patterns; evidence holds references, never credentials.

## Validate

```bash
python3 templates/scripts/validate-security-readiness.py            # portfolio/security-readiness/*.json
python3 templates/scripts/validate-security-readiness.py --today 2026-10-07 path/to/record.json
```

## Scope

This is the first slice: schema, validator, tests and three observed samples (`narwhal`, `kubemetal`, `clusterdeck`). Exposing readiness in the portfolio summary or `dashboard.json` is a planned second slice and will be an additive key without an `openforge-dashboard/v1` version bump. Adapters that automatically convert upstream output into this record are not part of this slice.
