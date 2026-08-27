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
| RT-005 | Runtime Reliability | PodDisruptionBudget 존재 여부 |
| RT-006 | Runtime Security | NetworkPolicy 존재 여부 |

`--namespace`를 지정하지 않으면 namespaced workload 진단은 전체 namespace를 대상으로 합니다. Node 진단은 항상 cluster scope입니다.

## Evidence 원칙

- Kubernetes API에서 읽은 관측 결과만 사용합니다.
- 접근 실패나 도구 부재는 FAIL로 단정하지 않고 `SKIP`으로 기록합니다.
- `SKIP`은 점수 분모에서 제외합니다.
- Runtime FAIL은 정적 manifest 존재 여부가 아니라 현재 cluster 상태를 의미합니다.
- 단순히 리소스가 존재한다고 전체 정책 적용이 보장되는 항목은 이후 coverage 기반 규칙으로 강화합니다.

## 제한사항

v0.3의 PDB와 NetworkPolicy는 우선 실제 리소스 존재 여부를 확인합니다. workload별 coverage, RBAC privilege 분석, deprecated API discovery, backup/restore verification, certificate expiry, GitOps drift, observability health는 후속 버전에서 evidence semantics를 정의한 뒤 추가합니다.
