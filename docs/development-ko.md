# 개발 표준

프로젝트의 구현 변경은 작고 테스트 가능하며 리뷰 가능한 형태로 유지합니다.

## 아키텍처

- 구현 전에 책임 경계를 정의합니다.
- 중요한 결정은 ADR로 기록합니다.
- UI에 종속된 API보다 안정적인 Domain Model을 우선합니다.
- 외부 컴포넌트와의 불필요한 결합을 피합니다.
- Architecture 정보는 source code와 configuration으로 재현 가능하게 유지합니다.

## 코드 품질

- 언어별 formatter를 로컬 개발과 CI에서 일관되게 적용합니다.
- Go 프로젝트에서는 `gofmt`를 직접 사용하기보다 `gofumpt`를 기본 formatter로 사용합니다.
- 언어에 맞는 static analysis 도구를 적용합니다.
- formatting, linting, testing, build를 CI에서 재현 가능하게 유지합니다.
- 생성 코드와 생성 분석 artifact는 파생 산출물로 취급합니다.

선호 도구와 적용 예시는 [Engineering Tooling Standard](tooling.md)를 참고합니다.

## Code Intelligence

중간 규모 이상의 저장소에서는 Architecture 이해, Review, Change-impact 분석에 도움이 되는 경우 Code Graph 또는 Code Intelligence 도구를 사용합니다. 예를 들어 프로젝트 기술 스택에 맞는 경우 `codegraph`, `graphify`를 사용할 수 있습니다.

생성된 Graph는 재현 가능해야 하며 source code나 ADR을 대신하는 authoritative Architecture 기록이 되어서는 안 됩니다.

## 테스트

적절한 최소 테스트 수준을 선택하고 핵심 사용자 흐름에는 End-to-End 테스트를 추가합니다.

```text
Unit → Component → Integration → E2E
```

## 설정

- 환경별 설정을 명시적으로 관리합니다.
- secret이 아닌 안전한 예제만 저장소에 등록합니다.
- 필수 설정이 없을 경우 명확하게 실패합니다.

## Dependency

- 핵심 dependency는 버전을 고정하거나 범위를 제한합니다.
- dependency 업데이트를 검토합니다.
- 사용하지 않는 dependency는 제거합니다.

## 다국어

다국어 애플리케이션의 사용자 노출 문자열은 translation key를 사용합니다.
API와 Domain 객체는 특정 locale에 종속되지 않도록 합니다.
