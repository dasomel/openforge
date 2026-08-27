# OpenForge Portfolio Compliance Scorecard

> Automated audit of active Dasomel OSS repositories against OpenForge engineering standards.

**Overall Portfolio Maturity:** `52.6%`
**Audited Repositories:** 14 projects

## 1. Portfolio Maturity Ranking

| Repository | Category | Archetype | Score | Maturity Status |
|---|---|---|---:|---|
| **OpenForge** | Standards & Blueprints | `Developer Tool` | 🟢 **96.7%** (58/60) | Production-ready OSS foundation |
| **ldapium** | Identity & Directory Service | `Admin Console` | 🟡 **76.6%** (49/64) | Healthy / minor gaps |
| **ClusterDeck** | Kubernetes Operations | `Operations Dashboard` | 🟠 **68.8%** (44/64) | Developing / improvement recommended |
| **NFS Quota Agent** | Storage & Kubernetes Controllers | `Developer Tool` | 🟠 **66.1%** (41/62) | Developing / improvement recommended |
| **Narwhal Portal** | Internal Developer Platform | `Platform Portal` | 🟠 **64.1%** (41/64) | Developing / improvement recommended |
| **Narwhal** | Internal Developer Platform | `Platform Portal` | 🟠 **63.8%** (37/58) | Developing / improvement recommended |
| **kube-ready-box** | OS & VM Infrastructure | `Developer Tool` | 🔴 **55.6%** (30/54) | Foundation work required |
| **KubeMetal** | Apple Silicon Hybrid MLOps | `Desktop Operator` | 🔴 **54.8%** (34/62) | Foundation work required |
| **dasomel.github.io** | Community Tech Blog | `Platform Portal` | 🔴 **50.0%** (31/62) | Foundation work required |
| **eGovFrame Launcher** | eGovFrame Developer Tooling | `Developer Tool` | 🔴 **38.3%** (23/60) | Foundation work required |
| **Kairos** | Automated Trading Bot | `Developer Tool` | 🔴 **35.0%** (21/60) | Foundation work required |
| **Beluga** | Data Platform IaC | `Data Control Plane` | 🔴 **33.9%** (19/56) | Foundation work required |
| **cka-lab** | Certification & Lab Simulator | `Developer Tool` | 🔴 **13.0%** (7/54) | Foundation work required |
| **Beluga Manager** | Data Platform Management | `Data Control Plane` | 🔴 **12.9%** (8/62) | Foundation work required |

## 2. Requirement Traceability & Gap Summary

### OpenForge (`96.7%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/openforge`
- **Archetype:** `Developer Tool` | **Category:** Standards & Blueprints
- **Gaps Identified:** 2

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| CI | **Format & Lint Check in CI** (🟡 Partial (1)) | CI present but no explicit format check detected | Add format/lint validation step to CI. `Deterministic rule enforcement.` |

### ldapium (`76.6%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/ldapium`
- **Archetype:** `Admin Console` | **Category:** Identity & Directory Service
- **Gaps Identified:** 10

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🟡 Partial (1)) | Legacy filename: README_ko.md | Rename README_ko.md -> README-ko.md per ADR-0002. `ADR-0002 / rename to -ko.md` |
| Documentation | **Korean Filename Standard** (🔴 Missing (0)) | Found 8 legacy files (CONTRIBUTING_ko.md, RELEASING_ko.md) | Migrate legacy Korean filenames (8 files) to *-ko.md. `ADR-0002 naming standard` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🔴 Missing (0)) | Missing DESIGN.md in UI project | Create DESIGN.md using OpenForge template with archetype and token mapping. `ADR-0007 required for UI.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🔴 Missing (0)) | Missing archetype declaration | Declare Admin Console in DESIGN.md. `ADR-0007 design contract.` |
| Design System | **Semantic Token Mapping** (🔴 Missing (0)) | No token mapping found | Map UI tokens to OpenForge semantic tokens in DESIGN.md. `ADR-0007 semantic tokens.` |
| Localization | **UI i18n (en-US & ko-KR)** (🟡 Partial (1)) | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. `ADR-0002 bilingual UI requirement.` |

### ClusterDeck (`68.8%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/clusterdeck`
- **Archetype:** `Operations Dashboard` | **Category:** Kubernetes Operations
- **Gaps Identified:** 14

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Bilingual Pairs** (🔴 Missing (0)) | 1/1 ADRs missing Korean pair | Add Korean translations for docs/adr/0001-macos-first-tauri-architecture.md. `ADR-0002 bilingual parity.` |
| Architecture | **DESIGN.md Contract** (🔴 Missing (0)) | Missing DESIGN.md in UI project | Create DESIGN.md using OpenForge template with archetype and token mapping. `ADR-0007 required for UI.` |
| GitHub | **Contributing Guide (en+ko)** (🟡 Partial (1)) | Found CONTRIBUTING.md (missing Korean pair) | Add CONTRIBUTING-ko.md. `ADR-0002 bilingual guidance.` |
| CI | **Documentation & ADR Validation** (🟡 Partial (1)) | Workflows present without dedicated doc check | Add documentation / ADR pair verification to CI. `Prevent doc drift.` |
| CI | **Supply Chain & Security Gates** (🟡 Partial (1)) | Standard CI present without supply chain gate | Add supply-chain and SBOM/dependency verification workflow. `ADR-0006 compliance.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🟡 Partial (1)) | Found SECURITY.md (missing Korean pair) | Add SECURITY-ko.md per ADR-0002. `Vulnerability disclosure path.` |
| Security | **Code Scanning / SAST** (🟡 Partial (1)) | CI present without automated SAST | Add CodeQL or language-specific static analysis. `Recommended public OSS practice.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🔴 Missing (0)) | Missing archetype declaration | Declare Operations Dashboard in DESIGN.md. `ADR-0007 design contract.` |
| Design System | **Semantic Token Mapping** (🔴 Missing (0)) | No token mapping found | Map UI tokens to OpenForge semantic tokens in DESIGN.md. `ADR-0007 semantic tokens.` |
| Localization | **UI i18n (en-US & ko-KR)** (🟡 Partial (1)) | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. `ADR-0002 bilingual UI requirement.` |

### NFS Quota Agent (`66.1%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/nfs-quota-agent`
- **Archetype:** `Developer Tool` | **Category:** Storage & Kubernetes Controllers
- **Gaps Identified:** 14

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🟡 Partial (1)) | Legacy filename: README_ko.md | Rename README_ko.md -> README-ko.md per ADR-0002. `ADR-0002 / rename to -ko.md` |
| Documentation | **Korean Filename Standard** (🔴 Missing (0)) | Found 3 legacy files (README_ko.md, docs/feature-guide_ko.md) | Migrate legacy Korean filenames (3 files) to *-ko.md. `ADR-0002 naming standard` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. `ADR-0007 adoption.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🟡 Partial (1)) | Found CONTRIBUTING.md (missing Korean pair) | Add CONTRIBUTING-ko.md. `ADR-0002 bilingual guidance.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🟡 Partial (1)) | DESIGN.md present without explicit archetype | Declare primary archetype (Developer Tool) in DESIGN.md. `ADR-0007 archetype standard.` |
| Design System | **Semantic Token Mapping** (🟡 Partial (1)) | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. `ADR-0007 design tokens.` |

### Narwhal Portal (`64.1%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/idp/narwhal-portal`
- **Archetype:** `Platform Portal` | **Category:** Internal Developer Platform
- **Gaps Identified:** 16

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🟡 Partial (1)) | Legacy filename: README_ko.md | Rename README_ko.md -> README-ko.md per ADR-0002. `ADR-0002 / rename to -ko.md` |
| Documentation | **Korean Filename Standard** (🔴 Missing (0)) | Found 6 legacy files (README_ko.md, CHANGELOG_ko.md) | Migrate legacy Korean filenames (6 files) to *-ko.md. `ADR-0002 naming standard` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. `ADR-0007 adoption.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| Security | **SECURITY Policy (en+ko)** (🟡 Partial (1)) | Found SECURITY.md (missing Korean pair) | Add SECURITY-ko.md per ADR-0002. `Vulnerability disclosure path.` |
| Security | **Code Scanning / SAST** (🟡 Partial (1)) | CI present without automated SAST | Add CodeQL or language-specific static analysis. `Recommended public OSS practice.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🟡 Partial (1)) | DESIGN.md present without explicit archetype | Declare primary archetype (Platform Portal) in DESIGN.md. `ADR-0007 archetype standard.` |
| Design System | **Semantic Token Mapping** (🟡 Partial (1)) | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. `ADR-0007 design tokens.` |
| Localization | **UI i18n (en-US & ko-KR)** (🟡 Partial (1)) | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. `ADR-0002 bilingual UI requirement.` |

### Narwhal (`63.8%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/idp/narwhal`
- **Archetype:** `Platform Portal` | **Category:** Internal Developer Platform
- **Gaps Identified:** 15

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🟡 Partial (1)) | Legacy filename: README_ko.md | Rename README_ko.md -> README-ko.md per ADR-0002. `ADR-0002 / rename to -ko.md` |
| Documentation | **Korean Filename Standard** (🔴 Missing (0)) | Found 4 legacy files (README_ko.md, CHANGELOG_ko.md) | Migrate legacy Korean filenames (4 files) to *-ko.md. `ADR-0002 naming standard` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | No DESIGN.md in non-UI project | Consider adding DESIGN.md declaring CLI/tool archetype. `ADR-0007 optional for headless tools.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🟡 Partial (1)) | Found CONTRIBUTING.md (missing Korean pair) | Add CONTRIBUTING-ko.md. `ADR-0002 bilingual guidance.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| Security | **SECURITY Policy (en+ko)** (🟡 Partial (1)) | Found SECURITY.md (missing Korean pair) | Add SECURITY-ko.md per ADR-0002. `Vulnerability disclosure path.` |
| Security | **Container Security Scan** (🟡 Partial (1)) | Dockerfile present without explicit container scanner in CI | Add Trivy container scanning step to CI. `Container security standard.` |
| Security | **Code Scanning / SAST** (🟡 Partial (1)) | CI present without automated SAST | Add CodeQL or language-specific static analysis. `Recommended public OSS practice.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |

### kube-ready-box (`55.6%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/kube-ready-box`
- **Archetype:** `Developer Tool` | **Category:** OS & VM Infrastructure
- **Gaps Identified:** 15

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🟡 Partial (1)) | Legacy filename: README.ko.md | Rename README.ko.md -> README-ko.md per ADR-0002. `ADR-0002 / rename to -ko.md` |
| Documentation | **Korean Filename Standard** (🔴 Missing (0)) | Found 1 legacy files (README.ko.md) | Migrate legacy Korean filenames (1 files) to *-ko.md. `ADR-0002 naming standard` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | No DESIGN.md in non-UI project | Consider adding DESIGN.md declaring CLI/tool archetype. `ADR-0007 optional for headless tools.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🟡 Partial (1)) | CI present without automated SAST | Add CodeQL or language-specific static analysis. `Recommended public OSS practice.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |

### KubeMetal (`54.8%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/kubemetal`
- **Archetype:** `Desktop Operator` | **Category:** Apple Silicon Hybrid MLOps
- **Gaps Identified:** 18

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🟡 Partial (1)) | Legacy filename: README_ko.md | Rename README_ko.md -> README-ko.md per ADR-0002. `ADR-0002 / rename to -ko.md` |
| Documentation | **Korean Filename Standard** (🔴 Missing (0)) | Found 2 legacy files (CHANGELOG.ko.md, README_ko.md) | Migrate legacy Korean filenames (2 files) to *-ko.md. `ADR-0002 naming standard` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. `ADR-0007 adoption.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| CI | **Format & Lint Check in CI** (🟡 Partial (1)) | CI present but no explicit format check detected | Add format/lint validation step to CI. `Deterministic rule enforcement.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🟡 Partial (1)) | DESIGN.md present without explicit archetype | Declare primary archetype (Desktop Operator) in DESIGN.md. `ADR-0007 archetype standard.` |
| Design System | **Semantic Token Mapping** (🟡 Partial (1)) | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. `ADR-0007 design tokens.` |
| Localization | **UI i18n (en-US & ko-KR)** (🟡 Partial (1)) | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. `ADR-0002 bilingual UI requirement.` |

### dasomel.github.io (`50.0%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/dasomel.github.io`
- **Archetype:** `Platform Portal` | **Category:** Community Tech Blog
- **Gaps Identified:** 18

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🔴 Missing (0)) | Missing Korean README | README-ko.md is missing. `Translate canonical README into README-ko.md.` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🔴 Missing (0)) | Missing DESIGN.md in UI project | Create DESIGN.md using OpenForge template with archetype and token mapping. `ADR-0007 required for UI.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| CI | **Supply Chain & Security Gates** (🟡 Partial (1)) | Standard CI present without supply chain gate | Add supply-chain and SBOM/dependency verification workflow. `ADR-0006 compliance.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🟡 Partial (1)) | CI present without automated SAST | Add CodeQL or language-specific static analysis. `Recommended public OSS practice.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🔴 Missing (0)) | Missing archetype declaration | Declare Platform Portal in DESIGN.md. `ADR-0007 design contract.` |
| Design System | **Semantic Token Mapping** (🔴 Missing (0)) | No token mapping found | Map UI tokens to OpenForge semantic tokens in DESIGN.md. `ADR-0007 semantic tokens.` |

### eGovFrame Launcher (`38.3%`)
- **Path:** `/Users/m/Documents/IdeaProjects/21.egov/egovframe-launcher`
- **Archetype:** `Developer Tool` | **Category:** eGovFrame Developer Tooling
- **Gaps Identified:** 22

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🔴 Missing (0)) | Missing Korean README | README-ko.md is missing. `Translate canonical README into README-ko.md.` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🔴 Missing (0)) | Missing DESIGN.md in UI project | Create DESIGN.md using OpenForge template with archetype and token mapping. `ADR-0007 required for UI.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| CI | **Format & Lint Check in CI** (🟡 Partial (1)) | CI present but no explicit format check detected | Add format/lint validation step to CI. `Deterministic rule enforcement.` |
| CI | **Documentation & ADR Validation** (🟡 Partial (1)) | Workflows present without dedicated doc check | Add documentation / ADR pair verification to CI. `Prevent doc drift.` |
| CI | **Supply Chain & Security Gates** (🟡 Partial (1)) | Standard CI present without supply chain gate | Add supply-chain and SBOM/dependency verification workflow. `ADR-0006 compliance.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🟡 Partial (1)) | CI present without automated SAST | Add CodeQL or language-specific static analysis. `Recommended public OSS practice.` |
| Agent Engineering | **Agent Root Contract** (🔴 Missing (0)) | No agent instruction file found | Add AGENTS.md based on OpenForge agent engineering standard. `ADR-0008 adoption.` |
| Agent Engineering | **Layered Instructions Model** (🔴 Missing (0)) | No layered agent instructions | Adopt layered instruction model. `ADR-0008 compliance.` |
| Agent Engineering | **Evidence & Convergence Rules** (🔴 Missing (0)) | No agent contract | Adopt OpenForge agent contract with convergence rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🔴 Missing (0)) | Missing archetype declaration | Declare Developer Tool in DESIGN.md. `ADR-0007 design contract.` |
| Design System | **Semantic Token Mapping** (🔴 Missing (0)) | No token mapping found | Map UI tokens to OpenForge semantic tokens in DESIGN.md. `ADR-0007 semantic tokens.` |
| Localization | **UI i18n (en-US & ko-KR)** (🟡 Partial (1)) | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. `ADR-0002 bilingual UI requirement.` |

### Kairos (`35.0%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/kairos`
- **Archetype:** `Developer Tool` | **Category:** Automated Trading Bot
- **Gaps Identified:** 23

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🔴 Missing (0)) | Missing Korean README | README-ko.md is missing. `Translate canonical README into README-ko.md.` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Release Guide & Changelog** (🔴 Missing (0)) | No release guide or changelog found | Add CHANGELOG.md and release process guide. `Follow Keep a Changelog format.` |
| Documentation | **Version Inventory** (🟡 Partial (1)) | No explicit version file | Add version inventory. `N/A for minimal prototypes.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. `ADR-0007 adoption.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| CI | **Automated CI Workflows** (🔴 Missing (0)) | No GitHub Actions workflows found | Create .github/workflows/ci.yml. `Core engineering standard.` |
| CI | **Format & Lint Check in CI** (🔴 Missing (0)) | No CI format check | Configure automated format check in CI. `Required for reproducible quality.` |
| CI | **Automated Tests in CI** (🔴 Missing (0)) | No CI test step | Add automated tests to CI. `Required for regression prevention.` |
| CI | **Documentation & ADR Validation** (🔴 Missing (0)) | No doc validation in CI | Add doc check workflow. `Recommended baseline.` |
| CI | **Supply Chain & Security Gates** (🔴 Missing (0)) | No supply chain validation | Add supply chain security workflow. `Required for secure releases.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🔴 Missing (0)) | No code scanning | Add CodeQL workflow. `Static vulnerability prevention.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🟡 Partial (1)) | DESIGN.md present without explicit archetype | Declare primary archetype (Developer Tool) in DESIGN.md. `ADR-0007 archetype standard.` |
| Design System | **Semantic Token Mapping** (🟡 Partial (1)) | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. `ADR-0007 design tokens.` |

### Beluga (`33.9%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/beluga`
- **Archetype:** `Data Control Plane` | **Category:** Data Platform IaC
- **Gaps Identified:** 20

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🔴 Missing (0)) | Missing Korean README | README-ko.md is missing. `Translate canonical README into README-ko.md.` |
| Documentation | **Architecture Document** (🟡 Partial (1)) | docs/ directory exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. `Document core architecture boundaries.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Release Guide & Changelog** (🔴 Missing (0)) | No release guide or changelog found | Add CHANGELOG.md and release process guide. `Follow Keep a Changelog format.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | No DESIGN.md in non-UI project | Consider adding DESIGN.md declaring CLI/tool archetype. `ADR-0007 optional for headless tools.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| CI | **Automated CI Workflows** (🔴 Missing (0)) | No GitHub Actions workflows found | Create .github/workflows/ci.yml. `Core engineering standard.` |
| CI | **Format & Lint Check in CI** (🔴 Missing (0)) | No CI format check | Configure automated format check in CI. `Required for reproducible quality.` |
| CI | **Automated Tests in CI** (🔴 Missing (0)) | No CI test step | Add automated tests to CI. `Required for regression prevention.` |
| CI | **Documentation & ADR Validation** (🔴 Missing (0)) | No doc validation in CI | Add doc check workflow. `Recommended baseline.` |
| CI | **Supply Chain & Security Gates** (🔴 Missing (0)) | No supply chain validation | Add supply chain security workflow. `Required for secure releases.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🔴 Missing (0)) | No code scanning | Add CodeQL workflow. `Static vulnerability prevention.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Evidence & Convergence Rules** (🟡 Partial (1)) | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. `ADR-0009 compliance.` |

### cka-lab (`13.0%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/cka-lab`
- **Archetype:** `Developer Tool` | **Category:** Certification & Lab Simulator
- **Gaps Identified:** 25

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🔴 Missing (0)) | Missing Korean README | README-ko.md is missing. `Translate canonical README into README-ko.md.` |
| Documentation | **Architecture Document** (🔴 Missing (0)) | No architecture documentation | Add architecture overview and diagram. `Required for platform & operator archetypes.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Release Guide & Changelog** (🔴 Missing (0)) | No release guide or changelog found | Add CHANGELOG.md and release process guide. `Follow Keep a Changelog format.` |
| Documentation | **Version Inventory** (🟡 Partial (1)) | No explicit version file | Add version inventory. `N/A for minimal prototypes.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🟡 Partial (1)) | No DESIGN.md in non-UI project | Consider adding DESIGN.md declaring CLI/tool archetype. `ADR-0007 optional for headless tools.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| GitHub | **License** (🔴 Missing (0)) | Missing LICENSE file | Add open source LICENSE file (e.g. Apache 2.0 / MIT). `Legal baseline.` |
| CI | **Automated CI Workflows** (🔴 Missing (0)) | No GitHub Actions workflows found | Create .github/workflows/ci.yml. `Core engineering standard.` |
| CI | **Format & Lint Check in CI** (🔴 Missing (0)) | No CI format check | Configure automated format check in CI. `Required for reproducible quality.` |
| CI | **Automated Tests in CI** (🔴 Missing (0)) | No CI test step | Add automated tests to CI. `Required for regression prevention.` |
| CI | **Automated Build in CI** (🔴 Missing (0)) | No CI build step | Add build verification to CI. `Prevent broken builds.` |
| CI | **Documentation & ADR Validation** (🔴 Missing (0)) | No doc validation in CI | Add doc check workflow. `Recommended baseline.` |
| CI | **Supply Chain & Security Gates** (🔴 Missing (0)) | No supply chain validation | Add supply chain security workflow. `Required for secure releases.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🔴 Missing (0)) | No code scanning | Add CodeQL workflow. `Static vulnerability prevention.` |
| Agent Engineering | **Agent Root Contract** (🔴 Missing (0)) | No agent instruction file found | Add AGENTS.md based on OpenForge agent engineering standard. `ADR-0008 adoption.` |
| Agent Engineering | **Layered Instructions Model** (🔴 Missing (0)) | No layered agent instructions | Adopt layered instruction model. `ADR-0008 compliance.` |
| Agent Engineering | **Evidence & Convergence Rules** (🔴 Missing (0)) | No agent contract | Adopt OpenForge agent contract with convergence rules. `ADR-0009 compliance.` |

### Beluga Manager (`12.9%`)
- **Path:** `/Users/m/Documents/IdeaProjects/20.dasomel/beluga-manager`
- **Archetype:** `Data Control Plane` | **Category:** Data Platform Management
- **Gaps Identified:** 28

| Area | Metric | Current Evidence | Action / Exception Path |
|---|---|---|---|
| Documentation | **Korean README** (🔴 Missing (0)) | Missing Korean README | README-ko.md is missing. `Translate canonical README into README-ko.md.` |
| Documentation | **Architecture Document** (🔴 Missing (0)) | No architecture documentation | Add architecture overview and diagram. `Required for platform & operator archetypes.` |
| Documentation | **Development Guide** (🔴 Missing (0)) | No development guide found | Add local development and contribution instructions. `Bootstrap from OpenForge CONTRIBUTING.md template.` |
| Documentation | **Release Guide & Changelog** (🔴 Missing (0)) | No release guide or changelog found | Add CHANGELOG.md and release process guide. `Follow Keep a Changelog format.` |
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| Architecture | **ADR Process** (🔴 Missing (0)) | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. `ADR-0001 adoption.` |
| Architecture | **DESIGN.md Contract** (🔴 Missing (0)) | Missing DESIGN.md in UI project | Create DESIGN.md using OpenForge template with archetype and token mapping. `ADR-0007 required for UI.` |
| GitHub | **PR Template** (🔴 Missing (0)) | Missing PR template | Add .github/pull_request_template.md. `Use OpenForge PR template baseline.` |
| GitHub | **Issue Templates** (🔴 Missing (0)) | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. `Use OpenForge templates.` |
| GitHub | **Contributing Guide (en+ko)** (🔴 Missing (0)) | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. `Use OpenForge template.` |
| GitHub | **Code of Conduct** (🔴 Missing (0)) | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. `OpenForge standard policy.` |
| GitHub | **License** (🔴 Missing (0)) | Missing LICENSE file | Add open source LICENSE file (e.g. Apache 2.0 / MIT). `Legal baseline.` |
| CI | **Automated CI Workflows** (🔴 Missing (0)) | No GitHub Actions workflows found | Create .github/workflows/ci.yml. `Core engineering standard.` |
| CI | **Format & Lint Check in CI** (🔴 Missing (0)) | No CI format check | Configure automated format check in CI. `Required for reproducible quality.` |
| CI | **Automated Tests in CI** (🔴 Missing (0)) | No CI test step | Add automated tests to CI. `Required for regression prevention.` |
| CI | **Automated Build in CI** (🔴 Missing (0)) | No CI build step | Add build verification to CI. `Prevent broken builds.` |
| CI | **Documentation & ADR Validation** (🔴 Missing (0)) | No doc validation in CI | Add doc check workflow. `Recommended baseline.` |
| CI | **Supply Chain & Security Gates** (🔴 Missing (0)) | No supply chain validation | Add supply chain security workflow. `Required for secure releases.` |
| Security | **Dependency Update Automation** (🔴 Missing (0)) | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. `Continuous vulnerability management.` |
| Security | **SECURITY Policy (en+ko)** (🔴 Missing (0)) | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. `OpenForge security standard.` |
| Security | **Code Scanning / SAST** (🔴 Missing (0)) | No code scanning | Add CodeQL workflow. `Static vulnerability prevention.` |
| Security | **.env.example Template** (🔴 Missing (0)) | Missing .env.example | Provide .env.example with sanitized placeholder secrets. `Prevent accidental credential exposure.` |
| Agent Engineering | **Agent Root Contract** (🔴 Missing (0)) | No agent instruction file found | Add AGENTS.md based on OpenForge agent engineering standard. `ADR-0008 adoption.` |
| Agent Engineering | **Layered Instructions Model** (🔴 Missing (0)) | No layered agent instructions | Adopt layered instruction model. `ADR-0008 compliance.` |
| Agent Engineering | **Evidence & Convergence Rules** (🔴 Missing (0)) | No agent contract | Adopt OpenForge agent contract with convergence rules. `ADR-0009 compliance.` |
| Design System | **Product Archetype Declaration** (🔴 Missing (0)) | Missing archetype declaration | Declare Data Control Plane in DESIGN.md. `ADR-0007 design contract.` |
| Design System | **Semantic Token Mapping** (🔴 Missing (0)) | No token mapping found | Map UI tokens to OpenForge semantic tokens in DESIGN.md. `ADR-0007 semantic tokens.` |
| Localization | **UI i18n (en-US & ko-KR)** (🟡 Partial (1)) | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. `ADR-0002 bilingual UI requirement.` |

## 3. Recommended Remediation Order

1. **Bilingual Filename Parity (ADR-0002)**: Migrate remaining legacy `_ko.md` and `.ko.md` files to `-ko.md` in `narwhal`, `narwhal-portal`, `kubemetal`, `nfs-quota-agent`, `ldapium`, `kube-ready-box`.
2. **DESIGN.md & Archetype Adoption (ADR-0007)**: Establish root `DESIGN.md` declaring semantic token mappings in `clusterdeck`, `beluga-manager`, `ldapium`, and `dasomel.github.io`.
3. **Root Agent Contract (ADR-0008, ADR-0009)**: Add concise `AGENTS.md` to `beluga-manager`, `cka-lab`, and `egovframe-launcher`.
4. **CI Supply Chain & Branch Protection (ADR-0003, ADR-0006)**: Configure required status checks on `main` and supply chain verification across all active repositories.
