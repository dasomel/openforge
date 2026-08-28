# Agent Evaluation 운영 표준

OpenForge Agent Behavior Trace/Eval을 실제 개발 작업에 적용하기 위한 운영 기준입니다. 모든 변경에 Trace 작성을 강제하지 않고, Agent-heavy 또는 고위험 작업에 선택적으로 적용합니다.

## 운영 흐름

```text
선택된 Agent-heavy / 고위험 작업
  → Structured Event를 점진적으로 기록
  → .agents/evals/traces/ 아래 Trace 저장
  → Deterministic Eval
  → Trusted Baseline과 비교
  → Behavior Regression일 때만 Gate 실패
```

## Trace를 남길 작업

다음과 같은 경우 Trace 작성을 권장합니다.

- AI Agent가 다단계 Bug Fix, Migration, Release, Incident 작업을 수행하는 경우
- 보안/RBAC/credential/filesystem/network/runtime 경계를 변경하는 경우
- 기존 Behavior baseline을 실제 작업에서 검증할 필요가 있는 경우
- 실패/복구 과정을 이후 regression evidence로 재사용할 가치가 있는 경우

일반적인 저위험 문서 수정이나 단순 formatting 변경에는 Trace를 강제하지 않습니다.

## Trusted Baseline

`baseline.eval.json`은 자동으로 최신 결과를 따라가는 snapshot이 아닙니다. 리뷰를 거친 기대 행동 기준입니다.

- baseline 변경은 별도 리뷰 대상
- CI를 통과시키기 위해 baseline을 낮추지 않음
- 새로운 Behavior가 추가되거나 평가 의미가 바뀌는 경우 변경 이유를 기록
- repository별 runtime evidence class는 baseline과 별도로 명시

## Regression

Outcome 순서는 다음과 같습니다.

```text
false < na < true
```

따라서 다음 변화는 regression입니다.

- `true → false`
- `true → na`
- `na → false`

반대로 `false → na`, `false → true`, `na → true`는 개선으로 기록할 수 있습니다.

## Privacy / Trust Boundary

Trace에는 hidden reasoning이나 chain-of-thought를 저장하지 않습니다. observable event와 evidence reference만 기록합니다.

Secret, token, 고객 데이터, PII 또는 불필요한 raw log를 Trace에 직접 저장하지 않습니다. 필요하면 immutable/redacted evidence의 reference만 남깁니다.

외부 Behavior/Skill/Spec은 provenance와 review 상태가 없는 경우 trusted policy로 승격하지 않습니다.

## CI 적용

Operational Trace가 존재하는 경우 CI는 다음 순서로 실행합니다.

1. Behavior structure validation
2. Trace schema validation
3. Deterministic Behavior Eval
4. Trusted Baseline comparison
5. Regression이 있으면 fail

Trace가 없는 일반 변경은 기존 repository CI만 수행할 수 있습니다.

## AGENT-005 승격 기준

Trace/Eval 운영을 portfolio compliance metric으로 승격하기 전 최소한 다음 evidence가 필요합니다.

- 서로 다른 프로젝트에서 실제 유지보수 Trace가 반복적으로 생성됨
- 실제 regression을 merge 전에 탐지한 사례
- baseline 변경이 편의상 낮아지지 않는 governance evidence
- maintenance cost 대비 debugging/regression value가 확인됨
- project-specific runtime evidence가 portable Behavior 모델과 충돌하지 않음

2026-08 cross-project 및 실제 유지보수 pilot 결과는 `agent-evaluation-adoption-2026-08.md`와 `agent-evaluation-adoption-2026-08-ko.md`에 기록합니다.
