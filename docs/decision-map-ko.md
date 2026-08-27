# OpenForge 의사결정 맵

[English](decision-map.md) | 한국어

이 문서는 OpenForge의 장기 의사결정과 이를 구현하는 Standard, 재사용 가능한 Enforcement, Adoption Evidence를 연결합니다.

두 번째 Source of Truth를 만드는 것이 목적은 아닙니다. ADR은 **왜**, Standard는 **무엇을**, Template/CI/Policy는 **어떻게**, Adoption Record는 **어디에/언제** 적용했는지를 담당합니다.

| ADR | 장기 의사결정 | Normative Standard | Reusable Enforcement / Adoption |
|---|---|---|---|
| [0001](adr/0001-record-cross-project-decisions-ko.md) | Cross-project Decision을 ADR로 관리 | [의사결정 관리](decision-management-ko.md), [변경 관리](change-management-ko.md) | `templates/ADR*.md`, ADR Index, Contributing Review Gate |
| [0002](adr/0002-english-canonical-korean-first-class-ko.md) | English canonical + Korean first-class | [Documentation](documentation-ko.md), [Internationalization](i18n-ko.md) | `-ko.md` 규칙, CI Filename Validation |
| [0003](adr/0003-risk-based-oss-security-governance-ko.md) | Risk 기반 OSS Security/Governance | [Security](security-ko.md), [Maintainer Governance](maintainer-governance-ko.md), [Security Exceptions](security-exceptions-ko.md), [Branch Protection](branch-protection-ko.md) | Risk-based Control, Branch Protection 기준, Exception Record |
| [0004](adr/0004-treat-ai-and-plugins-as-untrusted-input-ko.md) | AI/Plugin 입력을 untrusted executable influence로 취급 | [AI Engineering Security](ai-engineering-security-ko.md), [Plugin Supply Chain](plugin-supply-chain-ko.md) | Plugin Intake Policy, Agent Security Constraint |
| [0005](adr/0005-require-workflow-impact-analysis-for-upgrades-ko.md) | Upgrade 시 Workflow 전체 영향 분석 | [변경 관리](change-management-ko.md), [Upgrade Compatibility](upgrade-compatibility-ko.md) | Impact Matrix, Workflow Inventory, Compatibility Evidence |
| [0006](adr/0006-build-security-into-release-supply-chain-ko.md) | Lifecycle Security/Supply Chain | [Supply Chain](supply-chain-ko.md), [CI Security](ci-security-ko.md), [Release Security](release-security-ko.md) | SBOM/Provenance, Policy Check, Release Verification Template |
| [0007](adr/0007-design-system-standardizes-semantics-not-identity-ko.md) | Product Identity를 보존하며 Semantic 표준화 | [OSS Design System](design-system-ko.md) | `templates/DESIGN.md`, Figma Design System, Project Archetype |
| [0008](adr/0008-layer-agent-instructions-and-keep-root-context-small-ko.md) | Agent Instruction 계층화 및 작은 Root Context | [Agent Engineering](agent-engineering-ko.md) | `templates/AGENTS.md`, `templates/CODING_STANDARDS.md`, Portfolio Rollout |
| [0009](adr/0009-evidence-first-agent-verification-and-convergence-ko.md) | Evidence-first Agent Verification/Convergence | [Agent Engineering](agent-engineering-ko.md) | Bug-first Workflow, A/B/C Convergence, [2026-08 적용 기록](agent-engineering-adoption-2026-08.md) |
| [0010](adr/0010-reusable-templates-are-adaptable-baselines-ko.md) | Template은 Adaptable Baseline | [Repository Standard](repository-ko.md) | `templates/` Catalog, Placeholder/Adaptation Guidance |
| [0011](adr/0011-ci-resilience-must-not-encourage-security-bypass-ko.md) | CI Resilience가 Assurance를 유지 | [CI Resilience](ci-resilience-ko.md), [CI Security](ci-security-ko.md) | Degraded-state/Fallback Handling, Security Exception Path |
| [0012](adr/0012-document-and-time-bound-intentional-exceptions-ko.md) | Intentional Exception 문서화 및 재검토 | [Security Exceptions](security-exceptions-ko.md), [Maintainer Governance](maintainer-governance-ko.md) | Expiry/Review Field, `DESIGN.md` Deviation Table, Change Record |

## Audit 사용법

정기 OpenForge Audit에서는 다음 네 방향을 확인합니다.

1. **ADR → Standard** — Accepted Decision이 여전히 Normative Home을 가지는가
2. **Standard → Enforcement** — Deterministic Rule이 가능한 범위에서 자동화됐는가
3. **Enforcement → Adoption** — Reference OSS가 실제로 재사용 Practice를 적용하는가
4. **Adoption → Feedback** — 반복되는 Project Evidence가 Common Default를 바꿀 정도라면 다시 Decision으로 승격되는가

이 연결이 끊기면 일반적인 Documentation Debt가 아니라 **Standards Drift**로 취급합니다.
