# Kubernetes Bootstrap Checklist

Use this as a platform-neutral bootstrap contract; implementation may use kubeadm, Kubespray, RKE2, Talos, k3s, or another supported distribution.

## Preflight

- Kubernetes version selected and compatibility matrix recorded.
- Container runtime version recorded.
- CNI selected and pinned.
- Storage class selected and tested.
- Ingress/Gateway strategy recorded.
- DNS and certificate strategy recorded.
- Time synchronization verified.
- Node OS/kernel prerequisites verified.

## Baseline add-ons

1. Metrics / resource telemetry.
2. Ingress or Gateway API implementation.
3. Certificate management.
4. Logging/observability integration.
5. Policy/admission controls as required.
6. GitOps controller when GitOps is used.
7. Backup/restore integration for persistent workloads.

## Validation

```bash
kubectl get nodes
kubectl get pods -A
kubectl get storageclass
kubectl get --raw='/readyz?verbose'
```

Do not encode provider-specific credentials or cluster secrets in this template.
