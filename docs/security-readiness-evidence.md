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
5. `generate-portfolio.py` exposes the result per repository in `portfolio/dashboard.json` and the dashboard page, linking back to the evidence files (see Portfolio view).

## Files

| Path | Role |
|------|------|
| `schemas/security-readiness-evidence-v1.schema.json` | Versioned contract (`openforge-security-readiness-evidence/v1`) |
| `portfolio/security-readiness/<repo>.json` | Observed evidence, one file per repository, kept centrally in OpenForge |
| `portfolio/security-readiness/scorecard/<repo>.json` | Raw, unedited `scorecard --format=json` output; source evidence for the `scorecard` signal |
| `templates/scripts/validate-security-readiness.py` | Schema plus semantic validation; run in CI |
| `templates/scripts/import-scorecard.py` | Scorecard v5 adapter (see Scorecard adapter) |
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

## Scorecard adapter

`templates/scripts/import-scorecard.py` converts raw OpenSSF Scorecard v5 output (`scorecard --format=json`) into this record. It normalizes upstream results and never re-implements a check. It runs in **update mode**: it rewrites an existing `portfolio/security-readiness/<repo>.json` (schema version unchanged, no schema change) and refuses to write unless the result passes `validate-security-readiness.py`. Without `--write` it prints the result and leaves the file alone.

```bash
# 1. run the official Scorecard CLI (checksum-verified release binary; GITHUB_AUTH_TOKEN from your environment, never committed)
scorecard --repo=github.com/<owner>/<repo> --format=json > portfolio/security-readiness/scorecard/<repo>.json
# 2. dry run, then write
python3 templates/scripts/import-scorecard.py --record portfolio/security-readiness/<repo>.json --scorecard portfolio/security-readiness/scorecard/<repo>.json
python3 templates/scripts/import-scorecard.py --write --record portfolio/security-readiness/<repo>.json --scorecard portfolio/security-readiness/scorecard/<repo>.json
# 3. validate and regenerate the portfolio view
python3 templates/scripts/validate-security-readiness.py
python3 templates/scripts/generate-portfolio.py
```

The raw output is kept unedited in `portfolio/security-readiness/scorecard/<repo>.json` as the source evidence; `source.tool` is `openssf-scorecard` with `version`, UTC `observed_at` and a `ref` carrying the exact command, the scanned commit and that raw file path.

| Scorecard check (v5) | OpenForge signal | Applied |
|----------------------|------------------|---------|
| every check | `scorecard` | Always. Overall score sets the status: `pass` only at 10/10 with no check below 10, `fail` at 0, otherwise `partial`. Each conclusive check below 10 becomes one finding `<repo>-scorecard-<check>` with the upstream risk level as severity (`Dangerous-Workflow`/`Webhooks` critical; unknown new checks `info`). |
| `Security-Policy` | `security-policy` | Only if that signal is absent or `not-run` |
| `Pinned-Dependencies` | `actions-pinning` | Same rule; Scorecard also covers non-Actions dependencies |
| `Signed-Releases` | `release-signing` | Same rule; Scorecard also credits provenance files |
| `SBOM` (experimental, not in default output) | `sbom` | Same rule |
| all other checks | `scorecard` findings only | no dedicated signal |
| (none) | `provenance` | no Scorecard equivalent; never fed |

Per-check status for a filled signal: `10` pass, `0` fail, `1-9` partial, `-1` (inconclusive) `not-run`. A `-1` is never `pass`, and it is not counted as a conclusive check for the overall status. A signal that was observed directly (`pass`, `fail`, `partial`, `not-applicable`) is never overwritten: the adapter keeps it and prints a `NOTE`.

The adapter fails with a non-zero exit and a message, and writes nothing, on: input that is not Scorecard JSON, missing or empty `checks`, a Scorecard major version other than 5, an overall or check score outside -1..10, a `repo.name` that is not `github.com/<record repository>`, a commit that is not 40-hex, a date without UTC offset, duplicate checks, and a `scorecard` signal that is already measured (re-scan deltas are not computed; add a `rescan` block by hand). The one exception is re-importing the same run (identical tool, version, date and scanned commit, every fact unchanged): it only refreshes the checks digest in `source.ref`.

Record fields: `revision` stays the revision of the direct observations; the commit Scorecard scanned is in each `source.ref` and may differ. `observed_at` becomes the latest observation in the record.

## Portfolio view

`python3 templates/scripts/generate-portfolio.py` adds an additive top-level `security_readiness` key to `portfolio/dashboard.json` (`openforge-dashboard/v1` and every existing key are unchanged) and a "Security readiness" section to `docs/portfolio-dashboard.md`. Per repository it carries the roll-up (`fail` > `partial`; `not-run` next to a measured signal is `partial`, never `pass`), per-signal status counts, the Scorecard score, date and commit read from the raw file, and the repo-relative paths of the evidence record and raw Scorecard output. The build fails if a record cites Scorecard output that is missing or disagrees with the raw file (date, version, scanned commit, or the checks digest, so a changed overall score or check score fails the build). With no evidence directory the key is omitted.

## Validate

```bash
python3 templates/scripts/validate-security-readiness.py            # portfolio/security-readiness/*.json
python3 templates/scripts/validate-security-readiness.py --today 2026-10-07 path/to/record.json
```

## Scope

The first slice defined the schema, validator, tests and three observed samples (`narwhal`, `kubemetal`, `clusterdeck`); the re-scan slice added `rescan.resolved_findings` and re-observed `narwhal` and `kubemetal` after their `actions-pinning` remediation. The Scorecard slice added the adapter, replaced the `not-run` Scorecard signal of the three samples with real Scorecard v5.6.0 output (run 2026-10-15), and added the additive `security_readiness` portfolio summary. Adapters for other upstream tools (SBOM generators, Sigstore, SLSA) are not part of this slice.
