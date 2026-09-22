# ADR-0014: 계층형 Kubernetes Zero Trust 보안 기준 표준화

- 상태: Accepted
- 날짜: 2026-09-09

[English](0014-standardize-kubernetes-zero-trust-security-baseline.md) | 한국어

## 배경

OpenForge의 여러 프로젝트가 Cloud, Bare Metal, Local, Mixed Linux 환경에서 Kubernetes 클러스터를 구축하거나 운영하고 있습니다. 기존 기준에는 Workload 최소 권한과 NetworkPolicy 예제가 있지만 Public/Private 노출, Host Firewall, Kubernetes-aware Host Firewall, Linux Security Module, Workload Identity, Egress를 하나로 묶는 공통 계약이 없습니다.

CSP Firewall, OS Firewall, Cilium, Istio, AppArmor, SELinux 중 하나만으로 Zero Trust를 정의하면 중요한 Trust Boundary가 남습니다. 반대로 모든 프로젝트에 하나의 제품이나 하나의 Linux LSM을 강제하면 이식성이 떨어집니다.

## 결정

OpenForge는 `docs/kubernetes-zero-trust-security-baseline.md`를 Kubernetes Cluster/Workload 보안의 Canonical 표준으로 정의하고 여기서 재사용 Template과 Adoption Record를 배포합니다.

표준은 다음을 요구합니다.

1. External/Public과 Internal/Private 진입점을 둘 다 사용하는 경우 분리합니다.
2. Native OS Firewall과 Kubernetes-aware Host Firewall을 서로 다른 방어 계층으로 취급합니다.
3. Production 프로파일은 Default-Deny Workload Networking을 사용합니다.
4. Workload 최소 권한과 seccomp를 적용합니다.
5. Linux Security Module은 Host 계열에 따라 추상화합니다. 적합한 환경에서는 AppArmor, SELinux 계열에서는 `Enforcing`을 사용합니다.
6. East-West 신뢰는 인증된 Workload Identity와 mTLS/Authorization을 우선합니다.
7. Production/Zero-Trust 프로파일은 Egress를 명시적으로 통제합니다.
8. `development`, `standard`, `production`, `zero-trust` 적용 프로파일을 제공합니다.
9. 장애 영향이 큰 통제는 단계적 Audit/Preflight, Rollback, Regression Verification, 기한이 있는 예외 관리를 요구합니다.

Cilium Host Firewall과 Istio Ambient는 해당 기술을 이미 사용하는 프로젝트의 우선 참조 구현이지만 필수 의존성은 아닙니다. 동일한 통제 목적과 증적을 만족하면 동등 구현을 사용할 수 있습니다.

## 검토한 대안

### CSP Security Group 또는 Perimeter Firewall만 사용

거부합니다. Pod/Workload Segmentation, Runtime Confinement, Workload Identity Authorization을 충분히 제공하지 못합니다.

### Linux OS Firewall만 사용

거부합니다. Node Network는 보호하지만 Kubernetes-aware Workload Policy나 Service Identity를 대체하지 못합니다.

### Cilium 또는 Istio 도입을 Zero Trust로 정의

거부합니다. 각 제품은 Trust Model의 일부만 담당하며 표준이 구현체에 종속됩니다.

### AppArmor만 표준화

거부합니다. RHEL 계열의 SELinux 중심 운영 모델에 맞지 않습니다.

### SELinux만 표준화

거부합니다. 많은 Ubuntu/Debian 환경의 Native 기본과 맞지 않아 정상적인 Cluster 운영을 불필요하게 어렵게 만듭니다.

### Development에도 Zero-Trust 프로파일 강제

거부합니다. Strict Default-Deny와 Host 통제는 Local 개발 편의와 도입성을 크게 저하시킬 수 있습니다. 낮은 프로파일을 명시적으로 제공하되 이를 Production 보안 수준으로 오인하지 않도록 합니다.

## 근거

계층형 모델은 각 통제의 책임을 명확히 하고 Linux 배포판과 Platform 이식성을 유지하면서 여러 OSS의 보안 상태를 동일 기준으로 Audit할 수 있게 합니다. Profile 모델은 개발 편의 설정을 Production 보안 주장과 혼동하지 않으면서 단계적으로 적용할 수 있게 합니다.

## 결과와 Trade-off

- Cluster Installer는 Enforce 전에 Topology와 Dependency Discovery가 필요합니다.
- Default-Deny와 Host Firewall은 Audit/Regression Test 없이 적용하면 장애를 만들 수 있습니다.
- Custom AppArmor/SELinux Profile은 Node Distribution과 Scheduling 제약을 만들 수 있습니다.
- 프로젝트는 보안 통제를 전역 비활성화하는 대신 예외를 기록해야 합니다.
- OpenForge Portfolio Evidence를 통해 Cross-Project Adoption을 측정할 수 있습니다.

## 영향 받는 표준/템플릿/프로젝트

- `docs/security.md`
- `docs/kubernetes-zero-trust-security-baseline.md`
- `templates/kubernetes/security/`
- OpenForge Portfolio의 Cluster 구축 및 Kubernetes Runtime 프로젝트, 우선 Narwhal, kube-ready-box, Beluga, KubeMetal

## 마이그레이션과 적용

Security Baseline의 단계적 Rollout 순서를 따릅니다. 모든 Repository에 동일 설정을 그대로 복사하지 않고 OpenForge에서 프로젝트별 적용 Issue를 생성합니다. 각 프로젝트는 Profile을 선택하고 N/A 통제를 선언하며 Verification Evidence를 남깁니다.