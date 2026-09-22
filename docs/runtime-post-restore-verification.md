# RT-021 Post-Restore Functional Verification

RT-021 verifies declared application functionality after restore without letting OpenForge invent endpoints or execute arbitrary shell commands.

## Usage

```bash
openforge . \
  --runtime \
  --kube-context my-cluster \
  --post-restore-spec examples/post-restore-verification.json
```

The spec contains explicit Kubernetes Service probes:

```json
{
  "probes": [
    {
      "name": "api-health",
      "namespace": "production",
      "service": "api",
      "port": 8080,
      "path": "/healthz",
      "expect_contains": "ok"
    }
  ]
}
```

OpenForge converts each probe to a Kubernetes API Service proxy request and performs only `kubectl get --raw` GET operations. It does not execute commands in Pods and does not make arbitrary external URL requests.

## Scoring

The score is proportional to successful probes. All probes passing produces PASS and 10/10. Partial success remains FAIL while receiving proportional partial credit so the maturity score reflects the measured functional coverage.

```text
post_restore_probes_passed=2/3 coverage_percent=66.7
```

A probe fails when the Kubernetes Service proxy request fails or when `expect_contains` is configured and the response body does not contain that value.

## Applicability

- No `--post-restore-spec`: SKIP
- Empty or invalid spec: SKIP with evidence explaining why it could not be evaluated
- Runtime assessment disabled: SKIP
- Declared probes evaluated: PASS/FAIL based on observed results

RT-021 complements RT-013 backup freshness and RT-016 restore-resource evidence. A recent successful restore object alone does not prove that the restored application is usable; RT-021 provides a deterministic functional evidence layer.

## Trust boundary

The operator controls every namespace, Service, port, path and expected response marker. OpenForge does not discover or guess application endpoints. The current probe type is intentionally restricted to read-only Kubernetes Service proxy GET requests.
