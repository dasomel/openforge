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

## Reference calibration set

OpenForge uses multiple deliberately different real projects rather than tuning rules against one preferred repository. The `Calibration` workflow runs each static reference independently with `fail-fast: false`, requires complete classification of every active rule, and uploads the assessment and calibration reports as artifacts.

### Narwhal

`examples/calibration/narwhal.json` covers a shell/GitOps-heavy Kubernetes platform. Its first calibration exposed detector gaps rather than project gaps: shell regression scripts were not recognized by `CI-002`, GitOps manifests were outside `PLT-002` through `PLT-005` path scopes, and documentation badges/screenshots were being scored as web-application image assets. Those cases are regression-tested so future rules cannot silently reintroduce them.

After those detector corrections, the static `kubernetes-platform` assessment is 82.6 (`B`, `L4 Resilient`) with 20/20 active rules classified, four reviewed true findings, zero false positives, and 100% classification coverage/failure precision.

### NFS Quota Agent

`examples/calibration/nfs-quota-agent.json` provides a structurally different Go + Helm reference. It independently exercises conventional Go test/lint/security workflows, Helm workload probes/resources/PDBs, Prometheus resources and Kubernetes packaging instead of Narwhal's GitOps layout.

Its static `kubernetes-platform` assessment is 73.4 (`C`, `L3 Production`) with 20/20 active rules classified. Six reviewed failures remain real project gaps and no false positive is required to make the reference pass. This is evidence that the Narwhal detector corrections generalize to a second implementation style rather than merely fitting one repository.

## L2 execution calibration

Static repository evidence and trusted execution evidence are separate contracts. `examples/calibration/nfs-quota-agent-execution.json` extends the NFS Quota Agent reference only for the explicit `--run-execution` job. The execution calibration activates and verifies:

- `EXE-GO-001` — `go build ./...`
- `EXE-GO-002` — `go test ./...`
- `EXE-GO-003` — `go vet ./...`

Execution remains opt-in because OpenForge is intentionally executing code from the target repository. Static calibration never classifies disabled execution probes merely to raise coverage.

## L3 runtime replay calibration

Runtime detector development needs a deterministic regression layer before validation against a live cluster. `examples/runtime-fixtures/` contains reviewed Kubernetes API-shaped JSON plus deliberately narrow `kubectl` replay shims. These fixtures are CI test evidence only; fixture results must not be presented as proof that a real cluster is healthy or unhealthy.

Runtime replay is split into small evidence groups instead of one synthetic cluster that claims to model every provider and failure mode.

### Core: RT-001 through RT-006

The core contract covers provider-independent Kubernetes behavior:

- `RT-001` — Ready node state
- `RT-002` — desired workload availability
- `RT-003` — workload health probes
- `RT-004` — CPU/memory requests and limits
- `RT-005` — PodDisruptionBudget coverage
- `RT-006` — NetworkPolicy coverage

`healthy-core` contains Ready nodes, fully available workloads, probes/resources and matching PDB/NetworkPolicy coverage. `degraded-core` contains a NotReady node, an under-replicated Deployment, missing probes and resource limits, and no matching PDB or NetworkPolicy. CI requires 6/6 `accepted` for the healthy fixture and 6/6 `true_finding` for the degraded fixture; the degraded contract has zero false positives with 100% coverage and failure precision.

### Compatibility and security: RT-007 through RT-010

A separate runtime-security contract covers:

- `RT-007` — active deprecated Kubernetes API requests
- `RT-008` — non-system `cluster-admin` bindings
- `RT-009` — bound wildcard/escalation RBAC privileges
- `RT-010` — explicitly high-risk Pod security settings

`healthy-security` contains no active deprecated API metric, only system-safe administration evidence, bounded RBAC, and no explicitly high-risk workload security settings. `degraded-security` deliberately records one defect for each detector. CI requires 4/4 `accepted` for healthy evidence and records 4/4 reviewed `true_finding` results for degraded evidence with zero false positives and 100% coverage/failure precision.

### Storage, certificate and backup resilience: RT-011 through RT-013

The resilience contract activates only:

- `RT-011` — PVC Bound/volume health
- `RT-012` — cert-manager Certificate remaining lifetime
- `RT-013` — Velero completed-backup freshness

`healthy-resilience` contains a Bound PVC, a Certificate outside the 30-day risk window, and a completed Velero backup inside the seven-day freshness window. `degraded-resilience` contains a Pending PVC with no bound volume, a Certificate with eight days remaining, and a completed backup 408 hours old. CI requires 3/3 `accepted` for healthy evidence and reports 3/3 `true_finding` for degraded evidence, again with zero false positives and 100% classification coverage/failure precision.

RT-012 and RT-013 are time-sensitive. Normal runtime assessment uses the real UTC clock. Replay CI sets `OPENFORGE_NOW=2026-08-27T07:00:00Z` so recorded expiry and backup timestamps remain deterministic. `OPENFORGE_NOW` is a replay/test evidence-time override; using it does not turn recorded fixture evidence into proof about a live cluster.

Each fixture's `policy.json` activates only its intended rules. Unsupported `kubectl` calls fail closed in every replay shim, so unrelated collectors cannot silently receive fabricated successful evidence. The healthy/degraded symmetry also prevents a detector from passing calibration merely because it always returns PASS.

The next replay groups start at `RT-014` and should continue to be split by external API/provider boundary: observability, GitOps/restore, Prometheus targets/Alertmanager, CSI/storage, and post-restore functional verification.

The intended evidence ladder remains:

```text
recorded API-shaped fixture
    ↓ detector regression
controlled test cluster
    ↓ integration validation
real reference cluster
    ↓ reviewed operational evidence
production maturity conclusion
```

A replay PASS means the detector correctly interpreted the reviewed fixture. It does **not** mean a live cluster passed the same rule.

## Adding another reference

Choose a project that differs materially in language, packaging or deployment layout. Review its evidence before writing expectations, keep real gaps as `true_finding`, and change OpenForge only when a genuine detector/applicability defect is demonstrated. A new reference is valuable when it can disprove an assumption made by existing references, not when it merely repeats the same repository shape.

## Rule improvement loop

```text
real project or reviewed fixture
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
re-assessment across the reference set
```

Do not modify a target repository merely to make OpenForge's score look better. If the rule is wrong, fix the rule. If the project has a real gap, keep the finding and improve the project separately.
