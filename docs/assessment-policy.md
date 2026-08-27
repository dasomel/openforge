# Assessment applicability profiles and waivers

OpenForge assessments are deterministic, but not every rule is applicable to every project or platform. A policy file makes applicability explicit without deleting evidence or silently changing a score.

## Usage

```bash
openforge . --policy examples/assessment-policy.json
```

The policy is applied after evidence collection and before scoring.

## Profile applicability

`profile.include_rules` and `profile.exclude_rules` use glob patterns against rule IDs.

```json
{
  "profile": {
    "name": "kubernetes-platform",
    "include_rules": ["RT-*"],
    "exclude_rules": ["RT-021"]
  }
}
```

Rules excluded by the profile remain in the report with status `NOT_APPLICABLE`. They are excluded from the score numerator and denominator.

An empty `include_rules` list means all rules are initially included. Exclusions are then applied.

## Time-bounded waivers

A waiver requires a rule ID, a non-empty reason, and an ISO date (`YYYY-MM-DD`) expiry.

```json
{
  "waivers": [
    {
      "rule_id": "RT-005",
      "reason": "Temporary singleton workload pending HA migration.",
      "expires": "2026-12-31"
    }
  ]
}
```

A valid waiver changes a failing finding status to `WAIVED`. The finding and evidence remain visible, but the rule is excluded from scoring. Waivers are only applied to `FAIL` findings; they never remove credit for a `PASS` finding.

Expired waivers are automatically ignored. Invalid expiry dates and empty reasons are also ignored. In each case OpenForge preserves an evidence message explaining why the waiver was not applied.

A waiver does not turn a failure into a pass. It documents a temporary accepted exception.

## Policy identity and fingerprint

When a policy is used, the report includes both the profile name and a deterministic policy fingerprint:

```json
{
  "policy": {
    "profile": "kubernetes-platform",
    "fingerprint": "fnv1a64:..."
  }
}
```

The fingerprint is intended for change detection, not cryptographic verification. OpenForge canonicalizes the include/exclude rule lists and waiver entries before fingerprinting, so reordering equivalent entries does not create a false policy change.

`openforge compare` checks policy identity in addition to assessment schema and ruleset. It emits compatibility warnings when a policy is introduced, removed, the profile changes, or the fingerprint changes. This prevents a score change caused by applicability or waiver changes from being mistaken for a platform improvement or regression.

## Scoring semantics

Only `PASS` and `FAIL` findings contribute to score calculation.

- `PASS`: contributes earned and maximum weight.
- `FAIL`: contributes maximum weight, but zero or partial earned score depending on the rule.
- `SKIP`: provider/evidence not applicable or unavailable; excluded from scoring.
- `NOT_APPLICABLE`: explicitly excluded by profile; excluded from scoring.
- `WAIVED`: explicit, unexpired exception; excluded from scoring.

The report includes a policy summary with the profile name, fingerprint, and counts of excluded, waived, expired, and invalid waiver entries.

## CI guidance

Keep the policy file in version control and review changes like code. Avoid broad patterns such as excluding all security rules. Prefer narrow, rule-specific waivers with short expiry windows and a concrete remediation reason.

Combine the policy with score and regression gates:

```bash
openforge . \
  --runtime \
  --policy openforge-policy.json \
  --format json \
  --output current.json \
  --fail-under 80

openforge compare baseline.json current.json --fail-on-regression
```

For the cleanest trend signal, compare assessments generated with the same ruleset and the same policy fingerprint.
