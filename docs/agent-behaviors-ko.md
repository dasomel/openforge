# Agent Behavior 표준

OpenForge는 Agent 실행 지침과 장시간 작업에서 반복적으로 관찰되어야 하는 행동 기준을 분리합니다.

## 왜 Behavior를 별도 계층으로 관리하는가

장시간 동작하는 Agent는 하나의 작업에서 수십~수백 번의 판단을 수행할 수 있습니다. 최종 산출물만으로는 Agent가 증거를 확인했는지, 작업 범위를 지켰는지, 실패 후 안전하게 복구했는지, 불확실성을 적절히 처리했는지를 평가하기 어렵습니다.

OpenForge는 Agent Engineering을 다음 계층으로 봅니다.

```text
Instructions  -> 실행 중 반드시 따라야 할 규칙
Skills        -> 전문 작업을 수행하는 방법
Behaviors     -> 반복적으로 나타나야 하는 좋은 행동
Evidence      -> 판단과 완료 주장을 뒷받침하는 증거
Traces        -> 실제로 수행된 과정
Evals         -> 관찰된 행동이 기대 기준과 일치하는지 평가
CI / Policy   -> 결정론적으로 강제 가능한 규칙
```

Behavior는 모든 Runtime Prompt에 자동 주입하는 지침이 아니며, formatter·linter·test·policy로 강제할 수 있는 규칙을 중복해서 작성하는 용도도 아닙니다.

## 호환 포맷

OpenForge는 다음 이식 가능한 Agent Behavior 디렉터리 구조를 채택합니다.

```text
.agents/behaviors/<name>/BEHAVIOR.md
```

`BEHAVIOR.md`는 YAML frontmatter의 `name`, `description`을 필수로 사용하고 본문은 Markdown으로 작성합니다. 본문은 필요에 따라 Intent, Evidence, Decision, Execution, Recovery, Failure modes 관점으로 구성할 수 있습니다.

## OpenForge 기본 Behavior Profile

초기 기본 Profile은 기존 Agent Engineering 표준에서 반복적으로 강조하던 원칙을 Behavior로 분리한 것입니다.

1. `evidence-before-claim`
2. `scope-discipline`
3. `bug-fix-verification`
4. `task-convergence`
5. `trust-and-provenance`

프로젝트별 Behavior를 추가할 수 있지만, 동일한 의미의 규칙을 여러 Agent별 파일에 복제하지 않는 것을 권장합니다.

## 구조 검증 경계

저장소 로컬 검증기는 다음과 같이 실행합니다.

```bash
bash templates/scripts/validate-behaviors.sh
```

검증기는 결정론적으로 확인 가능한 구조만 검사합니다.

- `.agents/behaviors/<name>/BEHAVIOR.md` 파일 존재
- YAML frontmatter 시작/종료
- `name` 필드 존재 및 상위 디렉터리명과 일치
- `description` 필드 존재

검증기는 Behavior 내용의 품질, 유용성, 실제 Agent 준수 여부를 판단하지 않습니다. 이러한 의미적 평가는 Trace Review와 Eval 영역에서 수행합니다.

## OpenForge Compliance 연계

Agent Engineering 영역은 다음 메트릭으로 구성됩니다.

- `AGENT-001` — 간결한 Agent Root Contract
- `AGENT-002` — Runtime Instruction과 상세 Engineering Guidance의 계층 분리
- `AGENT-003` — Evidence, Reproduction, Convergence Rule
- `AGENT-004` — Agent Behavior Specification Profile

`AGENT-004`는 metric set `2026.09`에 추가된 adoption-level control입니다. 모든 저장소에 강제하지 않습니다.

Portfolio 설정에서는 다음과 같이 채택 여부를 선언할 수 있습니다.

```yaml
agent_behaviors: true   # 필수 채택. Behavior 디렉터리가 없으면 Gap
agent_behaviors: false  # 명시적으로 N/A
# 생략                  # .agents/behaviors/ 존재 여부를 자동 감지
```

설정을 생략했고 `.agents/behaviors/`가 없으면 `N/A`입니다. 디렉터리가 존재하면 그 시점부터 구조 유효성을 평가합니다.

## Canonical Portfolio Audit

`AGENT-004`는 이제 표준 감사 명령에 정식 편입되어 있습니다.

```bash
python3 templates/scripts/audit-portfolio.py --config portfolio.yml --summary-only
```

기존 `audit-agent-behaviors.py`는 이전 호출 경로를 위한 compatibility shim으로만 유지합니다.

감사 구현은 다음처럼 분리되어 있습니다.

```text
audit-portfolio.py       -> canonical entrypoint
audit-core.py            -> 안정화된 portfolio audit core
agent_behavior_metric.py -> AGENT-004와 2026.09 호환 정책
```

## Metric Set 호환성

`2026.09`는 `2026.08`에 `AGENT-004`를 추가한 additive 변경입니다. `2026.08` baseline과 비교할 경우 `additive-compatible` 상태를 반환합니다.

`AGENT-004`가 `N/A`인 프로젝트는 기존 점수와 직접 비교할 수 있습니다. Behavior Profile을 실제 채택한 프로젝트는 적용 가능한 메트릭 수가 하나 증가할 수 있으므로 점수 분모가 달라질 수 있습니다.

Audit JSON의 `metricSetChange` 필드가 이러한 변경을 명시합니다.

## 평가 원칙

Behavior 평가는 숨겨진 의도가 아니라 Trace에서 관찰 가능한 증거를 중심으로 수행해야 합니다. Human Review, Rubric 기반 Model Eval, 자동 평가를 사용할 수 있으며 OpenForge는 특정 Scorer를 강제하지 않습니다.

외부 Behavior Spec과 Tooling은 Third-party Input으로 취급합니다. 출처, License, Security 영향을 검토하고 외부 규칙이 저장소 정책을 자동으로 덮어쓰지 않도록 해야 합니다.
