# Assessment Calibration

OpenForge calibration measures the quality of the **assessment rules themselves** against reviewed project evidence. It is not a mechanism for changing a project's score to match an expected number.

## Why calibrate

A deterministic rule can still be wrong for a real project. Calibration distinguishes:

- `true_finding` — a reported failure represents a real maturity gap.
- `false_positive` — a reported failure is caused by incomplete or overly narrow detection.
- `not_applicable` — the rule should not apply to the project or selected profile.
- `accepted` — a passed rule is supported by reviewed evidence and does not require rule correction.

The calibration report exposes classification coverage and failure precision so rule changes can be evaluated with evidence rather than intuition.

Classification semantics are validated: `true_finding` and `false_positive` require a `FAIL` result, `accepted` requires `PASS`, and `not_applicable` is valid for a wrongly applied `FAIL` or an already corrected `NOT_APPLICABLE` result.

## Workflow

First produce an assessment:

```bash
openforge assess ../narwhal \
  --profile kubernetes-platform \
  --format json \
  --output narwhal-assessment.json
```

Then review findings and record only conclusions that have been manually verified:

```json
{
  "project": "dasomel/narwhal",
  "profile": "kubernetes-platform",
  "expectations": {
    "DOC-001": {
      "classification": "accepted",
      "rationale": "The canonical README is present and substantive."
    }
  }
}
```

Run calibration:

```bash
openforge calibrate \
  narwhal-assessment.json \
  examples/calibration/narwhal.json
```

Use JSON for automation:

```bash
openforge calibrate \
  narwhal-assessment.json \
  examples/calibration/narwhal.json \
  --format json \
  --output narwhal-calibration.json
```

`--require-complete` returns exit code `2` while an **active PASS/FAIL rule** remains unclassified. `SKIP`, `NOT_APPLICABLE`, `WAIVED`, and other non-scoring findings are reported as inactive and do not lower calibration coverage.

## Metrics

`classification_coverage_percent` is:

```text
classified active PASS/FAIL rules / all active PASS/FAIL rules
```

`failure_precision_percent` is:

```text
true_findings / (true_findings + false_positives)
```

`inactive_rules` reports findings that were not scored in the assessment run. They remain visible for auditability but are not mixed into active-rule coverage.

Only manually reviewed classifications should be added. A high coverage number created from guessed classifications is worse than a low but trustworthy coverage number.

## Reference calibration: Narwhal

`examples/calibration/narwhal.json` is the first reference calibration manifest. The `Calibration` GitHub Actions workflow checks out both OpenForge and Narwhal, runs a static `kubernetes-platform` assessment, applies the reviewed expectations, requires complete classification of all active static rules, and uploads both JSON reports as workflow artifacts.

The first Narwhal run exposed detector gaps rather than project gaps: shell regression scripts were not recognized by `CI-002`, GitOps manifests were outside `PLT-002` through `PLT-005` path scopes, and documentation badges/screenshots were being scored as web-application image assets. Those cases are now regression-tested so future rules cannot silently reintroduce them.

Runtime rules remain outside this static calibration until real cluster evidence is collected.

## Rule improvement loop

```text
real project
    ↓
assessment
    ↓
manual evidence review
    ↓
calibration classification
    ↓
false-positive / applicability analysis
    ↓
small rule change + regression test
    ↓
re-assessment
```

Do not modify a target repository merely to make OpenForge's score look better. If the rule is wrong, fix the rule. If the project has a real gap, keep the finding and improve the project separately.
