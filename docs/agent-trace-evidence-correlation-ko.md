# Agent Trace Evidence 상관관계

Operational trace는 자신이 검증한다고 주장하는 실제 변경과 연결되어야 의미가 있습니다. OpenForge는 따라서 trace 존재 여부, 변경 범위 연결, evidence 품질, Behavior regression을 서로 다른 gate로 구분합니다.

## 계약

PR이 high-risk로 분류되면 다음을 요구합니다.

1. 같은 diff에서 operational trace가 추가 또는 수정되어야 합니다.
2. 관련 trace의 `changeContext.paths`가 모든 high-risk 변경 경로를 커버해야 합니다.
3. 관련 trace에는 `verification` 또는 `regression_verification` 이벤트가 있어야 합니다.
4. 최소 하나의 verification 이벤트는 비어 있지 않은 `scope`를 가져야 합니다.
5. verification evidence는 `test:`, `ci:`, `runtime:`, `artifact:`, `policy:` 중 하나의 typed prefix를 사용해야 합니다.
6. 그 다음 trusted behavior baseline과 비교합니다.

현재 high-risk 변경을 전혀 커버하지 않는 과거 trace는 `not-applicable`로 처리하며 최신 필드로 강제 migration하지 않습니다. 이를 통해 새 governance 규칙이 무관한 historical evidence를 깨뜨리지 않으면서 현재 변경은 엄격하게 검증합니다.

## 예제

```json
{
  "schemaVersion": "openforge-agent-trace/v1",
  "traceId": "change-001",
  "task": "Harden release workflow",
  "changeContext": {
    "paths": [
      ".github/workflows/**",
      "scripts/ci/**"
    ]
  },
  "events": [
    {
      "id": "e4",
      "type": "regression_verification",
      "scope": "release workflow and governance checks",
      "evidence": ["ci:release-pass", "test:guard-regression"]
    }
  ]
}
```

## 변경 경로 상관관계가 필요한 이유

경로 연결이 없으면 generic trace 하나를 추가한 뒤 실제로는 전혀 다른 privileged/release-critical 파일을 변경해도 형식적으로 통과할 수 있습니다. `changeContext.paths`는 trace가 주장하는 범위를 실제 PR diff와 machine-checkable하게 연결합니다.

여러 파일이 하나의 일관된 subsystem 변경에 속하면 glob을 사용할 수 있지만, gate를 무력화하기 위해 지나치게 넓은 패턴을 사용하면 안 됩니다.

## Evidence class

Typed evidence identifier는 로그·Secret·고객 데이터·hidden reasoning을 trace에 직접 넣지 않고도 evidence 종류와 안정적인 참조를 표현하기 위한 가벼운 계약입니다.

- `test:` — deterministic test 또는 regression suite
- `ci:` — CI workflow/job/step 결과
- `runtime:` — 명시적인 runtime/environment 검증
- `artifact:` — digest, manifest, generated report 등 immutable evidence artifact
- `policy:` — deterministic policy finding 또는 policy decision

소스 파일 경로 자체는 verification evidence가 아닙니다. 무엇이 바뀌었는지는 설명할 수 있지만 변경된 동작이 정상이라는 증거는 되지 않습니다.

## Historical trace

현재 high-risk path를 하나 이상 커버하는 trace만 evidence-quality gate의 평가 대상입니다. 관련 없는 과거 trace는 `not-applicable`로 표시합니다.

첫 downstream rollout에서 이전 `pilot-001` trace가 현재 maintenance 변경과 무관함에도 새 `changeContext` 필드가 없다는 이유로 실패하는 문제가 발견됐습니다. 이를 통해 gate를 현재 변경과의 관련성 기준으로 좁혔고 OpenForge, Narwhal, KubeMetal, nfs-quota-agent에서 다시 검증했습니다.

## CI 순서

```text
PR diff
  -> risk classification
  -> same-diff trace requirement
  -> trace/change evidence correlation
  -> behavior baseline regression gate
  -> repository-specific tests/runtime evidence
```

각 단계가 답하는 질문은 서로 다릅니다. Agent Behavior workflow가 성공했다고 해서 unrelated repository CI나 실제 runtime validation까지 성공했다고 보고하면 안 됩니다.

## AGENT-005

이번 계약으로 operational evidence 품질은 강화됐지만 이것만으로 portfolio compliance metric을 하나 더 만들지는 않습니다. 자연스럽게 발생한 Behavior regression을 merge 전에 실제로 탐지한 증거가 확보된 뒤 `AGENT-005` 승격 여부를 판단합니다.
