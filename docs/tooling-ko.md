# 개발 도구 표준

OpenForge는 반복 가능한 코드 품질, 코드베이스 이해, 개발 자동화를 위한 권장 도구를 정의합니다. 모든 프로젝트에 같은 기술 스택을 강제하는 것이 아니라 프로젝트의 언어와 특성에 맞는 규칙을 적용합니다.

## Go

`gofmt`를 직접 사용하는 대신 기본 Formatter로 `gofumpt`를 사용합니다. `gofumpt`는 Go의 기본 formatting 규칙보다 엄격한 형식 검사를 제공합니다.

```bash
gofumpt -w .
```

CI에서는 다음과 같이 formatting 위반을 검출합니다.

```bash
test -z "$(gofumpt -l .)"
```

프로젝트는 승인된 `gofumpt` 버전을 pin하거나 필요한 경우 자체 배포판을 사용할 수 있습니다. `dasomel-dev/gofumpt`는 stricter `gofumpt` fork이므로 OpenForge 기본 규칙과 구분하여 프로젝트가 명시적으로 선택한 경우 사용합니다.

권장 Go 기본 검증:

```text
gofumpt
	go vet
	staticcheck (채택 시)
	go test ./...
```

## Code Intelligence / Code Graph

중간 규모 이상의 코드베이스에서는 Code Review, Architecture 분석, AI 지원 개발에 실제 도움이 되는 경우 기계가 읽을 수 있는 Code Structure를 유지합니다.

권장 기능:

- symbol 및 dependency graph 생성
- package/module 관계 분석
- call/reference navigation
- architecture dependency 확인
- change-impact analysis

`codegraph`, `graphify`와 같은 도구는 해당 언어와 저장소에 적합한 경우 통합할 수 있습니다. 이 도구들은 Runtime dependency가 아니라 Engineering Analysis 도구로 취급합니다.

생성된 graph 데이터는 source code에서 재현 가능해야 하며 Architecture의 authoritative source가 되어서는 안 됩니다.

## AI 지원 개발

AI Coding Tool은 `AGENTS.md`, `CLAUDE.md` 또는 프로젝트별 지침 파일을 사용할 수 있습니다.

AI 지침은 다음을 만족해야 합니다.

- 저장소와 함께 version control
- 짧고 실행 가능하게 작성
- 사람을 위한 문서와 일관성 유지
- command, architecture boundary, safety constraint를 명시

AI가 생성한 변경도 사람의 변경과 동일하게 test, review, security, license 요구사항을 적용합니다.

## 일반적인 도구 선택 기준

다음 특성을 가진 도구를 우선합니다.

- CI에서 재현 가능
- 가능한 경우 Linux와 macOS 모두 지원
- Scriptable
- Open Source 또는 명확한 License
- Version pinning 가능
- Interactive session 없이 실행 가능
