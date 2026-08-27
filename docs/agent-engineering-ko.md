# Agent Engineering 표준

OpenForge는 Repository Instruction을 모든 코딩 취향을 넣는 파일이 아니라 **Agent와 사람이 공유하는 Engineering Control**로 봅니다.

## 계층 구조

```text
AGENTS.md
  -> 짧은 실행 계약
  -> 범위, 경계, 검증, 중단/에스컬레이션

CODING_STANDARDS.md
  -> 상세 코딩/리뷰 가이드

CONTRIBUTING.md / DESIGN.md / Architecture 문서
  -> 프로젝트별 프로세스와 설계 문맥

formatter / linter / test / policy-as-code / CI
  -> 결정적으로 검사 가능한 규칙
```

`AGENTS.md`는 긴 세션에서도 중요한 규칙이 묻히지 않도록 짧게 유지합니다. Tooling이 안정적으로 검사할 수 있는 규칙은 Prompt에 중복하지 않습니다.

## AGENTS.md에 둘 내용

- 수정 전에 읽어야 할 Source of Truth
- 허용/금지 범위
- Architecture/Access Boundary
- Canonical Build/Test/Verification 진입점
- Bug 재현 정책
- 완료라고 말하기 전에 필요한 Evidence
- 중단/에스컬레이션 조건
- 코드만 보고 알기 어려운 프로젝트 고유 High-risk Path

## 변경 범위

요청을 해결하는 **가장 작은 일관된 변경(smallest coherent change)**을 만듭니다.

- 관련 없는 문제는 자동 수정하지 않고 별도로 보고합니다.
- 단순히 변경 Line 수를 줄이기 위해 중복 API나 Wrapper를 늘리지 않습니다.
- 기존 Layer/Architecture Boundary를 유지합니다.
- `private -> internal/public`, Exported API 추가, RBAC/Permission 확대, Destructive Behavior 변경은 Design Change로 취급합니다.

## 코드 가이드

상세 규칙은 `CODING_STANDARDS.md`나 Language Tooling에 둡니다.

- Early Return은 Nesting을 줄이고 가독성을 높일 때 사용합니다.
- 의미 있는 상태는 Boolean Flag보다 Domain Enum/Type을 우선합니다.
- 반복되거나 의미가 있거나 명세에 정의된 Magic Value는 Named Constant/Type으로 만듭니다.
- 단순한 일회성 값은 불필요한 추상화를 피하기 위해 Inline으로 둘 수 있습니다.
- 주석은 **왜 필요한지**, Invariant, Hazard, Compatibility Constraint, Trade-off를 설명합니다. 자명한 코드를 그대로 설명하지 않습니다.
- Example/ASCII Diagram은 실제 이해를 높일 때만 사용합니다.
- Hardware/FileSystem/Socket/Storage/Protocol/DB 세부 구현은 적절한 추상화 경계 안에 둡니다.
- 임의의 전역 함수명 길이 제한보다 프로젝트 Naming Convention을 우선합니다.

## Bug Fix

권장 순서:

```text
재현
  -> 실패하는 Regression Test 또는 실행 가능한 Evidence
  -> 최소 수정
  -> 동일 Test/Evidence 성공
  -> 관련 Regression Suite
```

자동 Test가 현실적으로 불가능하면 재현 가능한 절차와 자동화가 어려운 이유를 기록합니다.

## Evidence

완료 선언은 Evidence가 아닙니다. 실제로 실행한 검사와 범위를 명시합니다.

다음을 구분합니다.

- Unit/Stub/Mock Test
- Integration Test
- 실제 Runtime/Cluster/Device/FileSystem 검증
- Static Analysis/Lint
- Security/Policy Check
- Build/Package Verification

낮은 수준의 Evidence가 더 높은 수준의 Runtime 속성을 증명한다고 과장하지 않습니다.

## 수렴 상태

실질적인 작업은 다음 중 하나로 끝납니다.

- **A — Complete**: 실제 대상 경로에서 의도한 기능이 동작하고 적절한 검증을 통과함
- **B — Meaningful Progress**: 아직 완료되지 않았지만 하나의 검증된 Blocker를 제거하고 다음 Blocker를 Evidence와 함께 분리함
- **C — Stop**: 더 진행하려면 부당한 Scope 확대, 취약한 Patch, 근거 없는 가정 또는 허용하기 어려운 위험이 필요하므로 근거와 함께 중단함

활동량을 Progress로 착각하지 않습니다. 실패한 시도는 문제를 좁히거나 Evidence를 강화하거나 중단 근거를 만들어야 합니다.

## Context Dilution 대응

- Root Instruction은 짧게 유지합니다.
- 상세 표준은 필요할 때 읽는 별도 문서에 둡니다.
- 서로 무관한 기능은 가능하면 새 Session에서 시작합니다.
- 긴 조사 뒤 지침 준수도가 떨어지면 Repository Instruction을 다시 읽습니다.
- Formatter/Linter가 검사하는 규칙을 Prompt에 중복하지 않습니다.

## Agent별 파일

`CLAUDE.md`, `GEMINI.md`, Tool별 Rule은 `AGENTS.md`와 함께 존재할 수 있습니다.

Tool별 동작이나 프로젝트 고유 Gotcha에 사용하고, 일반적인 Engineering Rule을 여러 파일에 복제하지 않습니다. 이미 가치 있는 Gotcha/실패 이력 문서는 Generic Template으로 덮어쓰지 않고 참조합니다.
