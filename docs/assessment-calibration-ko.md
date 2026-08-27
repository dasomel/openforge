# Assessment Calibration

OpenForge Calibration은 프로젝트 점수를 임의의 기대값에 맞추는 기능이 아니라, **진단 규칙 자체의 품질**을 실제 프로젝트 증거와 비교해 검증하는 기능입니다.

## 왜 Calibration이 필요한가

결정론적인 규칙도 실제 프로젝트에서는 잘못 판단할 수 있습니다. Calibration은 결과를 다음과 같이 구분합니다.

- `true_finding` — 보고된 FAIL이 실제 성숙도 Gap입니다.
- `false_positive` — 탐지 범위가 좁거나 불완전해서 발생한 오탐입니다.
- `not_applicable` — 해당 프로젝트/Profile에는 적용하면 안 되는 규칙입니다.
- `accepted` — PASS 결과가 검토된 증거와 일치하며 규칙 수정이 필요하지 않습니다.

Calibration Report는 Classification Coverage와 Failure Precision을 제공해 규칙 보정을 감이 아니라 증거로 수행하도록 합니다.

분류와 Assessment 상태의 일관성도 검증합니다. `true_finding`과 `false_positive`는 `FAIL`, `accepted`는 `PASS`여야 하며, `not_applicable`은 잘못 적용된 `FAIL` 또는 이미 보정된 `NOT_APPLICABLE` 상태에서 사용할 수 있습니다.

## 실행 흐름

먼저 진단 결과를 생성합니다.

```bash
openforge assess ../narwhal \
  --profile kubernetes-platform \
  --format json \
  --output narwhal-assessment.json
```

그 다음 실제 증거를 사람이 확인한 항목만 expectation으로 기록합니다.

```json
{
  "project": "dasomel/narwhal",
  "profile": "kubernetes-platform",
  "expectations": {
    "DOC-001": {
      "classification": "accepted",
      "rationale": "Canonical README가 존재하고 충분한 내용을 포함한다."
    }
  }
}
```

Calibration을 실행합니다.

```bash
openforge calibrate \
  narwhal-assessment.json \
  examples/calibration/narwhal.json
```

자동화에서는 JSON을 사용할 수 있습니다.

```bash
openforge calibrate \
  narwhal-assessment.json \
  examples/calibration/narwhal.json \
  --format json \
  --output narwhal-calibration.json
```

`--require-complete`는 **실제 점수 계산에 참여하는 PASS/FAIL 규칙** 가운데 미분류 항목이 있으면 exit code `2`를 반환합니다. `SKIP`, `NOT_APPLICABLE`, `WAIVED` 등 비점수 finding은 inactive로 보고되지만 Coverage 분모에는 포함하지 않습니다.

## 지표

`classification_coverage_percent`는 다음 비율입니다.

```text
분류 완료된 활성 PASS/FAIL rule / 전체 활성 PASS/FAIL rule
```

`failure_precision_percent`는 다음과 같습니다.

```text
true_findings / (true_findings + false_positives)
```

`inactive_rules`는 현재 Assessment에서 점수화되지 않은 finding 수입니다. 감사 가능성을 위해 Report에는 유지하지만 활성 규칙 Coverage와 섞지 않습니다.

추측으로 높은 Coverage를 만드는 것보다 검증된 낮은 Coverage가 더 가치 있습니다.

## Reference Calibration Set

OpenForge는 하나의 선호 프로젝트에 규칙을 맞추지 않고 구조가 다른 실제 프로젝트 여러 개를 Reference로 사용합니다. `Calibration` Workflow는 static reference를 각각 독립적으로 실행하고 `fail-fast: false`로 한 프로젝트의 실패가 다른 프로젝트 검증을 막지 않도록 하며, 모든 활성 규칙의 분류 완료를 Gate로 검증합니다. Assessment와 Calibration JSON은 각각 artifact로 저장합니다.

### Narwhal

`examples/calibration/narwhal.json`은 Shell/GitOps 중심 Kubernetes Platform을 검증합니다. 첫 Calibration에서 프로젝트 Gap이 아니라 진단기 Gap도 발견됐습니다. Shell 기반 regression test가 `CI-002`에서 인식되지 않았고, `gitops/` manifest가 `PLT-002~005` 검색 경로에서 빠져 있었으며, README badge와 문서 screenshot이 Web Application image asset으로 점수화되고 있었습니다. 이 사례들은 regression test로 고정했습니다.

Detector 보정 후 static `kubernetes-platform` 평가는 82.6점(`B`, `L4 Resilient`)이며 활성 규칙 20/20을 모두 분류했습니다. 검토된 실제 Gap은 4개, false positive는 0개이고 Classification Coverage와 Failure Precision은 모두 100%입니다.

### NFS Quota Agent

`examples/calibration/nfs-quota-agent.json`은 구조가 다른 Go + Helm Reference입니다. Narwhal의 GitOps 구조 대신 Go test/lint/security workflow, Helm workload probe/resource/PDB, Prometheus resource와 Kubernetes packaging을 독립적으로 검증합니다.

Static `kubernetes-platform` 평가는 73.4점(`C`, `L3 Production`)이고 활성 규칙 20/20을 모두 분류했습니다. FAIL 6개는 검토 결과 실제 프로젝트 Gap으로 유지됐고 false positive는 0개였습니다. 따라서 Narwhal에서 수행한 Detector 보정이 한 Repository에만 과적합된 것이 아니라 다른 구현 방식에서도 성립함을 확인할 수 있습니다.

## L2 Execution Calibration

Static Repository Evidence와 Trusted Execution Evidence는 별도 Contract로 관리합니다. `examples/calibration/nfs-quota-agent-execution.json`은 명시적으로 `--run-execution`을 사용하는 NFS Quota Agent 실행 Job에서만 적용됩니다. 이 Calibration은 다음 규칙을 활성화하여 검증합니다.

- `EXE-GO-001` — `go build ./...`
- `EXE-GO-002` — `go test ./...`
- `EXE-GO-003` — `go vet ./...`

Execution은 대상 Repository의 코드를 실제 실행하기 때문에 계속 명시적 opt-in으로 유지합니다. Static Calibration에서 비활성 Execution probe를 Coverage를 높이기 위해 억지로 분류하지 않습니다.

## L3 Runtime Replay Calibration

Runtime Detector는 실제 운영 Cluster에 적용하기 전에 결정론적인 회귀검증 계층이 필요합니다. `examples/runtime-fixtures/` 아래 fixture는 Kubernetes API 형태의 JSON과 제한된 `kubectl` replay shim으로 구성하며 **CI 테스트 전용 증거**입니다. Fixture PASS를 실제 Cluster 건강 상태의 증거로 사용하지 않습니다.

하나의 synthetic cluster에 모든 공급자와 장애를 억지로 넣는 대신, Runtime Replay를 작은 evidence group으로 분리합니다.

### Core: RT-001~006

공급자와 무관한 Kubernetes 핵심 동작을 검증합니다.

- `RT-001` — Node Ready 상태
- `RT-002` — Workload desired availability
- `RT-003` — Workload health probe
- `RT-004` — CPU/Memory request 및 limit
- `RT-005` — PodDisruptionBudget coverage
- `RT-006` — NetworkPolicy coverage

`healthy-core`는 Ready node, 정상 replica, probe/resource, PDB/NetworkPolicy coverage를 포함하고 `degraded-core`는 NotReady node, 부족한 replica, probe/resource limit 누락, PDB/NetworkPolicy 미구성 상태를 포함합니다. CI는 Healthy 6/6 `accepted`, Degraded 6/6 `true_finding`을 요구하며 Degraded 결과는 false positive 0, Coverage와 Failure Precision 100%입니다.

### Compatibility / Security: RT-007~010

별도 Runtime Security Contract에서 다음을 검증합니다.

- `RT-007` — 활성 deprecated Kubernetes API request
- `RT-008` — non-system `cluster-admin` binding
- `RT-009` — 실제 binding된 wildcard/escalation 계열 고위험 RBAC
- `RT-010` — 명시적으로 고위험인 Pod security 설정

`healthy-security`는 활성 deprecated API metric이 없고 system-safe administration, 제한된 RBAC, 고위험 workload security 설정이 없는 상태입니다. `degraded-security`는 각 detector가 잡아야 하는 결함을 하나씩 기록합니다. CI는 Healthy 4/4 `accepted`, Degraded 4/4 `true_finding`을 검증하며 false positive 0, Coverage/Failure Precision 100%를 유지합니다.

### Storage / Certificate / Backup Resilience: RT-011~013

Resilience Contract는 아래 세 규칙만 활성화합니다.

- `RT-011` — PVC Bound/volume 상태
- `RT-012` — cert-manager Certificate 잔여 유효기간
- `RT-013` — Velero Completed Backup 최신성

`healthy-resilience`에는 Bound PVC, 30일 위험 구간 밖의 Certificate, 7일 freshness window 안의 Velero backup이 들어 있습니다. `degraded-resilience`에는 volume이 없는 Pending PVC, 잔여 8일 Certificate, 408시간 지난 Completed backup이 들어 있습니다. CI는 Healthy 3/3 `accepted`, Degraded 3/3 `true_finding`을 검증하며 false positive 0, Classification Coverage와 Failure Precision 100%입니다.

RT-012와 RT-013은 시간에 민감합니다. 일반 Runtime Assessment는 실제 UTC 현재시각을 사용합니다. Replay CI에서는 `OPENFORGE_NOW=2026-08-27T07:00:00Z`를 설정해 기록된 인증서 만료시각과 backup timestamp를 시간이 지나도 결정론적으로 해석합니다. `OPENFORGE_NOW`는 **replay/test evidence-time override**이며, 이를 사용했다고 해서 fixture 결과가 실제 운영 Cluster의 시간 기반 증거로 바뀌는 것은 아닙니다.

각 fixture의 `policy.json`은 해당 그룹의 규칙만 활성화합니다. Replay shim이 지원하지 않는 `kubectl` 호출은 fail-closed로 종료해 다른 Collector가 가짜 성공 증거를 받지 못하게 합니다. Healthy/Degraded 대칭 검증으로 Detector가 항상 PASS만 반환해도 Calibration을 통과하는 문제도 방지합니다.

다음 Runtime Replay group은 `RT-014`부터 시작하며 observability, GitOps/restore, Prometheus target/Alertmanager, CSI/storage, post-restore functional verification처럼 외부 API/provider 경계에 따라 계속 작게 분리합니다.

Evidence 단계는 다음처럼 구분합니다.

```text
recorded API-shaped fixture
    ↓ detector regression
controlled test cluster
    ↓ integration validation
real reference cluster
    ↓ reviewed operational evidence
production maturity conclusion
```

Replay PASS는 “검토된 fixture를 Detector가 올바르게 해석했다”는 의미일 뿐 실제 Cluster가 동일 규칙을 통과했다는 의미는 아닙니다.

## Reference 추가 원칙

새 Reference는 기존 프로젝트와 언어, packaging 또는 deployment layout이 실질적으로 다른 프로젝트를 우선합니다. Expectation을 작성하기 전에 실제 증거를 검토하고, 실제 Gap은 `true_finding`으로 유지하며, 진짜 Detector/Applicability 결함이 확인될 때만 OpenForge를 수정합니다. 기존 Reference와 같은 구조를 반복하는 프로젝트보다 기존 가정을 반증할 가능성이 있는 프로젝트가 더 가치 있습니다.

## 규칙 개선 Loop

```text
실제 프로젝트 또는 검토된 fixture
    ↓
assessment
    ↓
증거 검토
    ↓
calibration classification
    ↓
false-positive / applicability 분석
    ↓
작은 rule 수정 + regression test
    ↓
전체 reference set 재진단
```

OpenForge 점수를 높이기 위해 대상 프로젝트를 억지로 수정해서는 안 됩니다. 규칙이 잘못됐다면 OpenForge 규칙을 고치고, 프로젝트에 실제 Gap이 있다면 finding을 유지한 채 프로젝트 개선을 별도로 진행합니다.
