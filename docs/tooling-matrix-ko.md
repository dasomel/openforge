# 개발 도구 매트릭스

이 표는 OpenForge의 기본 도구를 정의합니다. 프로젝트의 언어, Framework, 운영 제약에 따라 다른 도구를 선택할 수 있으며, 중요한 예외는 ADR로 기록합니다.

| 영역 | 기본 권장 | 최소 CI 검사 |
|---|---|---|
| Go | `gofumpt`, `go vet`, `go test`; 필요 시 `staticcheck` | format + vet + test |
| TypeScript / JavaScript | 프로젝트 승인 formatter/linter (예: Biome 또는 ESLint + Prettier) | format + lint + typecheck + test |
| Python | Ruff + pytest; typing 필요 시 mypy/pyright | lint + 필요 시 typecheck + test |
| Rust | `rustfmt`, `clippy`, `cargo test` | fmt + clippy + test |
| Shell | `shfmt`, ShellCheck | format + static analysis |
| Markdown | markdownlint 또는 동등 도구 | naming/pair 검사 + lint 적용 시 lint |
| YAML | yamllint 또는 동등 도구 | syntax + lint |
| Dockerfile | hadolint 또는 동등 도구 | lint + image build |
| Container | Trivy 또는 동등 도구 | vulnerability scan |
| Helm | `helm lint`, schema/render validation | lint + render validation |
| Kubernetes manifest | kubeconform/kubeval 또는 동등 도구 | schema validation |
| Terraform | `terraform fmt`, `terraform validate`, 필요 시 TFLint | fmt + validate |

## 선택 규칙

1. IDE 없이 실행 가능한 deterministic CLI 도구를 우선합니다.
2. CI에서 사용하는 도구의 버전을 고정합니다.
3. 핵심 검사는 Local과 CI에서 동일하게 실행합니다.
4. Formatting 차이는 파일을 조용히 수정하지 않고 CI에서 실패시키는 것을 우선합니다.
5. Tool configuration은 저장소에서 관리합니다.
6. 단순한 인기보다 실제 Engineering Value를 기준으로 도구를 선택합니다.
7. 생성 artifact는 source에서 재현 가능해야 합니다.

## Go 예시

Go 프로젝트는 `gofmt`를 직접 호출하는 대신 `gofumpt`를 OpenForge Formatting 기준으로 사용합니다. 프로젝트별로 승인된 배포판을 선택할 수 있으며, 명시적인 경우 `dasomel-dev/gofumpt` fork를 사용할 수 있습니다.

## Code Graph 예시

Architecture 또는 AI-assisted Change-impact 분석에 실제 도움이 되는 저장소에서는 적합한 `codegraph`, `graphify` 또는 동등 도구를 사용해 재현 가능한 Graph 생성 단계를 둘 수 있습니다. Graph는 파생 데이터이며 authoritative Architecture 기록을 대체하지 않습니다.
