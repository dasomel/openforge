# RT-018 Alertmanager Runtime Health

RT-018 evaluates the runtime availability of Alertmanager instances managed by Prometheus Operator.

## Evidence

OpenForge reads `alertmanagers.monitoring.coreos.com` across the cluster and compares:

- desired replicas: `spec.replicas` (default: 1)
- available replicas: `status.availableReplicas`

The rule passes only when every detected Alertmanager instance has `availableReplicas >= desired replicas`.

Example failure evidence:

```text
alertmanager=monitoring/main desired=3 available=2
```

## Applicability

- If runtime assessment is disabled, the rule is `SKIP`.
- If the Prometheus Operator Alertmanager API is unavailable, the rule is `SKIP`.
- If the API exists but no Alertmanager resources are present, the rule is `SKIP`.
- A provider not being used is never treated as a maturity failure.

## Safety

RT-018 is read-only. It only executes `kubectl get ... -o json` and never creates, patches, deletes, restarts, or execs into resources.

## Scope

This rule measures Alertmanager control-plane availability. It does not yet prove that notifications are successfully delivered to external receivers. Receiver delivery verification should be implemented as a separate rule so that availability and end-to-end alert delivery remain distinct evidence types.
