# Kubernetes Zero Trust portfolio adoption — 2026-09

This record turns ADR-0014 and the Kubernetes Zero Trust Security Baseline into project-specific rollout work. OpenForge remains the source of truth; downstream repositories adapt the controls to their ownership boundary instead of copying one universal configuration.

## Rollout waves

| Project | Role | Target profile | Initial scope | Priority |
|---|---|---|---|---|
| Narwhal | reference implementation / cluster platform | `zero-trust` | full cluster exposure, node, workload, identity, egress | P0 |
| kube-ready-box | runtime foundation / enforcement provider | `production` | OS firewall inventory, AppArmor/SELinux, seccomp/runtime prerequisites | P0 |
| Beluga | Kubernetes data platform | `production` | workload segmentation/runtime, internal/external exposure where owned, controlled egress | P1 |
| KubeMetal | local/hybrid Kubernetes platform | `standard` → `production` where applicable | Linux-node runtime/network controls; topology-aware exposure/egress | P1 |
| nfs-quota-agent | Kubernetes controller | `production-workload` subset | restricted runtime, NetworkPolicy, explicit privilege exceptions | P2 |
| ClusterDeck | operations client | validation subset | surface cluster security posture and connectivity evidence where appropriate | P2 |
| CKA Lab | lab/education | `development` / opt-in production exercises | teach and test the baseline without changing exam-oriented defaults | P3 |

## Narwhal reference implementation acceptance

Narwhal should demonstrate the complete baseline first because it owns a full Kubernetes platform stack.

Expected outcomes:

- External/Public and Internal/Private Gateway/LB paths are explicitly separated and documented.
- Public/private VIP or address-pool ownership is explicit for CSP and bare-metal modes.
- Host OS firewall is inventoried and safely configured or an external firewall ownership boundary is documented.
- Cilium Host Firewall is staged audit → enforce with connectivity evidence.
- Application namespaces receive default-deny ingress/egress plus explicit dependency policies.
- Pod Security `restricted`, seccomp, non-root/no-escalation/capability-drop defaults are verified for ordinary workloads.
- Ubuntu/Debian nodes use AppArmor where supported; SELinux-native nodes remain `Enforcing`; exceptions are recorded rather than disabling LSM globally.
- Istio Ambient workload mTLS/identity is verified and plaintext rejection/AuthorizationPolicy is applied where required.
- Egress is allow-listed with FQDN or egress-gateway controls where applicable.
- Hubble/connectivity and policy regression checks prove expected allow and deny paths.

## kube-ready-box foundation acceptance

kube-ready-box should provide the host/runtime foundation consumed by cluster projects:

- read-only inventory of native firewall and LSM state;
- distro-aware AppArmor/SELinux prerequisites and validation;
- SELinux `Enforcing` preserved on SELinux-native images;
- AppArmor enabled/usable on AppArmor-native images;
- seccomp/runtime prerequisites verified;
- no generic firewall command that can break an unknown CNI topology;
- documented hand-off contract to cluster installers for CNI/host-firewall rules.

## Beluga and KubeMetal adaptation

These projects should consume the same control objectives but declare topology-specific N/A decisions. Local/single-node deployments must not pretend to have separate public/private network planes when the underlying topology does not provide them. Instead they should document the reduced boundary and preserve workload/runtime/egress controls that remain applicable.

## Adoption evidence contract

Each downstream issue/PR should record:

1. OpenForge baseline version or commit/PR reference.
2. Selected profile and explicitly non-applicable controls.
3. Current-state inventory before enforcement.
4. Implementation changes.
5. Allow/deny and rollback verification.
6. Remaining exceptions with owner and expiry.
7. Follow-up gaps returned to OpenForge if a reusable standard/template is missing.

## Feedback loop

```text
OpenForge standard
      ↓
project adoption issue
      ↓
implementation + verification
      ↓
project-specific evidence
      ↓
reusable gap found?
   yes ─────────────→ OpenForge standard/template update
   no  ─────────────→ adoption complete
```

A project is not considered adopted merely because it copies the template directory; it must show the applicable runtime/security evidence.