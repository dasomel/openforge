# Engineering Tooling Matrix

This matrix defines OpenForge defaults. A project may choose an alternative when justified by its language, framework or operational constraints; record significant deviations as an ADR.

| Area | Preferred baseline | Minimum CI check |
|---|---|---|
| Go | `gofumpt`, `go vet`, `go test`; `staticcheck` when adopted | formatting + vet + test |
| TypeScript / JavaScript | project-approved formatter/linter (for example Biome or ESLint + Prettier) | format + lint + typecheck + test |
| Python | Ruff + pytest; mypy/pyright when typing requires it | lint + typecheck when used + test |
| Rust | `rustfmt`, `clippy`, `cargo test` | fmt + clippy + test |
| Shell | `shfmt`, ShellCheck | format + static analysis |
| Markdown | markdownlint or equivalent | naming/pair checks + lint when enabled |
| YAML | yamllint or equivalent | syntax + lint |
| Dockerfile | hadolint or equivalent | lint + image build |
| Containers | Trivy or equivalent | vulnerability scan |
| Helm | `helm lint`, schema/render validation | lint + render validation |
| Kubernetes manifests | kubeconform/kubeval or equivalent | schema validation |
| Terraform | `terraform fmt`, `terraform validate`, optional TFLint | fmt + validate |

## Selection rules

1. Prefer deterministic CLI tools that run without an IDE.
2. Pin versions for tools used by CI.
3. Run the same essential checks locally and in CI.
4. Fail CI on formatting drift rather than silently rewriting files.
5. Keep tool configuration in the repository.
6. Avoid adding a tool merely because it is popular; explain its engineering value.
7. Generated artifacts must be reproducible from source.

## Go example

For Go repositories, `gofumpt` is the OpenForge formatting baseline rather than direct `gofmt` invocation. The approved distribution may be selected per project, including the `dasomel-dev/gofumpt` fork where explicitly required.

## Code graph example

For repositories where architecture or AI-assisted change-impact analysis benefits from graph data, add a reproducible graph-generation step using an appropriate `codegraph`, `graphify`, or equivalent tool. The graph is derived data and never the authoritative architecture record.
