# AGENTS.md

OpenForge defines reusable engineering standards for the OpenForge-family repositories. Downstream repositories link to this repository's docs, so `docs/change-management.md` and `docs/agent-engineering.md` must keep their paths.

- Keep declarative standards, executable checks, and human-judgment guidance separate; when a rule can be enforced reliably, put it in a script, test, or CI instead of prose.
- Treat changes under `templates/` as portfolio-wide API changes: consider downstream repositories and backward compatibility.
- Make the smallest coherent change; report unrelated findings instead of fixing them.
- For bugs in templates/scripts: reproduce, add a failing test or evidence, minimal fix, then the same evidence passes.
- Docs are bilingual (`X.md` + `X-ko.md`; root README/CONTRIBUTING/SECURITY/CODE_OF_CONDUCT pairs are enforced by CI); `*_ko.md` / `*.ko.md` names are rejected.
- Engineering measurements follow `docs/research-evidence.md`.
- Change classification (A-D, Change Package) and the A/B/C completion convention are defined in `docs/change-management.md` and `docs/agent-engineering.md`.

## Verify

Mirror of the CI jobs that touch instructions and templates:

- `python3 -m unittest discover -s tests`
- `python3 templates/scripts/audit-agent-skills.py . --strict`
- `python3 templates/scripts/audit-instruction-debt.py .`
- Rust changes: `cargo fmt --all -- --check`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo test --all-targets --all-features`

## Instruction design

Standard: `docs/model-agnostic-agent-instructions.md`, `docs/claude-agents-shared-instructions.md`, `docs/agent-skills.md`. `CLAUDE.md` is the reference thin adapter that downstream repositories copy from `templates/CLAUDE.md`.
