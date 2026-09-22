# RT-019 — CSI Storage Health

RT-019 evaluates the runtime health of CSI-backed storage without requiring a specific storage vendor.

## Evidence chain

OpenForge reads cluster-scoped Kubernetes resources only:

1. `StorageClass` — discovers CSI provisioners.
2. `CSIDriver` — verifies that each discovered CSI provisioner has a registered driver object.
3. `VolumeAttachment` — checks active attachments for `status.attached=true` and reports attach errors.

Legacy in-tree provisioners whose names start with `kubernetes.io/` are not treated as CSI provisioners by this rule.

## Result semantics

- `PASS`: every detected CSI provisioner has a matching `CSIDriver`, and every active `VolumeAttachment` for those provisioners is healthy.
- `FAIL`: one or more drivers are missing, or one or more relevant `VolumeAttachment` objects are not attached or contain an attach error.
- `SKIP`: runtime assessment is disabled, the required Kubernetes APIs are inaccessible, or no CSI-backed `StorageClass` is detected.

The score is coverage-based rather than binary. Driver registrations and active volume attachments are combined into a deterministic health ratio. A partial failure remains `FAIL` but receives proportional credit.

```text
FAIL [RT-019] CSI storage drivers and active volume attachments are healthy
csi_drivers_registered=2/2 volumeattachments_healthy=9/10 coverage_percent=91.7
volumeattachment=csi-abc attacher=example.csi.io node=node-2 attached=false attach_error=rpc timeout
```

## Scope and limitations

RT-019 does not claim end-to-end storage correctness. It does not currently verify controller Deployment/StatefulSet availability, node-plugin DaemonSet coverage, CSI capacity, snapshot support, backend latency, filesystem integrity, or application-level read/write success. Those should be separate evidence rules to avoid over-scoring a single signal.

All collection is read-only and uses Kubernetes API reads through `kubectl`.