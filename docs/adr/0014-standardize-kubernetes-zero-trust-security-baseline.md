# ADR-0014: Standardize a layered Kubernetes Zero Trust security baseline

- Status: Accepted
- Date: 2026-09-09

English | [한국어](0014-standardize-kubernetes-zero-trust-security-baseline-ko.md)

## Context

OpenForge projects increasingly build or operate Kubernetes clusters across cloud, bare-metal, local, and mixed Linux environments. Existing controls cover workload least privilege and NetworkPolicy examples, but there is no single cross-project contract for public/private exposure, host firewalling, node-aware firewalling, Linux Security Modules, workload identity, and egress.

Treating any one control such as a CSP firewall, OS firewall, Cilium, Istio, AppArmor, or SELinux as "Zero Trust" leaves material trust boundaries uncovered. At the same time, forcing one product or one Linux LSM across every project would reduce portability.

## Decision

OpenForge will define `docs/kubernetes-zero-trust-security-baseline.md` as the canonical Kubernetes cluster/workload security standard and distribute reusable templates and adoption records from it.

The standard will:

1. separate External/Public and Internal/Private entry points when both exist;
2. treat the native OS firewall and Kubernetes-aware host firewall as distinct defense layers;
3. use default-deny workload networking for production profiles;
4. require workload least privilege and seccomp;
5. abstract Linux Security Module enforcement by host family: AppArmor where appropriate and SELinux `Enforcing` where appropriate;
6. prefer authenticated workload identity and mTLS/authorization for east-west trust;
7. control egress explicitly in production and zero-trust profiles;
8. provide `development`, `standard`, `production`, and `zero-trust` adoption profiles;
9. require staged audit/preflight, rollback, regression verification, and time-bounded exceptions for disruptive controls.

Cilium Host Firewall and Istio Ambient are preferred reference mappings for projects that already use those technologies, but they are not normative dependencies. Equivalent implementations are acceptable when they preserve the control objective and evidence.

## Alternatives considered

### Rely only on CSP security groups or perimeter firewalls

Rejected. They do not provide sufficient pod/workload segmentation, runtime confinement, or workload identity authorization.

### Rely only on the Linux OS firewall

Rejected. It protects node networking but does not replace Kubernetes-aware workload policy or service identity.

### Define Zero Trust as Cilium or Istio adoption

Rejected. Each product covers only part of the trust model and would make the standard implementation-specific.

### Standardize AppArmor only

Rejected. It does not fit the RHEL-family SELinux-first operating model.

### Standardize SELinux only

Rejected. It is not the native default for many Ubuntu/Debian deployments and would make otherwise valid clusters harder to operate.

### Force the zero-trust profile in development

Rejected. Strict default-deny and host controls can materially harm local developer usability and adoption. Lower profiles remain explicit rather than silently weakening production.

## Rationale

The layered model gives each control a clear responsibility, preserves distro and platform portability, and makes security posture auditable across multiple OSS projects. A profile model allows staged adoption without confusing a development convenience setting with a production security claim.

## Consequences and trade-offs

- Cluster installers need topology and dependency discovery before enforcement.
- Default-deny and host firewall changes can cause outages if applied without audit and regression tests.
- AppArmor/SELinux custom profiles can create node scheduling and distribution obligations.
- Projects must record exceptions rather than disabling controls globally.
- Cross-project adoption becomes measurable through OpenForge portfolio evidence.

## Affected standards/templates/projects

- `docs/security.md`
- `docs/kubernetes-zero-trust-security-baseline.md`
- `templates/kubernetes/security/`
- cluster-building and Kubernetes-runtime projects in the OpenForge portfolio, beginning with Narwhal, kube-ready-box, Beluga, and KubeMetal

## Migration and adoption

Adoption should follow the staged rollout in the security baseline. OpenForge will create project-specific issues instead of copying one universal configuration into every repository. Each project must select a profile, declare non-applicable controls, and attach verification evidence.