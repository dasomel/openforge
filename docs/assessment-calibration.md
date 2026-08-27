# Assessment Calibration

OpenForge calibration measures the quality of the **assessment rules themselves** against reviewed project evidence. It is not a mechanism for changing a project's score to match an expected number.

## Why calibrate

A deterministic rule can still be wrong for a real project. Calibration distinguishes:

- `true_finding` — a reported failure represents a real maturity gap.
- `false_positive` — a reported failure is caused by incomplete or overly narrow detection.
- `not_applicable` — the rule should not apply to the project or selected profile.
- `accepted` — the observed result is expected and does not require rule correction.

The calibration report exposes classification coverage and failure precision so rule changes can be evaluated with evidence rather than intuition.

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

`--require-complete` returns exit code `2` while any assessment rule remains unclassified. This is useful only after a calibration manifest is intentionally complete; it should not be enabled for an early seed manifest.

## Metrics

`classification_coverage_percent` is:

```text
classified assessment rules / all assessment rules
```

`failure_precision_percent` is:

```text
true_findings / (true_findings + false_positives)
```

Only manually reviewed classifications should be added. A high coverage number created from guessed classifications is worse than a low but trustworthy coverage number.

## Reference calibration: Narwhal

`examples/calibration/narwhal.json` is the first reference calibration manifest. The `Calibration` GitHub Actions workflow checks out both OpenForge and Narwhal, runs a static `kubernetes-platform` assessment, applies the reviewed expectations, and uploads both JSON reports as workflow artifacts.

The initial manifest is intentionally small. It establishes stable known-good evidence first; subsequent findings should be classified only after inspecting Narwhal's implementation and, for runtime-dependent rules, actual cluster evidence.

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
