# OpenForge

> 오픈소스 프로젝트 Blueprint & Engineering Standards

OpenForge는 품질과 운영 방식을 일관되게 유지하면서 오픈소스 프로젝트를 만들고 운영하기 위한
재사용 가능한 Blueprint와 Engineering Standard입니다.

저장소 구조, 문서, GitHub 운영, CI/CD, 보안, 릴리스, 다국어, 개발 도구, 프로젝트 생명주기까지 공통 기준으로 관리합니다.

## 문서 정책

사용자에게 제공하는 Markdown은 항상 English와 Korean을 별도 파일로 관리합니다.

```text
English: <name>.md
Korean:  <name>-ko.md
```

`README_ko.md`, `README.ko.md`, `_ko.md` 규칙은 사용하지 않습니다.

## 표준 영역

- Documentation
- Repository
- GitHub
- Development
- Engineering Tooling
- Security
- CI/CD
- Release
- Internationalization
- OSS Compliance
- Project Templates

## 개발 도구 예시

- Go Formatter: `gofumpt`
- Code Intelligence: `codegraph`, `graphify` 또는 프로젝트에 적합한 동등 도구
- AI 개발 지침: `AGENTS.md`, `CLAUDE.md` 등 version-controlled instruction

자세한 내용은 [Engineering Tooling Standard](docs/tooling-ko.md)를 참고합니다.

## License

Apache License 2.0. See [LICENSE](LICENSE).
