# Agent Outcome / Evidence 일관성

OpenForge operational trace는 과거 기록 호환성과 엄격한 완료 의미를 구분합니다.

## 모드

- `legacy` 또는 미설정: 기존에 수집된 trace를 그대로 호환합니다.
- `strict`: 현재 high-risk 변경을 설명하는 trace에서 필수입니다.

## Strict 완료 계약

strict trace가 `A` 완료 상태를 보고하려면 다음을 모두 만족해야 합니다.

1. `completion_claim`이 존재해야 합니다.
2. scope와 typed evidence를 가진 verification이 있어야 합니다.
3. 관련 verification에 `passed`, `success`, `ok`, `verified` 등 명시적인 성공 status가 있어야 합니다.
4. 관련 verification 중 `failed`, `pending`, `unknown`, `skipped`, `unverified` 또는 status 미지정 상태가 없어야 합니다.

조건을 만족하지 않으면 `task-convergence`는 `false`가 됩니다. 실패했거나 명시적으로 성공하지 않은 verification 상태에서 완료를 주장하면 `evidence-before-claim`도 `false`가 됩니다.

strict bug fix에서는 `regression_verification` 역시 명시적으로 성공해야 합니다. regression check가 존재한다는 사실만으로는 충분하지 않습니다.

## B / C 수렴 상태

`B`, `C`는 다음 blocker 또는 action을 명시하면 계속 유효합니다. 다만 strict mode에서는 `completion_claim`과 동시에 존재할 수 없습니다. 진행 중/중단 상태와 완료 주장은 서로 모순되기 때문입니다.

## Verification status

검증 결과는 설명 문장에만 넣지 않고 구조화된 `status` 필드를 사용합니다.

```json
{
  "type": "verification",
  "status": "passed",
  "scope": "release workflow and immutable inputs",
  "evidence": ["ci:agent-behavior"]
}
```

## High-risk 강제 정책

Trace/Evidence correlation gate는 현재 high-risk 변경을 커버하는 trace에 `consistencyMode: strict`와 최소 하나의 명시적 성공 verification을 요구합니다. 현재 변경과 무관한 historical trace는 `not-applicable`로 유지되며 강제 migration하지 않습니다.

따라서 과거 evidence는 계속 읽을 수 있으면서, 새로운 고위험 변경은 pending/failed 검증 상태로 완료를 주장할 수 없습니다.

## Regression 의미

strict inconsistency는 기존 5개 Behavior 결과에 반영되므로 별도 점수 체계를 추가하지 않고 trusted baseline comparator가 그대로 탐지합니다. 예를 들어 기존 `evidence-before-claim: true` 또는 `task-convergence: true`가 failed/pending verification 상태의 완료 주장으로 인해 `false`로 내려가면 기존 regression gate가 차단할 수 있습니다.

즉 trace 파일 존재 여부보다 한 단계 강하게, **주장한 outcome과 기록된 evidence가 서로 일치해야 합니다.**
