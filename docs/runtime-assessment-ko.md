# Kubernetes Runtime Assessment (L3)

OpenForge L3는 실행 중인 Kubernetes 플랫폼의 실제 상태를 읽어 성숙도 evidence를 수집합니다.

## 실행

```bash
openforge . --runtime
openforge . --runtime --kube-context my-cluster
openforge . --runtime --kube-context my-cluster --namespace production
openforge . --runtime --format json --output openforge-runtime.json
```

L3 v0.6는 `kubectl`을 read-only transport로 사용합니다. 대상 kubeconfig/context가 접근 가능해야 하며 OpenForge는 리소스 생성, 수정, 삭제 명령을 실행하지 않습니다.

## 현재 진단 항목

| Rule | 영역 | Evidence |
|---|---|---|
| RT-001 | Runtime Availability | 모든 Node의 Ready condition |
| RT-002 | Runtime Availability | Deployment/StatefulSet/DaemonSet desired 대비 available/ready |
| RT-003 | Runtime Reliability | workload container의 readiness/liveness/startup probe |
| RT-004 | Runtime Operations | workload container CPU/memory requests/limits 존재 여부 |
| RT-005 | Runtime Reliability | 복제 workload 대비 PodDisruptionBudget selector coverage |
| RT-006 | Runtime Security | workload 대비 NetworkPolicy podSelector coverage |
| RT-007 | Runtime Compatibility | API server에서 실제 요청된 deprecated API metric |
| RT-008 | Runtime Security | built-in cluster-admin에 연결된 비시스템 subject |
| RT-009 | Runtime Security | 비시스템 subject에 바인딩된 ClusterRole의 wildcard/escalate/bind/impersonate 권한 |
| RT-010 | Runtime Security | privileged, host namespace, hostPath, root, privilege escalation, 위험 capability 등 명시적 Pod 보안 위험 |
| RT-011 | Runtime Storage | PersistentVolumeClaim의 Bound 상태와 실제 volume binding |
| RT-012 | Runtime Reliability | cert-manager Certificate의 실제 `status.notAfter`와 30일 만료 임계치 |
| RT-013 | Runtime Recovery | Velero Backup의 최근 성공 완료 evidence와 7일 freshness 임계치 |
| RT-014 | Runtime Observability | Prometheus Operator Prometheus 인스턴스 desired/available replica 상태 |
| RT-015 | Runtime GitOps | Argo CD Application sync/health 및 Flux Kustomization/HelmRelease Ready 상태 |
| RT-016 | Runtime Recovery | Velero Restore의 최근 성공 완료 evidence와 30일 restore-drill 임계치 |

`--namespace`를 지정하지 않으면 namespaced workload/PVC/Certificate/Backup 진단은 전체 namespace를 대상으로 합니다. Node와 cluster-scoped RBAC 진단은 항상 cluster scope입니다. RT-014~016은 provider 리소스를 전체 클러스터 범위에서 탐지합니다.

## Coverage 기반 점수

RT-005와 RT-006은 정책 리소스가 하나라도 존재하는지만 보지 않습니다. 실제 workload template labels와 정책 selector를 비교해 적용률을 계산합니다.

부분 적용인 경우 `FAIL` 상태와 함께 coverage 비율만큼 부분 점수를 부여합니다. PDB coverage의 기본 대상은 replicas가 2개 이상인 Deployment/StatefulSet이며, NetworkPolicy coverage는 Deployment/StatefulSet/DaemonSet workload를 대상으로 합니다. Selector 비교는 Kubernetes의 `matchLabels`와 `matchExpressions` (`In`, `NotIn`, `Exists`, `DoesNotExist`)를 지원합니다.

## Deprecated API 사용 진단

RT-007은 manifest에서 deprecated 문자열을 검색하지 않습니다. API server의 `/metrics`에서 `apiserver_requested_deprecated_apis`를 읽고 실제 요청 이력이 있는 API만 FAIL evidence로 기록합니다. API server metrics를 읽을 권한이 없거나 endpoint에 접근할 수 없으면 점수를 임의로 낮추지 않고 `SKIP` 처리합니다.

## RBAC 최소 권한 진단

RT-008은 오탐이 적고 영향도가 큰 built-in `cluster-admin` ClusterRoleBinding을 검사합니다. `system:*` 주체, `system:masters`, `kube-system` ServiceAccount는 시스템 주체로 간주해 기본 경고 대상에서 제외합니다.

RT-009는 미사용 ClusterRole을 실패시키지 않습니다. 비시스템 subject가 실제 ClusterRoleBinding을 통해 사용 중인 ClusterRole만 분석하고 verbs/resources/apiGroups wildcard와 `escalate`, `bind`, `impersonate`를 evidence로 기록합니다. RT-008에서 이미 평가하는 `cluster-admin`은 중복 감점하지 않습니다.

## Pod Security 위험 진단

RT-010은 hardening 필드가 빠졌다는 이유만으로 FAIL 처리하지 않습니다. 초기 버전에서는 `privileged: true`, `allowPrivilegeEscalation: true`, `runAsUser: 0`, hostNetwork/hostPID/hostIPC, hostPath volume, 고위험 capability 추가처럼 해석이 명확한 위험 설정만 탐지합니다.

## Storage/PVC 상태 진단

RT-011은 PVC 리소스 존재 여부가 아니라 현재 상태와 binding을 검사합니다. assessment scope에 PVC가 없다면 `SKIP` 처리합니다. PVC phase가 `Bound`가 아니거나 `spec.volumeName`이 비어 있으면 FAIL evidence가 됩니다.

## Certificate expiration 진단

RT-012는 특정 인증서 관리 방식을 강제하지 않습니다. cert-manager `Certificate` API가 존재하고 `status.notAfter`를 관측할 수 있는 경우에만 평가합니다.

- 남은 유효기간이 30일 이상이면 PASS
- 30일 미만 또는 이미 만료된 인증서는 FAIL
- cert-manager API가 없거나 평가 가능한 Certificate가 없으면 SKIP

## Backup evidence 진단

RT-013은 Velero `Backup` API가 존재하는 경우에만 평가합니다.

- 최근 168시간(7일) 안에 `Completed` Backup이 있으면 PASS
- Backup 리소스는 있으나 성공 완료 이력이 없거나 마지막 성공 Backup이 7일보다 오래되면 FAIL
- Velero API 또는 Backup 리소스 자체가 없으면 SKIP

## Observability health 진단

RT-014는 관측 도구의 단순 설치 여부를 점수화하지 않습니다. 첫 provider adapter는 Prometheus Operator이며 `Prometheus.spec.replicas`와 `status.availableReplicas`를 비교해 실제 control-plane 가용성을 판단합니다.

```text
RT-014 Observability control plane is healthy
prometheus=monitoring/main desired=2 available=1
```

Prometheus Operator API가 없거나 Prometheus 리소스가 없으면 SKIP합니다. 현재는 Prometheus 자체 availability evidence이며 scrape target success ratio, alert pipeline, metrics freshness, ServiceMonitor/PodMonitor coverage는 후속 규칙으로 분리합니다.

## GitOps reconciliation / drift 진단

RT-015는 GitOps 제품 자체를 강제하지 않고 지원 provider가 실제 탐지될 때만 평가합니다. 현재 Argo CD와 Flux를 지원합니다.

Argo CD는 `Application.status.sync.status == Synced`와 `Application.status.health.status == Healthy`를 모두 요구합니다. Flux는 `Kustomization`과 `HelmRelease`의 `Ready=True` condition을 평가합니다.

```text
RT-015 GitOps resources are reconciled and healthy
argocd_application=argocd/platform sync=OutOfSync health=Healthy
flux_kustomization=flux-system/apps ready=False reason=ReconciliationFailed
```

Argo CD와 Flux가 함께 존재하면 탐지된 모든 지원 리소스를 하나의 deterministic evidence set으로 평가합니다. 지원 리소스가 하나도 없으면 SKIP합니다.

## Restore verification 진단

RT-016은 RT-013의 backup existence/freshness와 분리된 실제 restore evidence 규칙입니다. Velero `Restore` API가 존재하면 최근 성공 restore를 확인합니다.

- 최근 30일 안에 `Completed` Restore가 있으면 PASS
- Restore API는 존재하지만 성공 완료 Restore가 없거나 마지막 성공 Restore가 30일보다 오래되면 FAIL
- Velero Restore API 자체가 없으면 SKIP

```text
RT-016 Recent successful restore verification evidence exists
latest_completed_restore=velero/monthly-drill age_hours=120 threshold_hours=720
```

이 규칙은 restore 리소스의 성공 완료 evidence를 측정합니다. 복구된 애플리케이션의 기능 테스트나 데이터 정합성 검증까지 자동으로 보장하지는 않으므로, 향후 post-restore verification hook과 분리해 확장할 수 있습니다.

## Evidence 원칙

- Kubernetes API에서 읽은 관측 결과만 사용합니다.
- 접근 실패나 도구 부재는 FAIL로 단정하지 않고 `SKIP`으로 기록합니다.
- `SKIP`은 점수 분모에서 제외합니다.
- Runtime FAIL은 정적 manifest 존재 여부가 아니라 현재 cluster 상태를 의미합니다.
- 적용률을 계산할 수 있는 정책은 단순 존재 여부보다 coverage 기반 evidence를 우선합니다.
- 특정 구현(cert-manager, Velero, Prometheus Operator, Argo CD, Flux)이 없는 경우 해당 구현을 사용하지 않는다는 이유만으로 감점하지 않습니다.
- 단, provider API가 실제 존재하면서 해당 운영 evidence가 없을 경우에는 해당 규칙의 목적에 따라 FAIL로 평가할 수 있습니다.
- 권한 및 보안 진단은 해석이 명확한 고위험 상태부터 단계적으로 추가합니다.

## 제한사항과 후속 범위

현재 NetworkPolicy coverage는 selector가 workload pod template labels를 선택하는지 평가하며 실제 CNI datapath enforcement까지 검증하지 않습니다. RT-009는 ClusterRoleBinding 기반 cluster-scoped 권한을 우선 분석하고, aggregated ClusterRole과 transitive privilege graph는 후속 범위입니다. RT-010은 명시적 위험 설정을 우선 탐지하며 전체 Restricted/Baseline 준수율은 별도 coverage 규칙으로 확장할 수 있습니다.

RT-011은 PVC/PV binding 건강 상태를 우선 평가합니다. RT-012~016은 provider-specific evidence adapter를 사용하되 provider 미사용 자체를 실패로 간주하지 않습니다. 향후 동일 evidence semantics 아래 다른 certificate, backup, observability, GitOps, recovery provider를 adapter 방식으로 추가할 수 있습니다.

다음 후보는 Prometheus target coverage/health, Alertmanager delivery health, StorageClass/CSI controller health, post-restore functional verification입니다.
