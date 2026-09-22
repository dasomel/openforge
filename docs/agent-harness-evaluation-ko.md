# 실험적 Agent Harness 평가 프로필

[English](agent-harness-evaluation.md)

> 상태: **Experimental / non-normative.** 이 프로필은 통제된 Pilot을 지원하며 기본 Harness, Model, Provider 또는 Subscription을 선택하거나 권장하지 않습니다.

동일한 Model도 Coding Harness의 Initial Instruction, Tool Schema, Context Management, Retry 방식, Execution Loop가 달라지면 다른 결과를 낼 수 있습니다. Correctness만 비교하면 이 차이가 가려질 수 있으므로 OpenForge는 통제된 Cohort 안에서 Correctness, Efficiency, Reliability, Safety를 비교하는 별도 Experiment Dataset을 제공합니다.

이 프로필은 [Agent Evaluation 표준](agent-evaluation-ko.md)을 보완합니다. Behavior Trace는 관측된 수행이 행동 계약을 만족했는지 평가하고, Harness Dataset은 그 수행에 사용된 Context, Tool Activity, Time, Intervention, 추정 API Cost를 평가합니다. Run은 `traceId`로 Behavior Trace를 참조할 수 있지만 두 Schema는 독립적으로 유지합니다.

## 구성 요소

- Dataset Schema: [`schemas/agent-harness-dataset-v1.schema.json`](../schemas/agent-harness-dataset-v1.schema.json)
- 중립적 Example: [`templates/agent-eval/harness-dataset.example.json`](../templates/agent-eval/harness-dataset.example.json)
- Comparison CLI: [`templates/scripts/compare-agent-harness-runs.py`](../templates/scripts/compare-agent-harness-runs.py)

Dataset Schema는 `openforge-agent-harness-dataset/v1`, Comparison Output은 `openforge-agent-harness-comparison/v1`입니다.

## 통제 Cohort

다음 필드가 모두 동일할 때만 Run을 집계합니다.

| 통제 항목 | 고정하는 이유 |
|---|---|
| Task ID와 Task Class | 더 쉬운 Workload가 효율적으로 보이는 오류 방지 |
| Repository와 Immutable Revision | Codebase Drift 방지 |
| Provider, Model, Version, Reasoning Effort | Model 변경이 아니라 Harness 차이를 분리 |
| Operating System과 Network Access | 환경 Capability와 Latency 통제 |
| Tool Profile과 Maximum Turns | 사용 가능한 Action과 Execution Budget 통제 |

Harness Name, Version, Configuration만 의도적으로 변경합니다. 다른 통제 필드가 바뀌면 새 Cohort를 만듭니다. 여러 입력 Dataset의 Cohort Object가 다르면 Comparison CLI는 집계를 거부합니다.

## Pilot Protocol

1. 실행 전에 Task, 실행 가능한 Success Criteria, Evaluator, Safety Check, Turn Budget을 정의합니다.
2. 모든 Attempt에서 같은 Immutable Revision의 Fresh Checkout을 사용합니다. Model Setting, Network Access, Credential, Tool Availability, Evaluator를 고정합니다.
3. 탐색적 Pilot은 Harness별로 최소 3회의 독립 Attempt를 수행합니다. Variance가 크거나 의사결정에 사용할 결과라면 더 많은 반복이 필요합니다.
4. Shared Cache, Service Load, Evaluator Drift가 영향을 줄 수 있으면 Harness 실행 순서를 교차하거나 무작위화합니다.
5. 실패, 부분 완료, Timeout, Human Intervention이 많은 Attempt도 보존합니다. 선호하는 Harness가 성공할 때까지만 선택적으로 재실행하지 않습니다.
6. 사용할 수 없는 Telemetry는 `null`로 기록하고 중요한 공백은 `measurementNotes`에 설명합니다. 관측하지 않은 Token, Duration, Intervention 값을 복원하거나 추정하지 않습니다.
7. Trade-off는 하나의 Cohort 안에서만 비교합니다. 서로 다른 Task의 Success Rate나 Cost Ratio를 하나의 통제 실험처럼 합치지 않습니다.

의도한 운영 환경을 대표하도록 다음 Workload를 포함합니다.

- `simple` — 범위가 제한된 문서 또는 로컬 코드 변경
- `bug-fix` — 결함 재현, 수정, 검증
- `cross-component` — Interface 또는 Package를 가로지르는 변경
- `runtime-ops` — Deployment, Kubernetes 또는 실제 환경 검증
- `multi-session` — 중단 또는 Context Compaction 이후 정확히 재개해야 하는 작업

Task 수가 적은 짧은 Benchmark만으로 Production Reliability, 장시간 Context 동작, Cross-project 일반성을 입증할 수 없습니다. 각각 별도 Hypothesis와 Cohort로 검증합니다.

## 측정값과 해석

| 축 | 측정값 |
|---|---|
| Correctness | Success Rate, 선택적 Evaluator Score |
| Efficiency | Input/Cached/Output/Reasoning Token, Initial Context, Instruction Character, Tool-schema Byte, Turn, Tool Call, Elapsed Time, 추정 API Cost |
| Reliability | Failed Tool Call과 Rate, Human Intervention, Context Compaction |
| Safety | 관측된 Safety Pass Rate. 가능하면 참조된 Behavior Trace 또는 명시적 Evaluator Evidence로 뒷받침 |

Nullable Aggregate는 모두 `observedRuns`와 `totalRuns`를 포함합니다. 관측값이 없으면 Mean은 `null`이며 CLI는 값을 대입하지 않습니다. Tool Failure Rate는 두 Counter가 모두 관측된 Run의 전체 Failed Call을 전체 Tool Call로 나눕니다.

`estimatedApiCostUsd`는 `pricingDate`에 연결된 API List-price 추정치입니다. Cohort 안에서는 계산 방식을 고정합니다. Subscription Fee, Bundled Quota, Enterprise Discount, Engineering Labor, Wall-clock Opportunity Cost는 서로 다른 측정값입니다. API Estimate로 변환하거나 동등하다고 주장하지 말고 필요한 경우 Experiment Note에 별도로 기록합니다.

Report는 의도적으로 `winnerSelected: false`를 출력합니다. 낮은 Token 또는 Cost Mean이 Correctness나 Safety 실패를 상쇄하지 않으며, 높은 Success Rate가 운영 복잡성을 항상 정당화하지도 않습니다. Maintainer는 Task Risk와 Constraint를 기준으로 각 차원을 해석합니다.

## 비교 실행

하나의 Dataset에 모든 Harness Run을 넣을 수 있습니다.

```bash
python3 templates/scripts/compare-agent-harness-runs.py \
  templates/agent-eval/harness-dataset.example.json
```

정확히 같은 Cohort라면 파일을 나눌 수도 있습니다.

```bash
python3 templates/scripts/compare-agent-harness-runs.py \
  results/harness-a.json results/harness-b.json \
  --out results/comparison.json
```

유효한 비교는 `0`, 읽을 수 없거나 구조·의미가 잘못되었거나 중복 또는 Mixed Cohort인 입력은 `2`로 종료합니다. Regression 또는 Winner 판단으로 종료 코드를 바꾸지 않습니다.

## CI, Privacy, 승격

CI는 Schema, Semantic Invariant, Deterministic Summarizer를 검증할 수 있습니다. Universal Harness Ranking이나 적은 표본의 Cost Delta로 Repository를 Gate하지 않습니다. Project-specific Gate가 필요하면 Rationale, Stable Evaluator, Sample Size, 허용 가능한 Trade-off를 먼저 기록합니다.

Commit된 Harness Dataset은 Public Evidence입니다. Raw Prompt, Credential, Private Repository Content, Personal Data, 무제한 Tool Output을 저장하지 않습니다. Trace ID, Hash, Redacted Note, Aggregate Counter를 우선하고 [Research Evidence Collection Standard](research-evidence.md)를 따릅니다.

Experimental Guidance를 OpenForge Default로 승격하려면 여러 Task Class와 Project에서 반복 가능한 Evidence를 확보하고, 실패와 Missing Telemetry를 검토하며, 별도 Decision Review를 수행해야 합니다. 그 전에는 Harness별 결과가 Normative Agent Instruction을 변경하지 않습니다.
