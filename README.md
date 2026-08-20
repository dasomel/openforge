# OpenForge

> Open Source Project Blueprint & Engineering Standards

OpenForge is a reusable blueprint for creating and maintaining high-quality open-source projects.
It defines repository structure, documentation, GitHub practices, CI/CD, security, release management,
localization, engineering tooling, and project lifecycle standards.

## 한국어

OpenForge는 품질과 운영 방식을 일관되게 유지하면서 오픈소스 프로젝트를 만들고 운영하기 위한
재사용 가능한 Blueprint와 Engineering Standard를 제공합니다.

저장소 구조, 문서, GitHub 운영, CI/CD, 보안, 릴리스, 다국어, 개발 도구, 프로젝트 생명주기까지 공통 기준으로 관리합니다.

## Core Principles / 핵심 원칙

- English is the canonical project language; Korean is a first-class translation.
- User-facing Markdown follows `<name>.md` and `<name>-ko.md`.
- Open-source projects should be reproducible, documented, testable, and secure by default.
- GitHub Issues and Pull Requests are the primary change-management mechanism.
- Architecture decisions are recorded as ADRs.
- CI validates quality before changes are merged.
- Localization is designed from the beginning rather than retrofitted later.
- Development tooling is standardized where it improves consistency and reproducibility.
- Secrets and credentials are never committed to source control.

## Standards / 표준

- [Documentation Standard](docs/documentation.md)
- [Repository Standard](docs/repository.md)
- [GitHub Standard](docs/github.md)
- [Development Standard](docs/development.md)
- [Engineering Tooling Standard](docs/tooling.md)
- [Security Standard](docs/security.md)
- [CI/CD Standard](docs/ci-cd.md)
- [Release Standard](docs/release.md)
- [Internationalization Standard](docs/i18n.md)
- [OSS Compliance Standard](docs/oss-compliance.md)

## Tooling Examples / 개발 도구 예시

- Go formatting: `gofumpt` instead of direct `gofmt` usage
- Code intelligence: `codegraph`, `graphify`, or an equivalent tool when appropriate
- AI-assisted development: versioned repository guidance such as `AGENTS.md` or `CLAUDE.md`

## Templates / 템플릿

Reusable GitHub and project templates are provided under [`templates/`](templates/).

## Project Lifecycle / 프로젝트 생명주기

```text
Idea
  ↓
Project Definition
  ↓
Repository Bootstrap
  ↓
Documentation + Architecture
  ↓
Implementation
  ↓
CI / Security / Testing
  ↓
Release
  ↓
Maintenance
```

## License / 라이선스

Apache License 2.0. See [LICENSE](LICENSE).
