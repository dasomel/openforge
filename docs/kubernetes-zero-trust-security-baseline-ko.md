# Kubernetes Zero Trust 보안 기준

[English](kubernetes-zero-trust-security-baseline.md) | 한국어

OpenForge는 Kubernetes 클러스터를 구축·운영하거나 Kubernetes에 배포하는 OSS를 위한 공통 보안 기준의 원본을 이 문서로 정의합니다. Zero Trust는 특정 제품 하나가 아니라 여러 계층의 보안 통제를 결합한 결과입니다.

## 범위와 원칙

프로젝트는 자신이 소유하는 경계와 배포 형태에 맞는 통제를 적용합니다. 클러스터 설치 프로젝트는 Host, Node, Workload, Exposure, Identity, Egress 계층을 다뤄야 하며, 애플리케이션 전용 프로젝트는 Workload 계층만 적용할 수 있습니다.

핵심 원칙:

- Public/External과 Private/Internal 노출을 분리합니다.
- 기본 차단 후 필요한 통신만 명시적으로 허용합니다.
- 네트워크 위치만 신뢰하지 않고 인증된 Workload Identity를 우선합니다.
- Linux Host 보호와 Kubernetes Workload 네트워크 보호를 별도 계층으로 관리합니다.
- seccomp와 지원되는 Linux Security Module(LSM)로 Runtime 최소 권한을 적용합니다.
- 장애 가능성이 큰 네트워크 통제는 Audit/Preflight 단계를 거치고 Rollback 경로를 유지합니다.
- 의도적인 예외는 `docs/security-exceptions.md`에 따라 사유와 만료 시점을 기록합니다.

## 보안 프로파일

| 통제 | development | standard | production | zero-trust |
|---|---|---|---|---|
| Internal/External 노출 분리 | 선택 | 권장 | 둘 다 존재하면 필수 | 둘 다 존재하면 필수 |
| Pod Security / 최소 권한 | baseline | restricted 목표 | restricted | restricted |
| seccomp `RuntimeDefault` | 권장 | 필수 | 필수 | 필수 |
| AppArmor 또는 SELinux | 탐지 | 지원 시 활성화 | 지원 시 Enforcing | Enforcing, 예외 없는 Unconfined 금지 |
| Default-deny Ingress | 선택 | Workload별 | 필수 | 필수 |
| Default-deny Egress | 선택 | Workload별 | 필수 | 필수 |
| Host OS Firewall | 선택 | baseline | Host 관리 시 필수 | Host 관리 시 필수 |
| Kubernetes-aware Host Firewall | 선택 | 지원 시 Audit | Audit 후 Enforce | Audit 후 Enforce |
| Workload mTLS | 선택 | 권장 | Mesh 채택 시 필수 | 필수 |
| Identity Authorization | 선택 | 권장 | 민감 경로 필수 | 필수 |
| Controlled Egress | 선택 | 권장 | 필수 | 필수 |

프로젝트는 더 강한 프로파일을 정의할 수 있습니다. 적용 가능한 Production 통제를 낮추는 경우 명시적 사유와 예외 기록이 필요합니다.

## 1. Exposure: Internal / External Gateway

구현체가 지원한다면 North-South 트래픽의 이식 가능한 기본 계약으로 Kubernetes Gateway API를 우선합니다.

- External/Public 서비스와 Internal/Private 서비스는 서로 다른 Gateway 또는 동등한 LoadBalancer 진입점을 사용합니다.
- Public VIP/IP Pool과 Private VIP/IP Pool을 분리합니다. 인프라가 지원하면 Subnet/VLAN/VPC 경로와 Firewall 정책까지 분리합니다.
- `internal` 같은 IP Pool 이름만으로 보안 경계가 생긴다고 보지 않습니다.
- GitOps, Registry, Observability, Secrets, Administration 등 관리 화면은 기본적으로 Private로 둡니다.
- Cilium Gateway API, APISIX, CSP LoadBalancer, MetalLB 등 구현체는 바꿀 수 있으며 OpenForge는 제품이 아니라 노출 계약을 표준화합니다.

## 2. Host OS Firewall

Host Firewall은 Linux Node 자체를 보호하며 Kubernetes NetworkPolicy와 별개입니다.

- OS에 맞는 Native Firewall Stack(`nftables`, `firewalld`, `ufw` 등)을 탐지·관리합니다.
- Management, Control Plane, Node-to-Node, CNI, LoadBalancer Health Check, Storage, Observability에 필요한 트래픽만 허용합니다.
- CNI/Runtime이 관리하는 Rule을 보존하며 운영 중인 클러스터에서 Firewall Rule을 무작정 활성화하거나 Flush하지 않습니다.
- 변경 전 Preflight, 원격 접속 보호, 검증된 Rollback, 변경 후 Connectivity 검증을 수행합니다.
- 고정된 범용 Port List가 아니라 실제 Cluster Topology와 CNI Mode에서 정책을 생성합니다.

## 3. Kubernetes-aware Node Firewall

Cilium을 CNI로 사용할 때는 Cilium Host Firewall을 우선 참조 구현으로 사용합니다.

- Host Policy는 Audit Mode부터 시작해 필요한 트래픽을 확인한 후 Enforce합니다.
- Audit Mode는 전환 단계이며 최종 Production 상태로 취급하지 않습니다.
- Enforce 전에 kube-apiserver, kubelet, Node 간 통신, CNI, Storage, DNS, Health Check, 운영 접속을 검증합니다.
- Emergency Console/OOB 또는 다른 복구 수단을 유지합니다.

Cilium이 없는 환경에서는 동등한 Kubernetes-aware Host 통제를 사용할 수 있습니다.

## 4. Workload Network Segmentation

Production과 Zero-Trust 프로파일은 Default Deny를 사용합니다.

- Namespace/Workload에 Default-Deny Ingress/Egress를 적용합니다.
- Ingress Gateway, DNS, Database, Storage, Observability, Control Service, External Dependency만 명시적으로 허용합니다.
- Production Policy에서 제한 없는 `namespaceSelector: {}` 같은 광범위 Selector를 피합니다.
- Identity/Label 기반 Rule을 우선하고 Allow/Deny 경로를 Regression Test로 검증합니다.

`templates/kubernetes/security/`의 재사용 템플릿은 보수적인 시작점이며 실제 Namespace와 Dependency에 맞게 수정해야 합니다.

## 5. Workload Runtime Security

일반 애플리케이션은 가능한 경우 Kubernetes Pod Security Standards의 `restricted` 수준을 목표로 합니다.

기본 Container 설정:

- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `seccompProfile.type: RuntimeDefault`
- Linux Capability는 모두 제거하고 검토된 요구사항만 다시 추가
- 명시적 사유가 없다면 Privileged Container, Host PID/IPC/Network, hostPath, Writable Host Mount를 사용하지 않음

권한 상승이 필요한 Platform Component는 일반 Application Workload와 분리해 별도 검토·기록합니다.

## 6. Linux Security Module: AppArmor와 SELinux

OpenForge는 보안 결과를 표준화하되 Linux 배포판의 Native LSM을 사용합니다.

| Host 계열 | 우선 LSM 기준 | Workload 지침 |
|---|---|---|
| AppArmor를 지원하는 Ubuntu/Debian 계열 | AppArmor 활성화 | `RuntimeDefault` 또는 검토된 `Localhost`; Production에서 `Unconfined` 지양 |
| SELinux를 지원하는 RHEL/Rocky/Alma/Fedora 계열 | SELinux `Enforcing` | 기본적으로 Container Runtime Label을 사용하고 필요한 경우에만 검토 후 `seLinuxOptions` 지정 |
| Mixed Linux Cluster | 적용 가능한 모든 Node에서 지원 LSM 활성화 | Custom Profile이 Node 종속이면 호환 Node로 Scheduling 제한 |

규칙:

- 배포 오류를 우회하기 위해 SELinux/AppArmor를 끄지 않습니다.
- `Unconfined`, SELinux `Permissive`, `Disabled`는 Production 예외로 취급하고 사유와 개선/만료 계획을 기록합니다.
- Custom AppArmor Profile은 Workload가 Scheduling될 수 있는 모든 Node에 배포합니다.
- 명시적 SELinux Label은 Container Runtime, Storage Driver, Mounted Volume과 호환되어야 합니다.
- LSM과 seccomp는 상호 보완 관계이며 서로를 대체하지 않습니다.

## 7. Service Identity와 East-West Zero Trust

Service Mesh는 구현 방식 중 하나이며 Zero Trust 자체의 정의가 아닙니다. Istio Ambient를 사용할 경우:

- Mesh Traffic에 Workload Identity와 mTLS를 사용합니다.
- Plaintext/Bypass Traffic 거부가 요구되는 곳에는 `PeerAuthentication` `STRICT`를 사용합니다.
- `AuthorizationPolicy`로 Caller Identity, Namespace, ServiceAccount를 우선 인가하고 필요한 경우에만 Network Attribute를 함께 사용합니다.
- L7 Authorization/Processing이 필요한 곳에만 Waypoint를 도입합니다.

다른 Mesh/Identity 계층을 사용하는 프로젝트도 동등한 인증 암호화와 인가 증적을 제공해야 합니다.

## 8. Controlled Egress

Production과 Zero-Trust 프로파일은 Outbound Traffic을 제한합니다.

- Egress를 기본 차단하고 필요한 DNS 및 Destination만 허용합니다.
- IP가 동적으로 변하는 승인된 External API는 FQDN-aware Policy를 우선합니다.
- 하위 시스템이 고정 Source IP 또는 중앙 검사를 요구하면 Egress Gateway 또는 동등 기능을 사용합니다.
- Internet Dependency를 기록하고 차단 대상이 실제로 계속 차단되는지 검증합니다.

## 적용 순서

프로젝트 제약이 없다면 장애 가능성이 큰 통제를 다음 순서로 적용합니다.

1. 현재 Exposure, Host Firewall/LSM, CNI, Mesh, Workload, 필요 통신을 Inventory합니다.
2. Workload 최소 권한, seccomp, OS Native LSM 기준을 적용합니다.
3. External/Public과 Internal/Private 진입점을 분리합니다.
4. Explicit Dependency Rule과 함께 Default-Deny NetworkPolicy를 도입합니다.
5. Node-aware Host Firewall을 Audit으로 적용하고 검증 후 Enforce합니다.
6. 지원 환경에서 Workload mTLS와 Identity Authorization을 적용하고 프로파일이 요구하면 Plaintext를 거부합니다.
7. Egress를 제한하고 FQDN/고정 Source 예외를 의도적으로 추가합니다.
8. Deterministic Regression Check와 적용 증적을 남깁니다.

## 필수 증적

Production 적용 시 해당되는 항목을 기록합니다.

- 선택한 Security Profile
- Public/Private Gateway 또는 LoadBalancer Inventory
- Host Firewall Provider/상태와 Rollback 절차
- CNI Host Firewall Audit/Enforcement 상태
- Namespace Default-Deny 적용 범위와 명시적 예외
- seccomp 및 Pod Security 상태
- Node 계열별 AppArmor/SELinux 상태
- Mesh mTLS/Plaintext 거부와 Authorization 증적
- Egress Allow-list/Gateway 구성
- Allow/Deny Connectivity Regression 결과
- Owner와 Expiry가 있는 예외 기록

## 참조 구현

OpenForge는 Cilium, Istio Ambient, Gateway API, MetalLB, AppArmor, SELinux 예제를 제공할 수 있습니다. 이들은 참조 매핑이며 프로젝트는 동일한 통제 목적과 검증 증적을 만족하는 다른 구현을 사용할 수 있습니다.