# OpenForge Execution Evidence

OpenForge L2 execution evidence verifies that selected engineering controls actually execute successfully instead of inferring maturity only from repository files.

Execution is opt-in:

```bash
openforge . --run-execution
```

The default assessment remains static and does not execute target repository code.

## Security model

Execution probes are trusted built-ins compiled into the OpenForge binary. External rulesets cannot introduce shell commands. This prevents a downloaded or repository-local ruleset from silently becoming an arbitrary command execution mechanism.

`--run-execution` is an explicit trust boundary. Build and test commands may execute build scripts, test fixtures, generators, compiler plugins, or other target-repository code. Run execution assessment only for repositories you trust and preferably in an isolated CI job or disposable environment.

## Initial profiles

Rust projects detected by `Cargo.toml`:

- `cargo check --all-targets --all-features`
- `cargo test --all-targets --all-features`
- `cargo clippy --all-targets --all-features -- -D warnings`

Go projects detected by `go.mod`:

- `go build ./...`
- `go test ./...`
- `go vet ./...`

If execution is disabled, applicable execution findings are reported as `SKIP` and are excluded from score denominators. If no supported execution profile is detected, no execution findings are added.

## Evidence

Each execution finding records the command, exit code, and a bounded tail of stdout/stderr. A successful execution probe contributes to the `Execution` category. A failed probe contributes zero for that probe and includes remediation guidance.

Execution evidence is stronger than static declaration evidence but still does not replace runtime verification. OpenForge keeps the evidence progression explicit:

```text
Declared < Configured < Executed < Runtime Verified
```

Runtime evidence is planned as a separate L3 assessment dimension.
