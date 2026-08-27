# OpenForge 성숙도 진단

OpenForge Maturity Assessment는 OSS 프로젝트와 플랫폼의 Engineering Maturity를 **재현 가능한 규칙과 증거**를 기반으로 측정하는 진단 기능입니다.

핵심 원칙은 진단 결과가 특정 AI 모델, 외부 SaaS 또는 주관적 평가에 의존하지 않는 것입니다. 점수와 PASS/FAIL 판정은 Rust 기반 OpenForge CLI가 직접 수행하며, 동일한 입력과 동일한 ruleset에서는 동일한 결과를 생성해야 합니다.

## 목표

- 문서 체크리스트가 아니라 실제 repository/configuration evidence를 코드로 검사합니다.
- 결과를 0~100 점수, Grade, Maturity Level, category score와 rule별 evidence로 제공합니다.
- 규칙은 versioned ruleset으로 관리합니다.
- CI에서 `--fail-under`를 이용해 품질 저하를 감지할 수 있습니다.
- 향후 repository static evidence에서 execution evidence, Kubernetes/runtime evidence로 확장합니다.
- AI는 선택 사항이며 **진단 자체가 아니라 진단 결과 분석**에만 사용합니다.

## 기본 실행

```bash
openforge .
```

JSON 결과:

```bash
openforge . --format json --output openforge-assessment.json
```

CI threshold:

```bash
openforge . --fail-under 70
```

## 진단 계층

### L1 — Repository Evidence

현재 MVP의 기본 범위입니다.

- README / CONTRIBUTING / CHANGELOG
- SECURITY / dependency update policy / security scan
- GitHub workflow / test / lint
- release automation / versioning policy
- Kubernetes packaging
- probes
- resource requests/limits
- NetworkPolicy
- PodDisruptionBudget
- observability configuration

### L2 — Execution Evidence

향후 단계에서는 선언이 존재하는지만 확인하지 않고 실제 실행 결과를 증거로 사용합니다.

예:

- build
- unit/integration test
- lint/static analysis
- Helm render
- Kubernetes manifest validation
- SBOM generation
- dependency/container vulnerability scan
- reproducibility checks

### L3 — Runtime Evidence

클러스터 접근이 허용된 경우 실제 runtime 상태를 진단합니다.

예:

- workload availability
- probes and restart behavior
- RBAC
- NetworkPolicy effective behavior
- resource pressure
- storage and backup/restore
- certificate expiry
- observability coverage
- GitOps drift
- deprecated Kubernetes APIs
- high availability / disruption tolerance

Repository score와 Runtime score는 혼합하지 않고 필요 시 별도 dimension으로 표시합니다.

## 점수와 Level

초기 기준은 다음과 같습니다.

| Score | Grade | Level |
| ---: | :---: | --- |
| 90-100 | A | L5 Optimizing |
| 80-89.9 | B | L4 Resilient |
| 70-79.9 | C | L3 Production |
| 55-69.9 | D/E | L2 Managed |
| 35-54.9 | E | L1 Repeatable |
| 0-34.9 | E | L0 Initial |

이 Level은 certification이 아니라 OpenForge ruleset이 관찰한 engineering evidence의 상태를 나타냅니다.

## Evidence-first 원칙

단순히 특정 파일 이름이 존재한다는 이유만으로 높은 성숙도를 부여하지 않는 방향으로 발전시킵니다.

예를 들어:

```text
SECURITY.md exists
```

는 security policy의 존재 evidence일 뿐 실제 vulnerability handling capability 전체를 의미하지 않습니다.

향후 rule은 가능하면 다음 순서로 강한 evidence를 사용합니다.

```text
Declared < Configured < Executed < Runtime Verified
```

따라서 같은 control도 실행 또는 runtime evidence가 추가되면 더 높은 신뢰도로 평가할 수 있도록 rule model을 확장합니다.

## AI-assisted Result Analysis

AI는 OpenForge의 필수 구성요소가 아닙니다.

OpenForge CLI가 먼저 deterministic assessment를 완료합니다.

```text
Repository / Runtime
        ↓
OpenForge Rust Scanner
        ↓
Evidence + Rule Engine
        ↓
Deterministic Score
        ↓
openforge-assessment.json
        ↓ optional
AI-assisted Result Analysis
```

AI는 다음 작업만 수행합니다.

- 진단 결과 의미 설명
- 중요한 FAIL의 영향 분석
- 개선 우선순위 제안
- 추가 검증 항목 제안
- false positive / applicability 가능성 검토
- 이전 결과와 비교한 trend 해석
- OpenForge rule 자체의 개선점 제안

AI는 다음 작업을 수행하지 않습니다.

- 점수 변경
- PASS/FAIL 변경
- evidence 생성 또는 조작
- 별도의 AI maturity score 생성

Provider-neutral prompt는 [`../prompts/detailed-assessment.md`](../prompts/detailed-assessment.md)에 제공합니다.

향후 CLI에서 다음과 같은 연결을 지원할 수 있습니다.

```bash
openforge analyze openforge-assessment.json --provider openai
openforge analyze openforge-assessment.json --provider anthropic
openforge analyze openforge-assessment.json --provider gemini
openforge analyze openforge-assessment.json --provider ollama
```

Provider integration은 optional feature로 유지하며, 기본 `openforge assess` 실행에는 네트워크나 API key가 필요하지 않도록 합니다.

## 프로젝트 Archetype과 Applicability

모든 프로젝트에 동일한 rule을 강제하면 잘못된 점수가 발생할 수 있습니다.

예를 들어 library에 Kubernetes PDB를 요구하거나 desktop application에 NetworkPolicy를 요구하는 것은 적절하지 않습니다.

향후 ruleset은 다음 profile을 지원하는 방향으로 확장합니다.

- generic OSS
- library / SDK
- CLI / developer tool
- desktop application
- web service
- Kubernetes operator/controller
- platform portal
- infrastructure / IaC
- data/AI platform

프로필에 따라 적용 가능한 rule을 선택하고 명시적인 waiver/exception도 machine-readable하게 관리하는 것을 목표로 합니다.

## 출력 형식

기본:

- terminal text
- JSON

향후:

- SARIF
- Markdown
- HTML
- GitHub Job Summary

모든 출력은 동일한 assessment model에서 파생되어야 하며 format에 따라 점수가 달라져서는 안 됩니다.

## 비목표

OpenForge Maturity Assessment는 다음을 목표로 하지 않습니다.

- 공식 인증 또는 보증
- 프로젝트 간 단순 순위 경쟁
- 특정 vendor 제품 채택 유도
- AI가 만든 주관적 점수
- 파일을 추가하는 것만으로 점수를 올리는 checklist gaming

목표는 프로젝트의 현재 engineering 상태를 반복 가능하게 관찰하고, 개선 전후의 변화를 evidence로 확인할 수 있게 만드는 것입니다.
