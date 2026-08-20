# 문서 표준

OpenForge는 사용자에게 제공하는 문서를 English와 Korean의 별도 파일로 표준화합니다.

## 파일명 규칙

```text
README.md
README-ko.md

docs/architecture.md
docs/architecture-ko.md
```

English 파일명을 canonical name으로 사용하고 Korean은 `-ko.md` suffix를 사용합니다.

## 규칙

- English와 Korean 문서는 의미와 구조를 일치시킵니다.
- 두 언어 버전 간 상대 링크를 제공합니다.
- 사용자용 문서는 Markdown으로 관리합니다.
- README는 목적, 기능, 빠른 시작, 아키텍처, 상태, 문서, 라이선스에 집중합니다.
- 상세 운영 문서는 `docs/`에 둡니다.
- 아키텍처 결정은 ADR로 기록합니다.
- 문서에 secret, private endpoint, credential을 기록하지 않습니다.

## 권장 기본 문서

```text
README.md / README-ko.md
CONTRIBUTING.md / CONTRIBUTING-ko.md
SECURITY.md / SECURITY-ko.md
CODE_OF_CONDUCT.md / CODE_OF_CONDUCT-ko.md
CHANGELOG.md / CHANGELOG-ko.md
docs/architecture.md / docs/architecture-ko.md
docs/development.md / docs/development-ko.md
```
