# Reference Implementation Metrics

> Metrics derived from existing dasomel OSS repositories and used as practical reference targets for OpenForge.

## 1. Purpose

OpenForge defines standards, but standards are easier to apply when maintainers can compare a new repository with proven implementations. This document provides a lightweight maturity scorecard based on patterns already used in maintained OSS projects.

These are **reference metrics, not mandatory universal thresholds**. A project may mark an item N/A when it does not apply and should record intentional deviations in an ADR.

## 2. Repository Maturity Matrix

| Area | Metric | Target | Reference practice | Evidence to check |
|---|---|---:|---|---|
| Documentation | English README | 1 | All mature repositories | `README.md` |
| Documentation | Korean README | 1 | Current dasomel OSS direction | `README-ko.md` |
| Documentation | Language-paired docs | 100% applicable docs | English canonical + `-ko.md` | CI/documentation audit |
| Documentation | Architecture document | 1 | Narwhal / Narwhal Portal | `docs/architecture*.md` |
| Documentation | Development guide | 1 | Multiple active repositories | `docs/development*.md` |
| Documentation | Release guide | 1 | Release-oriented repositories | `RELEASING*.md` |
| Documentation | Version inventory | 1 for platform projects | Narwhal-style practice | `VERSIONS.md` |
| Documentation | Lessons / mistakes log | Recommended | Narwhal / KubeMetal practice | `lessons-log*.md` / `mistakes-log*.md` |
| Architecture | ADR process | 1 | OpenForge / Narwhal Portal practice | `docs/adr/` |
| Architecture | Decision management standard | Recommended for multi-project standards | OpenForge | `docs/decision-management*.md` |
| Architecture | ADR English/Korean pairs | 100% user-facing ADRs | OpenForge | ADR CI validation |
| Architecture | Decision map / traceability | Recommended for standards repositories | OpenForge | `docs/decision-map*.md` |
| GitHub | PR template | 1 | ldapium / others | `.github/pull_request_template.md` |
| GitHub | Bug template | 1 | Common project practice | `.github/ISSUE_TEMPLATE/` |
| GitHub | Feature template | 1 | Common project practice | `.github/ISSUE_TEMPLATE/` |
| GitHub | Architecture template | Recommended | Beluga/OpenForge direction | `.github/ISSUE_TEMPLATE/` |
| CI | Automated CI | 1 | All active code repositories | `.github/workflows/` |
| CI | Format check | 1 | Language-specific | workflow |
| CI | Test | 1 | Code repositories | workflow |
| CI | Build | 1 | Application/library repositories | workflow |
| CI | Documentation validation | Recommended | OpenForge standard | workflow |
| CI | ADR pair/index validation | Recommended when ADRs are bilingual | OpenForge | `templates/scripts/validate-adrs.sh` |
| Security | Dependency update automation | 1 | Dependabot practice | `.github/dependabot.yml` |
| Security | Container scanning | Required when containers exist | Trivy-oriented practice | CI |
| Security | Code scanning | Recommended | CodeQL / equivalent | CI |
| Security | Scorecard / supply-chain checks | Recommended for public OSS | ldapium practice | workflow |
| Security | SECURITY policy | 1 | Mature OSS practice | `SECURITY*.md` |
| Development | Formatter | 1 per language | Project-specific standard | tooling matrix |
| Development | Go formatter | `gofumpt` | OpenForge Go standard | `gofumpt` check |
| Development | Go static analysis | `go vet` + recommended static analyzer | OpenForge Go standard | CI |
| Development | Test command | 1 documented command | Makefile/project docs | `make test` or equivalent |
| Development | Unified task runner | Recommended | Makefile practice in KubeMetal | `Makefile` |
| Development | Code graph | Recommended for complex codebases | codegraph / graphify use case | generated graph/artifact |
| Development | AI agent instructions | Recommended | Narwhal / KubeMetal / Portal practice | `AGENTS.md`, `CLAUDE.md`, etc. |
| Release | Changelog | 1 | Existing OSS practice | `CHANGELOG.md` |
| Release | Versioning policy | 1 | Existing OSS practice | `VERSION*` / release docs |
| Release | Release workflow | Recommended | KubeMetal / active projects | `.github/workflows/` |
| Release | Artifact verification | Recommended | Supply-chain standard | digest/SBOM/provenance |
| Configuration | `.env.example` | Required when env config exists | ldapium practice | `.env.example` |
| Localization | UI i18n | Required for UI projects | Beluga Manager direction | locale resources |
| Localization | `en-US` | 1 | Beluga Manager standard | locale resources |
| Localization | `ko-KR` | 1 | Beluga Manager standard | locale resources |

## 3. Scoring

For a quick repository health check, score each applicable metric:

- **2 — Implemented and automated where practical**
- **1 — Implemented manually / partially**
- **0 — Missing**
- **N/A — Not applicable**

Suggested interpretation:

| Score | Maturity |
|---:|---|
| 90–100% | Production-ready OSS foundation |
| 75–89% | Healthy / minor gaps |
| 60–74% | Developing / improvement recommended |
| <60% | Foundation work required |

The percentage is calculated only over applicable metrics.

## 4. Reference Projects

The matrix is informed by existing repositories rather than invented from scratch. Reference repositories include:

- `openforge` — cross-project ADR governance, bilingual decision history, CI validation, standards/templates traceability
- `narwhal` — platform architecture, versions, lessons, AI instructions, release/deployment documentation
- `narwhal-portal` — ADR, roadmap, design system, AI instructions
- `nfs-quota-agent` — bilingual documentation and development/release conventions
- `kube-ready-box` — bilingual README and AI/skill guidance
- `kubemetal` — Makefile, release workflow, mistakes log, AI instructions
- `ldapium` — security/release files, `.env.example`, PR standards, Scorecard-oriented supply-chain checks
- `beluga-manager` — bilingual documentation, unified domain/API architecture, i18n-first UI policy

## 5. How to Use This Matrix

When bootstrapping a new OSS repository:

1. Copy the OpenForge project foundation.
2. Run the reference-metrics checklist.
3. Mark each metric `2`, `1`, `0`, or `N/A`.
4. Create issues for all missing `0` items that apply.
5. Record intentional deviations in an ADR.
6. For durable shared defaults, link ADR → Standard → enforcement → adoption evidence.
7. Re-run the matrix before the first stable release.

The matrix should evolve when existing projects demonstrate a better repeatable practice.
