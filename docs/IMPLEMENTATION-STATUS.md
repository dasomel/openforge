# Current Implementation Status

Last verified: 2026-09-24 against `main`.

OpenForge is no longer only a collection of prose standards. The repository now contains executable portfolio-governance machinery, reusable engineering templates, ADR discipline, design-system guidance and adoption evidence from active OSS repositories.

## Implemented standards

OpenForge currently documents shared standards for:

- repository and documentation structure
- development and engineering tooling
- CI/CD and CI resilience
- security and supply-chain security
- dependency / package / artifact identity
- change impact and upgrade compatibility
- AI-assisted engineering and agent engineering
- container / Kubernetes / IaC security
- secrets and machine identity
- vulnerability and incident response
- release security and exception governance
- localization
- OSS compliance
- UI/UX design-system contracts
- maintainer governance

## ADR and decision governance

Durable cross-project decisions are recorded as ADRs and linked to standards/templates rather than being buried in implementation history. `docs/adr/` currently holds 15 canonical decisions (0001-0015); `templates/scripts/generate-portfolio.py` fails its `--check` if `portfolio/projects.json`'s `portfolio.adr_count` drifts from the files on disk (`count_english_adrs`).

```text
ADR -> Standard -> Template / CI / Policy -> Adoption record / Issue / PR
```

English is canonical and Korean is maintained as a first-class translation for user-facing policy where provided.

## Executable compliance assessment

A portable portfolio audit engine is implemented under the reusable template/scripts area. It supports:

- portfolio-wide repository assessment
- single-repository assessment
- stable metric identifiers
- historical baseline comparison
- scorecard generation
- delta analysis
- actionable gap-issue generation
- parser/false-positive regression fixtures

`portfolio/projects.json` registers 15 repositories (`portfolio.standard_metrics: 35`); the scored table in `docs/portfolio-scorecard.md` covers 14 of them, since Siqoq is registered with `role: "experiment"` and `adoption_percent: null` and is not yet scored. After the first adoption wave the portfolio scorecard records 61.6% adoption (`portfolio/dashboard.json` → `portfolio.adoption_percent`); that value is an evidence snapshot, not a permanent target.

## Branch / repository governance

Implemented governance includes:

- branch-protection standard
- GitHub issue/PR templates
- AGENTS.md execution-contract template
- coding-standards template
- design-system contract template
- security-policy baseline
- reusable CI/release/SBOM patterns

## Design system

OpenForge includes an OSS design-system standard plus a Figma design-system reference. The rule is to share semantics, accessibility and common tokens while allowing each project to retain its own density, platform convention and visual personality.

## Agent engineering

Agent context is treated as engineering input, not free-form prompt text. Implemented guidance covers concise repository contracts, executable checks, context dilution, risky tool/plugin intake and evidence-first review. ADR-0013 (`docs/adr/0013-bind-agent-authority-to-canonical-resolved-invocations.md`) now also defines the execution grant enforcement boundary: explicit PDP (policy decision point), grant issuer/signer and PEP (policy enforcement point) responsibilities, with spend-once/atomic-consume semantics for high-risk operations so the agent/model runtime cannot hold the authority to mint its own execution grants.

## Agent Skills standard and audit

The Agent Skills standard is implemented: `docs/agent-skills.md` / `-ko.md` define a canonical `.agents/skills/` layout (one editable copy per skill; runtime-specific copies are generated or linked, never hand-diverged), an `openforge-maturity` lifecycle (`draft` -> `verified` -> `stable`, plus `deprecated`), and a `.agents/skill-evals/<skill-name>.json` verification-evidence convention (schema in `templates/agent-skill-verification.json`) that gates `verified` on a fresh-session replay with recorded evidence rather than a self-report. `templates/scripts/audit-agent-skills.py` audits skills for duplication, missing maturity and missing evidence.

A revision-bound agent engineering audit runs across the portfolio: `templates/scripts/audit-agent-engineering.py` inspects each repository's own pinned revision for deterministic controls (formatting/lint/tests/static-analysis/security-policy/generated-files), Agent Skills maturity and false-green findings; `templates/scripts/generate-agent-audit-matrix.py` renders the results to `docs/agent-audit-matrix.md` / `-ko.md`; `portfolio/agent-audit.json` is the generated data source; `.github/workflows/refresh-agent-audit.yml` refreshes it on a schedule and on policy change. The current snapshot covers 11 repositories and 24 canonical Agent Skills: 10 `verified`, 6 `draft`, and 8 with unspecified maturity; 6 mature skills have evidence. It records 15 false-green findings across 9 repositories, 2 swallowed-validator findings across all 11 measured repositories, and repository-local agent contract gates in 2 repositories. See the generated [audit matrix](agent-audit-matrix.md) for revision-bound detail.

A repository-local agent contract gate uses `audit-agent-skills.py --strict` to escalate the codes in `STRICT_CONTRACT_CODES` to fail-closed exit status instead of the default report-only severities; `templates/github/agent-contract-gate.yml` is the reusable caller workflow and `.github/workflows/agent-contract-gate.yml` its callee. `detect_local_agent_gate` in `audit-agent-engineering.py` detects whether a repository wires this into its own CI, surfaced as the `local_agent_ci_gate` field and the "Local gate" column in the audit matrix. The current audit detects this gate in 2 of 11 scanned repositories. OpenForge runs it on itself via the `agent-contract` job in `.github/workflows/ci.yml`.

The audit also models the second false-green class — an executable owner that runs and has its verdict discarded. `templates/scripts/swallowed_failure_detector.py` reports `|| true`, `|| :`, `|| exit 0`, make's `-` recipe prefix, step- and job-level `continue-on-error: true`, and `set +e` over a validator whose status is never read, classifying the program rather than the idiom so that `grep ... || true` and cleanup or probe commands are not reported. The current revision-bound scan records 2 findings across 11 measured repositories. Validators invoked through a third-party action (`uses:`) and commands assembled from variables at runtime are outside what it can classify.

## Maintenance and lifecycle governance

`portfolio/maintenance.json` is a maintenance/lifecycle registry (ownership, blast radius, exit-review requirements) validated by `templates/scripts/validate-portfolio-maintenance.py`; `docs/portfolio-maintenance.md` / `-ko.md` document the governance rule. Current registry state (`validate-portfolio-maintenance.py` output): `projects=15 owned=15 high-blast-radius=3 exit-review-required=15`.

## Documentation freshness rule

Implementation status should flow through:

```text
Implementation -> Evidence -> OSS documentation -> Blog / storytelling
```

Capabilities must not be described as implemented until they exist on the target repository's default branch with a reproducible evidence path. Issue-only or design-only work must remain labeled as planned/experimental.

This is now an executable rule, not only prose: `docs/documentation-freshness.md` / `-ko.md` define the standard (including this file's required ``Last verified: YYYY-MM-DD against `main`.`` line shape); the `DOC-010` metric in `templates/scripts/audit-portfolio.py` checks a repository's `docs/IMPLEMENTATION-STATUS.md` against that regex when the repository opts in with `documentation_freshness: true`; `templates/scripts/validate-doc-impact.py` is a companion check; and `.github/pull_request_template.md` now has a required "Documentation / Blog impact" section (`none` / `updated` / `follow-up-required`) per the standard's PR contract.

## Kubernetes zero-trust security baseline

ADR-0014 (`docs/adr/0014-standardize-kubernetes-zero-trust-security-baseline.md`) and `docs/kubernetes-zero-trust-security-baseline.md` define a Kubernetes zero-trust baseline; `templates/kubernetes/security/` provides the reusable artifacts (`security-profile.example.yml`, `workload-baseline.yaml`, `mesh-istio-ambient-strict.yaml`, `check-host-security.sh`, `README.md`).

## Engineering operating model

`docs/engineering-operating-model.md` documents the engineering operating model, and `docs/maka-runtime-evaluation.md` records the Maka runtime adoption evaluation and decision.

## Portfolio adoption

OpenForge standards have already been applied to active repositories including Narwhal, nfs-quota-agent and ldapium through documentation naming, security/GitHub templates and design-system/engineering contracts.

`portfolio/dashboard.json` has a live downstream consumer: `dasomel.github.io` syncs it on a schedule and renders it on its public `/oss` page (see `docs/portfolio-governance.md#downstream-consumers`). It also now carries a top-level `agent_audit` block sourced from `portfolio/agent-audit.json`, rendered by `docs/portfolio-dashboard.md`'s "Agent engineering audit" section. That block follows an explicit honesty rule: a `null` value (for example `swallowed_failure_findings` or `local_agent_ci_gate` at the per-repository level) means the metric has not been measured yet at this revision, and is kept distinct from a measured `0`, which means measured-and-currently-zero.

## Not yet done

These are open, not implemented, and should not be described otherwise:

- **Status publication is verified for one caller.** Beluga Manager's `OPENFORGE_STATUS_TOKEN` successfully opened an OpenForge status PR and passed all 16 checks. The other eight priority caller repositories still need their own credential configured and an end-to-end run (issue #39).
- **Some Agent Skills remain unverified or need more evidence.** The current snapshot records 10 `verified` skills with 6 mature skills backed by evidence, 6 `draft`, and 8 with unspecified maturity. Fresh-session replay, edge-case and real-runtime gaps remain project-owned; maturity must not be inferred from this aggregate snapshot (issue #54).
- **Repository-local agent contract gate adoption is partial.** The revision-bound audit detects gates in 2 of 11 repositories. The remaining repositories should adopt or explicitly assess this control as their owning issues and rollout work allow.

## Related evidence

- `README.md`
- `docs/adr/README.md`
- `docs/adr/0013-bind-agent-authority-to-canonical-resolved-invocations.md`
- `docs/adr/0014-standardize-kubernetes-zero-trust-security-baseline.md`
- `docs/agent-engineering.md`
- `docs/agent-skills.md`
- `docs/agent-audit-matrix.md`
- `docs/documentation-freshness.md`
- `docs/portfolio-maintenance.md`
- `docs/kubernetes-zero-trust-security-baseline.md`
- `docs/engineering-operating-model.md`
- `docs/design-system.md`
- `docs/oss-compliance.md`
- `docs/reference-metrics.md`
- `docs/portfolio-scorecard.md`
- `docs/portfolio-dashboard.md`
- `docs/branch-protection.md`
- `templates/`
- `templates/scripts/audit-portfolio.py`
- `templates/scripts/audit-agent-engineering.py`
- `templates/scripts/audit-agent-skills.py`
- `templates/scripts/validate-portfolio-maintenance.py`
- `portfolio/agent-audit.json`
- `portfolio/maintenance.json`

Refresh this file after meaningful standards, audit-engine or portfolio-adoption changes.
