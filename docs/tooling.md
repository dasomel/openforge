# Engineering Tooling Standard

OpenForge defines preferred tools for repeatable code quality, codebase understanding and engineering automation. Tooling is language-aware: apply the rules that match the project rather than forcing one stack onto every repository.

## Go

Use `gofumpt` as the default formatter instead of calling `gofmt` directly. `gofumpt` is a stricter formatter built on top of Go formatting conventions.

```bash
gofumpt -w .
```

For CI:

```bash
test -z "$(gofumpt -l .)"
```

The project should pin the formatter version or otherwise make the distribution reproducible. The `dasomel-dev/gofumpt` repository is an available stricter `gofumpt` fork; use a fork only when the project intentionally selects that distribution and records the reason.

Recommended Go baseline:

```text
gofumpt
  ↓
go vet
  ↓
staticcheck (when adopted)
  ↓
go test ./...
```

## Language toolchains

Use the [Engineering Tooling Matrix](tooling-matrix.md) as the default baseline for Go, TypeScript/JavaScript, Python, Rust, Shell, Markdown, YAML, Dockerfile, container, Helm, Kubernetes and Terraform projects.

Project-specific alternatives are allowed when they provide a clear engineering benefit. Significant deviations should be recorded as an ADR.

## Code intelligence / Code graph

For medium and large codebases, maintain machine-readable code structure where it materially improves review, architecture work and AI-assisted development.

Preferred capabilities:

- symbol and dependency graph generation
- package/module relationship analysis
- call/reference navigation
- architectural dependency inspection
- change-impact analysis

Tools such as `codegraph` and `graphify` can be integrated when they match the language and repository. Treat them as engineering-analysis tooling, not runtime dependencies.

Generated graph data should be reproducible from source and should not become the authoritative source of architecture. Prefer generating graphs on demand or in CI unless the repository has a clear reason to check derived graph artifacts into source control.

## Repository guidance for AI-assisted development

AI coding tools may use repository guidance such as `AGENTS.md`, `CLAUDE.md`, `.agent/AGENT.md`, or an equivalent project instruction file. Active OpenForge reference repositories demonstrate that repository-local instructions are useful for commands, migration work, architecture boundaries and safety constraints.

Keep AI instructions:

- versioned with the repository
- concise and actionable
- consistent with human documentation
- explicit about commands, architecture boundaries and safety constraints
- free of secrets and credentials

AI-generated changes remain subject to the same tests, review, security and license requirements as human-authored changes.

## Command surface

For projects with non-trivial build or deployment workflows, provide a discoverable command surface through `Makefile` or an equivalent tool such as `just`, `task`, npm scripts or project-native commands.

The command surface should expose common operations such as:

```text
setup / bootstrap
format
lint
test
build
check
release
clean
```

Avoid hiding required environment assumptions inside opaque scripts.

## Version and compatibility tooling

When a project contains the same component version in charts, images, manifests, package metadata or release files, automate consistency checks. A checked-in `VERSIONS.md` or equivalent inventory is preferred for platform projects.

## General tool selection

Prefer tools that are:

- reproducible in CI
- available on Linux and macOS when practical
- scriptable
- open-source or clearly licensed
- pin-able by version
- usable without requiring an interactive session
