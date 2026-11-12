# Agent 작업을 위한 엔지니어링 판단 기준

상태: 사람의 판단을 돕는 가이드입니다. 스크립트, 테스트, CI로 강제되지 않으며 **측정된 효과가 아직 없습니다.** 검토를 거친 출발점일 뿐, 이를 따르면 Agent가 더 잘 동작한다는 증거가 아닙니다. 효과를 측정한다면 [Research Evidence](research-evidence-ko.md)를 따라야 합니다.

이 문서는 Agent 보조 엔지니어링을 위한 아홉 가지 판단 습관을 정리합니다. 기존 OpenForge 표준을 보완할 뿐 반복하지 않습니다. 이미 표준이나 Behavior가 소유한 규칙은 링크로 연결합니다. [AGENTS.md](../AGENTS.md)에 따라, 여기 있는 내용 중 안정적으로 강제할 수 있는 것은 산문을 늘리지 말고 스크립트, 테스트, CI로 옮깁니다(원칙 4 참조).

## 출처

이 원칙들은 Lauren Tan(`poteto`)의 pstack Skill 모음(<https://github.com/cursor/plugins/tree/main/pstack>, MIT License, Copyright (c) 2026 Lauren Tan)을 정리한 것입니다. 참고한 pstack 버전은 0.15.36입니다. 문장은 OpenForge의 표현으로 새로 작성했고 pstack 원문은 옮기지 않았으므로 MIT 고지를 이 문서에 함께 싣지는 않지만, 출처는 여기에 명시합니다. OpenForge 적용은 메인테이너가 2026-11-13에 수행했습니다.

## 사용 방법

작업이 실제로 관련되는 원칙만 적용합니다. 대부분의 작업은 두세 가지에 해당합니다. 각 항목에 적용 시점과 기존 표준과의 관계를 적었습니다.

## 아홉 가지 원칙

### 1. 최소 변경, 뺄셈 먼저
목표를 충족하는 가장 작은 변경을 정하고, 추가하기 전에 불필요한 것부터 제거합니다. 요구사항을 넘는 추측성 방어 코드, 계층, 추상화를 만들지 않습니다. 요청된 변경이 불필요하다는 증거가 나오면 증거를 보이고 멈춥니다.
- 적용: 모든 수정, 특히 첫 아이디어가 코드를 늘릴 때.
- 관계: [`scope-discipline`](../.agents/behaviors/scope-discipline/BEHAVIOR.md)과 [AGENTS.md](../AGENTS.md)의 "smallest coherent change" 규칙. 여기서는 "변경 없음"이라는 결론을 명시적으로 허용합니다.

### 2. 증상이 아닌 근본 원인
먼저 재현하고, 시스템이 처음 잘못된 지점을 고치며, 같은 결함의 다른 사례를 찾습니다. 방어 코드, 재시도, clamp, 삼켜진 오류는 그것이 처리하는 상태가 정당할 때만 수정으로 인정됩니다.
- 적용: 버그 수정, 불안정한 동작.
- 관계: [`bug-fix-verification`](../.agents/behaviors/bug-fix-verification/BEHAVIOR.md)(재현, 최소 수정, 회귀 증거). 새로운 점은 동일 결함의 다른 사례를 훑는 것입니다.

### 3. 전제를 공격하라
같은 가정을 공유하는 수정이 두 번 실패하면, 세 번째 시도 전에 그 가정을 적어 두고 직접 검증합니다.
- 적용: 한 문제에서 반복되는 실패.
- 관계: 맹목적 재시도 대신 증거 기반 중단을 요구하는 [`task-convergence`](../.agents/behaviors/task-convergence/BEHAVIOR.md).

### 4. 레버를 만들어라
사소하지 않거나 반복되는 작업은 그 일을 수행하거나 증명하는 재실행 가능한 스크립트, codemod, 검사를 작성합니다. 두 번 쓴 교훈은 산문이 아니라 lint, 검사, 스크립트가 되어야 합니다.
- 적용: 반복 편집, 리뷰어가 다시 돌려보고 싶은 모든 것.
- 관계: [AGENTS.md](../AGENTS.md)와 [Model-Agnostic Agent Instruction Design](model-agnostic-agent-instructions.md)의 선언적 표준 / 실행 가능한 검사 / 판단 분리, [`instruction-debt-audit`](../.agents/behaviors/instruction-debt-audit/BEHAVIOR.md).

### 5. 검증 가능한 단위
각 단계가 검사로 끝나는 작은 단계로 일하고, 하나를 검증한 뒤 다음으로 넘어갑니다. 실패하는 테스트 먼저, 그다음 수정.
- 적용: 여러 단계로 된 변경.
- 관계: [`evidence-before-claim`](../.agents/behaviors/evidence-before-claim/BEHAVIOR.md), `bug-fix-verification`.

### 6. 구현이 아닌 동작을 테스트하라
테스트는 동작이 깨질 때 실패하고 리팩터링에는 살아남아야 합니다. 기대값은 요구사항에서 가져오며, 테스트 대상 코드를 실행해서 얻지 않습니다.
- 적용: 테스트 작성과 리뷰.
- 관계: `bug-fix-verification`. 구현에서 기대값을 도출하는 것을 금지하는 기존 표준은 없었고, 이 문서가 금지합니다.

### 7. 숫자를 설명하라
측정값을 신뢰하거나 보고하기 전에, 어떤 결과가 결정을 바꾸는지, 실행 횟수와 산포, 값을 제한하는 요인, 그 값이 다른 무엇을 측정하고 있을 수 있는지(오류, 캐시되거나 건너뛴 작업, 실행되지 않은 코드)를 밝힙니다.
- 적용: 벤치마크, 커버리지, 시간, 통과율.
- 관계: OpenForge 측정 기록 방식을 소유하는 [Research Evidence](research-evidence-ko.md). 이 원칙은 보고 전 점검입니다.

### 8. 공유 상태: 직렬화 전에 분리하고, 연산은 멱등하게
동시에 도는 Lane은 각자 파일, 브랜치, 키를 가지며 읽기 경계에서 병합합니다. 쓰기 대상이 정말 하나여야 할 때만 직렬화합니다. 연산은 재실행하거나 중단 후 재개해도 수렴해야 합니다.
- 적용: 병렬 Agent, 마이그레이션, 재시도되는 CI/릴리스 단계.
- 관계: 현재 이를 전담하는 OpenForge 표준은 없습니다. 가장 가까운 맥락은 [Change Management](change-management-ko.md)와 [CI/CD Resilience](ci-resilience-ko.md)입니다.

### 9. 솔직함
"아니오", "이것은 존재할 가치가 없다"도 유효한 답입니다. 동의가 기본값이 아닙니다.
- 적용: 리뷰, 계획 피드백, 전제가 잘못돼 보이는 요청.
- 관계: 취지상 `evidence-before-claim`, [`trust-and-provenance`](../.agents/behaviors/trust-and-provenance/BEHAVIOR.md). 반론을 명시적으로 다루는 Behavior는 없습니다.

## 증거 보강

`evidence-before-claim`과 `trust-and-provenance`를 보완하는 세 가지입니다.

- **대리 지표가 아닌 실제 산출물.** 파일 mtime, Worker의 자기 보고, 캐시된 출력이 아니라 대상 자체를 확인합니다. 검사가 실패하면 시스템보다 관찰 방법을 먼저 의심합니다.
- **주장에 라벨을 붙여라.** 같은 문장 안에서 측정됨, 추론됨, 추측 중 무엇인지 밝힙니다.
- **읽지 않은 것은 인용하지 않는다.** 이번 세션에서 읽거나 만들지 않은 링크나 참조는 인용하지 않으며, 직접 실행할 수 있는 검사를 남에게 넘기지 않습니다.

## Orchestrator 가이드

Worker Agent에게 위임하는 세션을 위한 관행이며, 모든 저장소에 대한 요구사항은 아닙니다.

- 모든 Worker 브리프에 사용자의 목표를 다시 적습니다. Orchestrator가 각 Worker 산출물의 책임을 지며, diff나 증거를 검토하고 직접 요약합니다. Worker의 "완료"를 그대로 전달하지 않습니다.
- 새 라운드(수정, 재시도, 후속)는 통합된 범위(원래 브리프, 이후 지시, 이전 보고, 브랜치)와 함께 새 Worker에게 보냅니다. 체크아웃이나 실행 중 프로세스처럼 상태가 Worker 안에 있을 때만 기존 Worker를 재개합니다.
- 결정적 스크립트가 fan-out보다 낫습니다. fan-out 시에는 모든 Lane에 쓰기 범위 밖의 공유 레시피와 검증 계약 파일 하나를 줍니다.
- 두 번째 의견은 같은 프롬프트를 다른 벤더에 보내는 것이며, 일치는 신호가 강합니다.
- 사용자에게 묻기 전에 갈림길을 분류합니다. 실행해서 관찰할 수 있는 사실은 사용자가 답할 일이 아니므로 직접 실행합니다. 되돌릴 수 있는 작업은 진행하고 보고합니다. 어떤 실험으로도 정할 수 없는 제품/선호 판단이나 되돌릴 수 없는 외부 영향 작업 전에만 묻습니다.

## 해결된 하나의 충돌

원칙 2는 clamp가 버그를 가릴 수 있다고 경고하지만, 외부 입력을 불신하라는 일반적 습관은 신뢰할 수 없는 값을 clamp하라고 합니다. 해결: **시스템 경계(외부 입력, 변조된 데이터)에서 검증하고 clamp하며, 그 안쪽에서는 내부 타입을 신뢰합니다.** 내부 깊은 곳의 clamp는 결함을 가리는 것으로 의심하고, 정당한 상태가 있을 때만 정당화합니다. 경계 사례(정상, 매핑됨, 없음, 변조됨)는 여전히 테스트합니다.

## 의도적으로 채택하지 않은 것

- **특정 벤더나 등급으로의 모델 라우팅.** OpenForge는 모델 비종속을 유지합니다([Model-Agnostic Agent Instruction Design](model-agnostic-agent-instructions.md) 참조).
- **Cursor 전용 기능**(플러그인 명령, Agent, 설정 흐름). 도구별 어댑터 영역이지 포트폴리오 표준이 아닙니다.
- **영어 산문 스타일 규칙.** OpenForge 문서는 이중 언어이며 스타일은 [Documentation Standard](documentation.md)가 정합니다.
- **23개 Playbook.** 작업 워크플로는 좁게 트리거되는 Skill([Agent Skills](agent-skills-ko.md))에 두고, 반복되는 필요가 확인될 때 추가합니다.
- **묻지 않고 커밋하거나 외부 작업을 수행하는 자율성.** OpenForge의 권한 경계([Agent Execution Security Contract](agent-execution-security-ko.md), [Agent Engineering Standard](agent-engineering-ko.md))와 충돌합니다. 커밋, 푸시, 외부 영향 작업은 명시적 승인이 계속 필요하며, 위의 "갈림길 분류"는 되돌릴 수 있는 로컬 작업에만 적용됩니다.

## 포함하지 않은 것

이 문서와 함께 강제 검사, 새 `.agents/behaviors/` 항목, `templates/` 변경은 없습니다. 가치가 입증되면 승격 후보는 현재 소유자가 없는 원칙 9 또는 8의 Behavior, 원칙 6의 테스트 품질 lint입니다.
