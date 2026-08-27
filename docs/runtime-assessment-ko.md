# Kubernetes Runtime Assessment (L3)

OpenForge L3는 실행 중인 Kubernetes 플랫폼의 실제 상태를 읽어 성숙도 evidence를 수집합니다.

## 실행

```bash
openforge . --runtime
openforge . --runtime --kube-context my-cluster
openforge . --runtime --kube-context my-cluster --namespace production
openforge . --runtime --format json --output openforge-runtime.json
```

L3 v0.3은 `kubectl`을 read-only transport로 사용합니다. 대상 kubeconfig/context가 접근 가능해야 하며 OpenForge는 리소스 생성, 수정, 삭제 명령을 실행하지 않습니다.

## 현재 진단 항목

| Rule | 영역 | Evidence |
|---|---|---|
| RT-001 | Runtime Availability | 모든 Node의 Ready condition |
| RT-002 | Runtime Availability | Deployment/StatefulSet/DaemonSet desired 대비 available/ready |
| RT-003 | Runtime Reliability | workload container의 readiness/liveness/startup probe |
| RT-004 | Runtime Operations | workload container CPU/memory requests/limits 존재 여부 |
| RT-005 | Runtime Reliability | 복제 workload 대비 PodDisruptionBudget selector coverage |
| RT-006 | Runtime Security | workload 대비 NetworkPolicy podSelector coverage |

`--namespace`를 지정하지 않으면 namespaced workload 진단은 전체 namespace를 대상으로 합니다. Node 진단은 항상 cluster scope입니다.

## Coverage 기반 점수

RT-005와 RT-006은 정책 리소스가 하나라도 존재하는지만 보지 않습니다. 실제 workload template labels와 정책 selector를 비교해 적용률을 계산합니다.

예시:

```text
RT-005 PodDisruptionBudget workload coverage
coverage=75.0% (3/4)
uncovered: production/api

RT-006 NetworkPolicy workload coverage
coverage=83.3% (5/6)
uncovered: production/worker
```

부분 적용인 경우 `FAIL` 상태와 함께 coverage 비율만큼 부분 점수를 부여합니다. 따라서 정책 하나가 존재한다고 전체 점수를 받지 못합니다.

PDB coverage의 기본 대상은 replicas가 2개 이상인 Deployment/StatefulSet입니다. DaemonSet과 단일 replica workload는 기본 PDB coverage 분모에서 제외합니다. NetworkPolicy coverage는 Deployment/StatefulSet/DaemonSet workload를 대상으로 합니다.

Selector 비교는 Kubernetes의 `matchLabels`와 `matchExpressions` (`In`, `NotIn`, `Exists`, `DoesNotExist`)를 지원합니다.

## Evidence 원칙

- Kubernetes API에서 읽은 관측 결과만 사용합니다.
- 접근 실패나 도구 부재는 FAIL로 단정하지 않고 `SKIP`으로 기록합니다.
- `SKIP`은 점수 분모에서 제외합니다.
- Runtime FAIL은 정적 manifest 존재 여부가 아니라 현재 cluster 상태를 의미합니다.
- 적용률을 계산할 수 있는 정책은 단순 존재 여부보다 coverage 기반 evidence를 우선합니다.
- coverage 계산의 분모와 제외 기준을 명시해 동일 입력에 대해 동일 결과가 나오도록 합니다.

## 제한사항과 후속 범위

현재 NetworkPolicy coverage는 selector가 workload pod template labels를 선택하는지 평가합니다. ingress/egress 규칙의 실제 허용 범위나 CNI datapath enforcement까지 검증하는 것은 아닙니다.

RBAC privilege 분석, deprecated API discovery, backup/restore verification, certificate expiry, GitOps drift, observability health는 후속 버전에서 evidence semantics를 정의한 뒤 추가합니다.
