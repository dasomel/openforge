# OpenForge Engineering Operating Model

OpenForge는 repository를 단순한 source 저장소가 아니라 **engineering execution context**로 취급합니다.

> OpenForge는 engineering intent를 재현 가능하고, 테스트 가능하고, 리뷰 가능하고, 복구 가능한 시스템으로 전환합니다.

이 문서는 상위 운영모델입니다. Agent Engineering, Agent Execution Security, Documentation Freshness, Portfolio, Release, Supply-chain 표준을 대체하지 않고 하나의 lifecycle로 어떻게 조합되는지를 설명합니다.

## Lifecycle

```text
Intent
  -> Constraints
  -> Repository Context / Instructions
  -> Human or Agent Implementation
  -> Executable Checks
  -> Evidence
  -> Human Review / Stewardship
  -> Release / Rollback
  -> Observe
  -> Learning Loop
```

코드가 생성되거나 merge되었다는 사실만으로 변경은 완료되지 않습니다. 관련 경계에서 의도한 동작이 존재하고, 필요한 검증이 통과하며, evidence가 남고, release/recovery 영향이 이해된 상태가 완료입니다.

## 1. Intent as specification

실질적인 작업은 구현에 영향을 주는 범위에서 다음을 명시해야 합니다.

- goal과 사용자/시스템 가치
- scope와 non-goals
- constraints와 금지 변경
- acceptance criteria
- risks와 failure mode
- verification/evidence class
- release/rollback 영향

Issue, ADR, spec 또는 간결한 작업 지침이 이를 담을 수 있습니다. 형식보다 중요한 것은 중요한 의도를 구현자나 agent가 추측하지 않도록 review 가능한 형태로 만드는 것입니다.

## 2. Constraints as policy

제약은 검증 가능성에 따라 세 계층으로 나눕니다.

- **Declarative:** architecture, contribution, security, compatibility, operations guidance
- **Executable:** lint, test, schema validation, policy-as-code, dependency/supply-chain check, CI gate
- **Judgment:** architecture coherence, user value, maintainability, community fit, usability, ethical/organizational impact

객관적으로 검증 가능한 규칙은 신뢰성 있게 구현 가능할 때 executable check로 이동합니다. 반대로 판단 영역을 자동화하기 어렵다는 이유로 false-green 검사로 바꾸지 않습니다.

## 3. Repository context and instructions

`AGENTS.md`는 human과 agent 모두를 위한 repository-level engineering contract입니다. 모든 스타일 규칙을 복제하지 않고 관련 source-of-truth 문서를 연결하면서 간결하게 유지합니다.

Instruction hierarchy는 다음을 답해야 합니다.

- 시스템이 무엇이며 무엇이 아닌가
- 어떤 경계가 high risk인가
- generated state의 source가 무엇인가
- canonical build/test/verification entrypoint가 무엇인가
- completion claim 전에 어떤 evidence가 필요한가
- 언제 중단하고 escalation하는 것이 올바른가

세부 규칙은 `agent-engineering.md`와 executable audit model을 따릅니다.

## 4. Implementation is not authority

AI agent, automation 또는 human contributor가 변경을 만들 수 있어도 governance authority가 자동으로 이전되지는 않습니다.

Tool이 host, cluster, identity, data 또는 external system에 side effect를 만들 수 있다면 repository instruction은 authorization boundary가 아닙니다. Agent Execution Security Contract에 따라 concrete invocation을 한 번 resolve하고, validate/authorize하고, authority를 attenuate하고, 필요한 approval을 exact invocation에 bind하고, runtime에서 enforce하며, post-state를 검증하고 recomputable evidence를 남깁니다.

## 5. Rules as executable checks

문서 규칙이 객관적으로 기계 검증 가능하다면 가능한 경우 executable owner를 가져야 합니다.

```text
"release에 SBOM이 있어야 함"
        -> release artifact validation

"generated files는 source와 동기화"
        -> regeneration + git diff gate

"portfolio 상태는 canonical source에서 생성"
        -> schema validation + deterministic dashboard generation

"high-risk agent behavior는 evidence 필요"
        -> behavior/eval gate
```

Rule registry와 agent audit은 prose 규칙을 실제 enforcement로 오해하는 false-green을 방지합니다.

## 6. Evidence over claims

"tests passed", "implemented" 같은 문장은 evidence 자체가 아니라 evidence에 대한 metadata입니다.

Evidence class를 구분합니다.

- unit/stub/mock
- integration
- real runtime / cluster / filesystem / browser / identity-provider / hardware
- static analysis / policy
- build/package
- SBOM/provenance/signature
- post-state verification

낮은 evidence class로 더 강한 runtime property를 주장하지 않습니다. Mocked command runner는 argv 구성을 증명할 수 있지만 실제 kernel quota enforcement를 증명하지 못합니다.

## 7. Human stewardship

Human responsibility는 모든 코드를 직접 작성하는 것에서 다음 경계를 책임지는 쪽으로 확장됩니다.

- architecture와 product direction
- permission/risk boundary
- trade-off와 exception
- evidence sufficiency
- release decision
- rollback/recovery readiness
- maintainability와 community quality

Automation은 반복 작업을 줄이되 accountable review를 제거하지 않습니다.

## 8. Failure is a first-class design object

주요 workflow는 필요한 경우 다음을 정의합니다.

- explicit failure conditions
- partial/indeterminate outcome
- timeout/retry
- idempotency/deduplication
- retained failure evidence
- rollback/recovery path
- manual intervention point

Agentic workflow에서 side effect가 일부 발생한 상태는 success나 clean failure와 동일하지 않으므로 명시적으로 표현해야 합니다.

## 9. Release and rollback

단순히 자동화 가능한 것보다 재현 가능하고 되돌릴 수 있는 자동화를 우선합니다.

- versioned source/dependency
- pinned 또는 recorded build inputs
- 가능한 경우 immutable artifact
- release provenance
- migration compatibility
- rollback 또는 forward-recovery plan
- rollout 이후 verification

## 10. Documentation and learning loop

사용자, architecture, operations, security, compatibility 또는 공개 capability claim에 영향을 주는 구현 변경은 Documentation Freshness review를 통과해야 합니다.

Operational finding, incident, benchmark, contributor feedback, adoption 결과는 다음 intent와 standard에 반영됩니다. 이 loop는 human-governed입니다. OpenForge가 observation이나 proposal을 생성할 수 있어도 project goal을 자율적으로 재정의하지 않습니다.

## Maturity model

| Level | 의미 | 최소 강조점 |
|---|---|---|
| 0 | Repository | source, README, license |
| 1 | Structured Project | contribution/security docs, basic CI |
| 2 | Automated Engineering | build/test/lint/security/release automation |
| 3 | Agent-Ready Repository | concise instructions, explicit boundaries, deterministic entrypoints |
| 4 | Evidence-Driven Engineering | provenance, runtime evidence, rollback/recovery, executable governance |
| 5 | Human-Governed Learning System | operational feedback와 improvement proposal을 standards와 연결 |

Level 5는 autonomous repository를 의미하지 않습니다. Human stewardship와 approval boundary는 계속 authoritative합니다.

## 현재 OpenForge control과의 관계

- `agent-engineering.md` — repository instruction / convergence contract
- `agent-execution-security.md` — tool/side-effect authorization / evidence
- `agent-behaviors.md` — executable behavior evaluation
- `documentation-freshness.md` — implementation-to-documentation claim integrity
- portfolio registry/dashboard — cross-project state/evidence
- reproducible-build / supply-chain standards — build/release integrity
- ADR — durable architecture decision

따라서 Engineering Operating Model은 새로운 병렬 프레임워크가 아니라 이미 구현된 OpenForge control의 **composition rule**입니다.