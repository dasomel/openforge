# Kubernetes Zero Trust Security Baseline

English | [한국어](kubernetes-zero-trust-security-baseline-ko.md)

OpenForge defines this document as the canonical cross-project security baseline for OSS that builds, operates, or deploys to Kubernetes clusters. Zero Trust is a layered security outcome, not a single product.

## Scope and principles

Projects should apply the controls that match their ownership boundary and deployment model. A cluster installer is expected to cover host, node, workload, exposure, identity, and egress controls; an application-only project may apply only the workload controls.

Core principles:

- separate public/external and private/internal exposure;
- deny by default and explicitly allow required communication;
- do not trust network location alone; prefer authenticated workload identity;
- protect the Linux host separately from Kubernetes workload networking;
- enforce runtime least privilege with seccomp and a supported Linux Security Module (LSM);
- stage disruptive network controls through audit/preflight and preserve a rollback path;
- document and time-bound intentional exceptions under `docs/security-exceptions.md`.

## Security profiles

| Control | development | standard | production | zero-trust |
|---|---|---|---|---|
| Internal/external exposure separation | optional | recommended | required when both exist | required when both exist |
| Pod Security / least privilege | baseline | restricted target | restricted | restricted |
| seccomp `RuntimeDefault` | recommended | required | required | required |
| AppArmor or SELinux | detect | enabled where supported | enforcing where supported | enforcing; no unconfined workload without exception |
| Default-deny ingress | optional | workload dependent | required | required |
| Default-deny egress | optional | workload dependent | required | required |
| Host OS firewall | optional | baseline | required where host is managed | required where host is managed |
| Kubernetes-aware host firewall | optional | audit when supported | audit then enforce | audit then enforce |
| Workload mTLS | optional | recommended | required when mesh is adopted | required |
| Identity authorization | optional | recommended | required for sensitive paths | required |
| Controlled egress | optional | recommended | required | required |

Projects may define stricter profiles. A downgrade from an applicable production control requires an explicit rationale and exception record.

## 1. Exposure: internal and external gateways

Use Kubernetes Gateway API as the preferred portable contract for north-south traffic when the implementation supports it.

- External/public services and internal/private services must use distinct Gateway instances or equivalent load-balancer entry points.
- Use separate public and private VIPs/IP pools. Where the infrastructure supports it, also separate subnets/VLANs/VPC paths and firewall policy.
- Do not treat an IP-pool name such as `internal` as a security boundary by itself.
- Management surfaces such as GitOps, registry, observability, secrets, and administration should be private by default.
- An implementation may use Cilium Gateway API, APISIX, a CSP load balancer, MetalLB, or another conformant implementation; the standard defines the exposure contract rather than one product.

## 2. Host OS firewall

The host firewall protects the Linux node itself and is distinct from Kubernetes NetworkPolicy.

- Detect and manage the native firewall stack appropriate to the OS (`nftables`, `firewalld`, `ufw`, or equivalent).
- Permit only required management, control-plane, node-to-node, CNI, load-balancer health-check, storage, and observability traffic.
- Preserve CNI/runtime-managed rules and never blindly enable or flush firewall rules on an active cluster.
- Changes must have preflight validation, remote-access protection, a tested rollback path, and post-change connectivity checks.
- Firewall policy must be generated from the actual cluster topology and CNI mode rather than a hard-coded universal port list.

## 3. Kubernetes-aware node firewall

When Cilium is the CNI, Cilium Host Firewall is the preferred node-aware implementation.

- Start host policy in audit mode and inspect required traffic before enforcement.
- Treat audit mode as a migration aid, not the final production state.
- Verify kube-apiserver, kubelet, node-to-node, CNI, storage, DNS, health-check, and operational access before enforcement.
- Preserve emergency console/out-of-band access or another recovery mechanism.

Equivalent Kubernetes-aware host controls may be used when Cilium is not present.

## 4. Workload network segmentation

Production and zero-trust profiles use deny-by-default network policy.

- Apply namespace/workload default-deny ingress and egress.
- Add explicit allow rules for ingress gateways, DNS, databases, storage, observability, control services, and external dependencies.
- Avoid broad selectors such as an unrestricted `namespaceSelector: {}` in production policy.
- Prefer identity/label-scoped rules and test expected allow/deny paths as regression checks.

The reusable templates under `templates/kubernetes/security/` are intentionally conservative starting points and must be adapted to the target namespaces and dependencies.

## 5. Workload runtime security

Application workloads should target the Kubernetes Pod Security Standards `restricted` profile where practical.

Baseline container settings:

- `runAsNonRoot: true`;
- `allowPrivilegeEscalation: false`;
- `seccompProfile.type: RuntimeDefault`;
- drop all Linux capabilities and add back only reviewed requirements;
- avoid privileged containers, host PID/IPC/network, hostPath, and writable host mounts unless explicitly justified.

Platform components that require elevated privileges must be isolated, documented, and reviewed separately from ordinary application workloads.

## 6. Linux Security Module: AppArmor and SELinux

OpenForge standardizes the security outcome while allowing the native LSM of each Linux distribution.

| Host family | Preferred LSM baseline | Workload guidance |
|---|---|---|
| Ubuntu/Debian family where AppArmor is available | AppArmor enabled | use `RuntimeDefault` or reviewed `Localhost` profiles; avoid `Unconfined` in production |
| RHEL/Rocky/Alma/Fedora family where SELinux is available | SELinux `Enforcing` | rely on container-runtime labels by default; use explicit `seLinuxOptions` only when required and reviewed |
| Mixed Linux cluster | supported LSM enabled on every applicable node | constrain workloads to compatible nodes when a custom profile is node-specific |

Rules:

- Do not disable SELinux or AppArmor merely to make a deployment pass.
- Treat `Unconfined`, SELinux `Permissive`, or SELinux `Disabled` as a production exception that needs a documented reason and remediation/expiry plan.
- Custom AppArmor profiles must be distributed to every node that may schedule the workload.
- Explicit SELinux labels must be compatible with the container runtime, storage driver, and mounted volumes.
- LSM enforcement complements seccomp; neither replaces the other.

## 7. Service identity and east-west Zero Trust

A service mesh is an implementation option, not the definition of Zero Trust. When Istio Ambient is used:

- use workload identity and mTLS for mesh traffic;
- use `PeerAuthentication` `STRICT` where the requirement is to reject plaintext/bypass traffic;
- use `AuthorizationPolicy` to authorize callers by identity, namespace, service account, and only then by network attributes where necessary;
- introduce waypoint/L7 policy only where L7 authorization or processing is required.

Projects using another mesh or identity layer should provide equivalent authenticated encryption and authorization evidence.

## 8. Controlled egress

Production and zero-trust profiles restrict outbound traffic.

- Default-deny egress, then allow required DNS and destinations.
- Prefer FQDN-aware policy for approved external APIs whose addresses change dynamically.
- Use an egress gateway or equivalent when downstream systems require a stable source IP or centralized inspection.
- Record internet dependencies and verify that denied destinations remain denied.

## Rollout order

Apply disruptive controls in this order unless project-specific constraints require otherwise:

1. Inventory current exposure, host firewall/LSM state, CNI, mesh, workloads, and required flows.
2. Enable workload least privilege, seccomp, and the OS-native LSM baseline.
3. Separate external/public and internal/private entry points.
4. Introduce default-deny network policy with explicit dependency rules.
5. Put node-aware host firewall policy into audit, validate flows, then enforce.
6. Enable workload mTLS and identity authorization where supported; require plaintext rejection where the profile requires it.
7. Restrict egress and add FQDN/fixed-source exceptions deliberately.
8. Add deterministic regression checks and publish adoption evidence.

## Required evidence

A production adoption should record, where applicable:

- security profile selected;
- public/private Gateway or load-balancer inventory;
- host firewall provider/state and rollback procedure;
- CNI host-firewall audit/enforcement state;
- namespace default-deny coverage and explicit exceptions;
- seccomp and Pod Security posture;
- AppArmor/SELinux state by node family;
- mesh mTLS/plaintext-rejection and authorization evidence;
- egress allow-list/gateway configuration;
- allow/deny connectivity regression results;
- documented exceptions with owner and expiry.

## Reference implementations

OpenForge may publish Cilium, Istio Ambient, Gateway API, MetalLB, AppArmor, and SELinux examples. These are reference mappings. Projects may use equivalent implementations when they preserve the control objective and verification evidence.