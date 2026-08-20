# Engineering Tooling Standard

OpenForge defines preferred tools for repeatable code quality, codebase understanding and engineering automation. Tooling is language-aware: apply the rules that match the project rather than forcing one stack onto every repository.

## Go

Use `gofumpt` as the default formatter instead of calling `gofmt` directly. `gofumpt` is a stricter formatter built on top of Go formatting conventions. The OpenForge default command is:

```bash
gofumpt -w .
```

For CI:

```bash
test -z "$(gofumpt -l .)"
```

The project may pin or vendor an approved `gofumpt` build. The `dasomel-dev/gofumpt` repository is an available stricter `gofumpt` fork; use it only when the project explicitly selects that distribution.

Recommended Go baseline:

```text
gofumpt
	go vet
	staticcheck (when adopted)
	go test ./...
```

## Code intelligence / Code graph

For medium and large codebases, maintain machine-readable code structure where it materially improves review, architecture work and AI-assisted development.

Preferred capabilities:

- symbol and dependency graph generation
- package/module relationship analysis
- call/reference navigation
- architectural dependency inspection
- change-impact analysis

Tools such as `codegraph` and `graphify` can be integrated when they match the language and repository. They should be treated as engineering-analysis tools, not as runtime dependencies.

Generated graph data should be reproducible from source and should not become the authoritative source of architecture.

## AI-assisted development

AI coding tools may use repository guidance such as `AGENTS.md`, `CLAUDE.md`, or equivalent project instructions.

Projects should keep AI instructions:

- versioned with the repository
- concise and actionable
- consistent with human documentation
- explicit about commands, architecture boundaries and safety constraints

AI-generated changes remain subject to the same tests, review, security and license requirements as human-authored changes.

## General tool selection

Prefer tools that are:

- reproducible in CI
- available on Linux and macOS when practical
- scriptable
- open-source or clearly licensed
- pin-able by version
- usable without requiring an interactive session
