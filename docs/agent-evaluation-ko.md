# Agent Evaluation 표준

OpenForge는 Behavior Specification과 Behavior Evaluation을 분리합니다. `BEHAVIOR.md`는 반복적으로 기대되는 행동을 정의하고, Trace Evaluation은 실제 실행 증거가 그 행동을 뒷받침하는지 평가합니다.

## 평가 파이프라인

```text
BEHAVIOR.md
  → structured trace
  → deterministic evaluation
  → eval result
  → baseline comparison
  → regression report
  → semantic gap에 대한 human/model review
```

기본 Evaluator는 의도적으로 제한적입니다. 명시적으로 기록된 Event와 Evidence Reference만 평가하며, 자유 형식 문장에서 숨겨진 reasoning, intent, semantic quality를 추론하지 않습니다.

## Trace 형식

Canonical Trace Schema는 `openforge-agent-trace/v1`입니다.

```json
{
  "schemaVersion": "openforge-agent-trace/v1",
  "traceId": "task-001",
  "events": [
    {"id": "e1", "type": "scope_check"},
    {"id": "e2", "type": "verification", "scope": "unit tests", "evidence": ["test:unit-pass"]},
    {"id": "e3", "type": "task_outcome", "state": "A"}
  ]
}
```

Event ID는 Trace 내에서 유일해야 합니다. `evidence`는 Test Result, CI Job, Command, File, Runtime Check, Review Record, External Source Identifier 같은 관측 가능한 증거의 Reference 배열입니다.

## Baseline Event Vocabulary

| Event type | 목적 |
| --- | --- |
| `scope_check` | 요청된 변경 범위 확인 |
| `change` | 범위 내 구현 변경 기록 |
| `scope_expansion` | 의도적 범위 확장. 승인된 경우 `approved: true` |
| `unrelated_change` | 범위 밖 변경 기록. scope-discipline 실패로 처리 |
| `reproduction` | 수정 전 실패 재현 증거 |
| `bug_fix` | Bug Fix Workflow 표시 |
| `regression_verification` | 수정 후 원래 Failure에 대한 회귀 검증 |
| `verification` | 범위가 명확한 검사. `scope`, `evidence` 포함 |
| `completion_claim` | 완료 또는 검증 완료 주장 |
| `task_outcome` | 수렴 상태 `A`, `B`, `C`. `B/C`는 `next` 필요 |
| `external_input` | 외부 Behavior/Skill/Spec/Guidance. `provenance`, `reviewed` 포함 |

프로젝트는 추가 Event Type을 정의할 수 있습니다. Baseline Evaluator가 모르는 Event는 보존하지만 점수에는 사용하지 않습니다.

## Deterministic Baseline Evaluation

`templates/scripts/evaluate-agent-trace.py`는 5개 Baseline Behavior를 평가합니다.

- `evidence-before-claim` — Completion Claim에는 Scope와 Evidence Reference가 있는 Verification Event가 필요합니다.
- `scope-discipline` — Unrelated Change 또는 승인되지 않은 Scope Expansion이 있으면 실패합니다.
- `bug-fix-verification` — Bug Fix에는 Reproduction과 Regression Verification이 모두 필요합니다.
- `task-convergence` — Task는 `A`, `B`, `C` 중 하나로 종료해야 하며 `B/C`에는 다음 Blocker 또는 Action이 필요합니다.
- `trust-and-provenance` — 외부 Behavior/Skill/Spec 입력에는 Provenance와 Review Marker가 필요합니다.

결과는 `true`, `false`, `na`입니다. `na`는 해당 Behavior가 Trace에서 사용되지 않았다는 의미이며 Pass가 아닙니다.

```bash
python3 templates/scripts/evaluate-agent-trace.py templates/agent-eval/trace.example.json
```

Exit Code는 Applicable Behavior 실패가 없으면 `0`, 하나 이상 실패하면 `1`, Trace가 구조적으로 잘못되었거나 읽을 수 없으면 `2`입니다.

## Regression 비교

대표 Task의 Eval JSON을 저장하고 Trusted Baseline과 비교할 수 있습니다.

```bash
python3 templates/scripts/evaluate-agent-trace.py trace-before.json --out eval-before.json
python3 templates/scripts/evaluate-agent-trace.py trace-after.json --out eval-after.json
python3 templates/scripts/compare-agent-evals.py eval-before.json eval-after.json
```

Baseline 순서는 `false < na < true`입니다. `true → false`, `true → na`, `na → false`는 Regression으로 처리하며 Regression이 있으면 비교 Command는 `1`을 반환합니다.

## CI에서 검증할 것과 검증하지 않을 것

CI에 적합한 항목:

- Trace Schema 유효성
- Evaluator 자체 Regression Test
- Event 수집 방식이 결정적인 Representative Trace
- 명시적인 Behavior Regression

Sparse Trace만으로 Agent의 Semantic Quality 전체를 증명해서는 안 됩니다. Human Review 또는 Model-based Eval을 추가할 수 있지만 Trace Evidence를 명시해야 하고 Deterministic Failure를 조용히 덮어써서는 안 됩니다.

## Privacy와 Provenance

Trace에는 Prompt, Source Material, Identity, Credential, Repository Detail, Tool Output 등 민감 정보가 포함될 수 있습니다. 평가에 필요한 최소 Evidence만 저장하고 Raw Secret이나 전체 Conversation Transcript보다 Reference, Hash, Redacted Summary, CI Identifier를 우선 사용합니다.

External Trace와 Eval Baseline도 Provenance와 Integrity가 확인되기 전까지 Untrusted Input으로 취급합니다.

## 성숙도 단계

1. **Specification** — 반복적이고 중요한 Behavior 정의
2. **Instrumentation** — 대표 Task에 최소 Structured Event 기록
3. **Deterministic Eval** — Trace에서 관측 가능한 속성 평가
4. **Regression Baseline** — 안정적인 Scenario의 Trusted Eval Result 보존
5. **Semantic Eval** — 결정론적 Evidence로 부족한 영역에 한해 Rubric/Human/Model Eval 추가
6. **Portfolio Governance** — 여러 프로젝트에서 운영 증거가 확보된 이후에만 OpenForge Compliance Control로 승격
