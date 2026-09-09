# Kubernetes security templates

These templates implement reusable parts of the OpenForge [Kubernetes Zero Trust Security Baseline](../../../docs/kubernetes-zero-trust-security-baseline.md).

They are baselines, not drop-in universal production configuration. Inventory the target cluster and adapt namespaces, DNS labels, Gateway/LB implementation, ports, identities, storage, CNI, and egress dependencies before enforcement.

## Files

- `security-profile.example.yml` — implementation-neutral OpenForge profile example. It is configuration documentation, not a Kubernetes CRD.
- `workload-baseline.yaml` — Pod Security namespace labels, default-deny ingress/egress, and an explicit DNS exception.
- `mesh-istio-ambient-strict.yaml` — optional Istio Ambient reference mapping to reject plaintext/bypass traffic after mesh validation.
- `check-host-security.sh` — read-only host inventory for OS, AppArmor/SELinux, firewall, and runtime prerequisites.

## Recommended adoption flow

1. Copy `security-profile.example.yml` into the target project's design/adoption record and select a profile.
2. Run `check-host-security.sh` on representative Linux nodes; do not mutate firewall or LSM state yet.
3. Apply workload runtime controls and verify application compatibility.
4. Adapt and apply the default-deny policy with every required allow rule prepared first.
5. Configure the target project's External/Internal Gateway and address pools.
6. If Cilium Host Firewall is used, start in audit and validate required traffic before enforcement.
7. If Istio Ambient is used, validate mesh enrollment/mTLS before applying `STRICT`.
8. Restrict egress and record required external dependencies.
9. Add deterministic allow/deny regression checks and rollback evidence.

## AppArmor and SELinux

Do not copy a universal custom LSM profile across heterogeneous nodes.

- AppArmor: prefer Kubernetes `RuntimeDefault` or a reviewed `Localhost` profile when AppArmor is the native LSM. A custom `Localhost` profile must exist on every eligible node.
- SELinux: keep SELinux `Enforcing` on SELinux-native distributions. Let the container runtime assign labels by default; set workload `seLinuxOptions` only for a reviewed compatibility requirement.
- Mixed clusters: use node constraints when a workload depends on an LSM-specific custom profile.

## Host firewall safety

OpenForge deliberately does not ship a universal `ufw enable`, `firewall-cmd --set-default-zone`, or `nft flush ruleset` script. Kubernetes/CNI firewall requirements depend on topology and implementation. Generate and review host firewall policy from the actual cluster design, protect management access, stage the change, and keep a rollback path.