# OpenForge Portfolio Compliance Scorecard

> Automated audit of active Dasomel OSS repositories against OpenForge engineering standards.
> Evaluates 35 standard metrics with project-specific applicability (scored 0/1/2; non-applicable metrics are N/A).

**OpenForge Standard Maturity:** `96.9%`  
**Portfolio Adoption Baseline:** `70.6%`  
*(Note: 70.6% is portfolio adoption of OpenForge standards across 14 active projects, not the implementation completeness of OpenForge itself.)*

## Baseline Comparison

- **Portfolio Score:** `68.0%` → `70.6%` (**+2.6%**)

## 1. Portfolio Maturity Ranking

| Repository | Category | Archetype | Score | Metrics (Earned/Possible) | Maturity Status |
|---|---|---|---:|---:|---|
| **dasomel/openforge** | Standards & Blueprints | `Developer Tool` | 🟢 **96.9%** | 62/64 (32 applicable) | Production-ready OSS foundation |
| **dasomel/ldapium** | Identity & Directory Service | `Admin Console` | 🟡 **89.7%** | 61/68 (34 applicable) | Healthy / minor gaps |
| **dasomel/dasomel.github.io** | Community Tech Blog | `Platform Portal` | 🟡 **89.7%** | 61/68 (34 applicable) | Healthy / minor gaps |
| **dasomel/kubemetal** | Apple Silicon Hybrid MLOps | `Desktop Operator` | 🟡 **88.2%** | 60/68 (34 applicable) | Healthy / minor gaps |
| **dasomel/egovframe-launcher** | eGovFrame Developer Tooling | `Developer Tool` | 🟡 **87.9%** | 58/66 (33 applicable) | Healthy / minor gaps |
| **dasomel/kube-ready-box** | OS & VM Infrastructure | `Developer Tool` | 🟡 **87.1%** | 54/62 (31 applicable) | Healthy / minor gaps |
| **dasomel/narwhal-portal** | Internal Developer Platform | `Platform Portal` | 🟡 **83.8%** | 57/68 (34 applicable) | Healthy / minor gaps |
| **dasomel/clusterdeck** | Kubernetes Operations | `Operations Dashboard` | 🟡 **82.4%** | 56/68 (34 applicable) | Healthy / minor gaps |
| **dasomel/narwhal** | Internal Developer Platform | `Platform Portal` | 🟡 **81.8%** | 54/66 (33 applicable) | Healthy / minor gaps |
| **dasomel/nfs-quota-agent** | Storage & Kubernetes Controllers | `Developer Tool` | 🟡 **81.8%** | 54/66 (33 applicable) | Healthy / minor gaps |
| **dasomel/kairos** | Automated Trading Bot | `Developer Tool` | 🔴 **35.9%** | 23/64 (32 applicable) | Foundation work required |
| **dasomel/beluga** | Data Platform IaC | `Data Control Plane` | 🔴 **33.3%** | 20/60 (30 applicable) | Foundation work required |
| **dasomel/cka-lab** | Certification & Lab Simulator | `Developer Tool` | 🔴 **19.6%** | 11/56 (28 applicable) | Foundation work required |
| **dasomel/beluga-manager** | Data Platform Management | `Data Control Plane` | 🔴 **15.6%** | 10/64 (32 applicable) | Foundation work required |

## 2. Top Portfolio Remediation Priorities

| Priority | Metric ID | Area | Action Item | Related ADR | Affected Projects |
|---|---|---|---|---|---|
| `P0` | `CI-006` | CI | **Supply Chain & Security Gates in CI** | `ADR-0006` | `dasomel.github.io`, `egovframe-launcher`, `clusterdeck`, `kairos` +3 (7 repos) |
| `P0` | `CI-001` | CI | **Automated CI Workflows** | `ADR-0011` | `kairos`, `beluga`, `cka-lab`, `beluga-manager` (4 repos) |
| `P0` | `CI-003` | CI | **Automated Tests in CI** | `ADR-0009` | `kairos`, `beluga`, `cka-lab`, `beluga-manager` (4 repos) |
| `P0` | `SEC-001` | Security | **Dependency Update Automation** | `ADR-0006` | `kairos`, `beluga`, `cka-lab`, `beluga-manager` (4 repos) |
| `P0` | `SEC-002` | Security | **SECURITY Policy (Bilingual)** | `ADR-0003` | `kairos`, `beluga`, `cka-lab`, `beluga-manager` (4 repos) |
| `P0` | `GH-005` | GitHub | **License** | `ADR-0003` | `cka-lab`, `beluga-manager` (2 repos) |
| `P0` | `CI-004` | CI | **Automated Build in CI** | `ADR-0006` | `cka-lab`, `beluga-manager` (2 repos) |
| `P1` | `DOC-005` | Documentation | **Architecture Document** | `ADR-0001` | `ldapium`, `dasomel.github.io`, `kubemetal`, `egovframe-launcher` +7 (11 repos) |

## 3. Requirement Traceability & Gap Summary

### dasomel/openforge (`96.9%`)
- **Path:** `<workspace>/openforge`
- **Archetype:** `Developer Tool` | **Profile:** `documentation` | **Category:** Standards & Blueprints
- **Gaps Identified:** 2

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-004` (🟡 1) | `P2` | Documentation | 83/179 docs have Korean counterparts (46%) | Add Korean pairs for key docs. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |

### dasomel/ldapium (`89.7%`)
- **Path:** `<workspace>/ldapium`
- **Archetype:** `Admin Console` | **Profile:** `standard` | **Category:** Identity & Directory Service
- **Gaps Identified:** 6

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 2/12 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🟡 1) | `P1` | Architecture | No ADR records found (single-purpose project) | Adopt docs/adr/ when cross-cutting decisions arise. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `I18N-001` (🟡 1) | `P2` | Localization | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. |

### dasomel/dasomel.github.io (`89.7%`)
- **Path:** `<workspace>/dasomel.github.io`
- **Archetype:** `Platform Portal` | **Profile:** `documentation` | **Category:** Community Tech Blog
- **Gaps Identified:** 6

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 2/24 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `CI-006` (🟡 1) | `P0` | CI | Standard CI present without supply chain gate | Add supply-chain and SBOM/dependency verification workflow. |
| `SEC-004` (🟡 1) | `P1` | Security | CI present without automated SAST | Add CodeQL or language-specific static analysis. |
| `AGENT-003` (🟡 1) | `P1` | Agent Engineering | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. |

### dasomel/kubemetal (`88.2%`)
- **Path:** `<workspace>/kubemetal`
- **Archetype:** `Desktop Operator` | **Profile:** `desktop` | **Category:** Apple Silicon Hybrid MLOps
- **Gaps Identified:** 7

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 2/55 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `ARCH-004` (🟡 1) | `P1` | Architecture | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. |
| `CI-002` (🟡 1) | `P1` | CI | CI present but no explicit format check detected | Add format/lint validation step to CI. |
| `DESIGN-001` (🟡 1) | `P1` | Design System | DESIGN.md present without explicit archetype | Declare primary archetype (Desktop Operator) in DESIGN.md. |
| `DESIGN-002` (🟡 1) | `P2` | Design System | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. |
| `I18N-001` (🟡 1) | `P2` | Localization | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. |

### dasomel/egovframe-launcher (`87.9%`)
- **Path:** `<workspace>/../21.egov/egovframe-launcher`
- **Archetype:** `Developer Tool` | **Profile:** `standard` | **Category:** eGovFrame Developer Tooling
- **Gaps Identified:** 8

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `CI-002` (🟡 1) | `P1` | CI | CI present but no explicit format check detected | Add format/lint validation step to CI. |
| `CI-005` (🟡 1) | `P2` | CI | Workflows present without dedicated doc check | Add documentation / ADR pair verification to CI. |
| `CI-006` (🟡 1) | `P0` | CI | Standard CI present without supply chain gate | Add supply-chain and SBOM/dependency verification workflow. |
| `SEC-004` (🟡 1) | `P1` | Security | CI present without automated SAST | Add CodeQL or language-specific static analysis. |
| `AGENT-002` (🟡 1) | `P2` | Agent Engineering | Single contract without layered separation | Consider splitting detailed rules to CODING_STANDARDS.md. |
| `I18N-001` (🟡 1) | `P2` | Localization | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. |

### dasomel/kube-ready-box (`87.1%`)
- **Path:** `<workspace>/kube-ready-box`
- **Archetype:** `Developer Tool` | **Profile:** `standard` | **Category:** OS & VM Infrastructure
- **Gaps Identified:** 7

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 0/44 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🟡 1) | `P1` | Architecture | No ADR records found (single-purpose project) | Adopt docs/adr/ when cross-cutting decisions arise. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `SEC-004` (🟡 1) | `P1` | Security | CI present without automated SAST | Add CodeQL or language-specific static analysis. |
| `AGENT-003` (🟡 1) | `P1` | Agent Engineering | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. |

### dasomel/narwhal-portal (`83.8%`)
- **Path:** `<workspace>/idp/narwhal-portal`
- **Archetype:** `Platform Portal` | **Profile:** `desktop` | **Category:** Internal Developer Platform
- **Gaps Identified:** 8

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-003` (🔴 0) | `P2` | Documentation | Found 4 legacy files (.claude/worktrees/agent-afae34fa5970eab3f/README_ko.md, .claude/worktrees/agent-afae34fa5970eab3f/CHANGELOG_ko.md) | Migrate legacy Korean filenames (4 files) to *-ko.md. |
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 0/26 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `ARCH-001` (🔴 0) | `P1` | Architecture | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `SEC-004` (🟡 1) | `P1` | Security | CI present without automated SAST | Add CodeQL or language-specific static analysis. |
| `DESIGN-002` (🟡 1) | `P2` | Design System | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. |
| `I18N-001` (🟡 1) | `P2` | Localization | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. |

### dasomel/clusterdeck (`82.4%`)
- **Path:** `<workspace>/clusterdeck`
- **Archetype:** `Operations Dashboard` | **Profile:** `desktop` | **Category:** Kubernetes Operations
- **Gaps Identified:** 10

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 0/11 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-002` (🔴 0) | `P1` | Architecture | 1/1 ADRs missing Korean pair | Add Korean translations for docs/adr/0001-macos-first-tauri-architecture.md. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `GH-003` (🟡 1) | `P2` | GitHub | Found CONTRIBUTING.md (missing Korean pair) | Add CONTRIBUTING-ko.md. |
| `CI-005` (🟡 1) | `P2` | CI | Workflows present without dedicated doc check | Add documentation / ADR pair verification to CI. |
| `CI-006` (🟡 1) | `P0` | CI | Standard CI present without supply chain gate | Add supply-chain and SBOM/dependency verification workflow. |
| `SEC-004` (🟡 1) | `P1` | Security | CI present without automated SAST | Add CodeQL or language-specific static analysis. |
| `AGENT-002` (🟡 1) | `P2` | Agent Engineering | Single contract without layered separation | Consider splitting detailed rules to CODING_STANDARDS.md. |
| `I18N-001` (🟡 1) | `P2` | Localization | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. |

### dasomel/narwhal (`81.8%`)
- **Path:** `<workspace>/idp/narwhal`
- **Archetype:** `Platform Portal` | **Profile:** `platform` | **Category:** Internal Developer Platform
- **Gaps Identified:** 9

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-003` (🔴 0) | `P2` | Documentation | Found 1 legacy files (csp/kakao-cloud/terraform/README.ko.md) | Migrate legacy Korean filenames (1 files) to *-ko.md. |
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 0/54 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🔴 0) | `P1` | Architecture | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `GH-003` (🟡 1) | `P2` | GitHub | Found CONTRIBUTING.md (missing Korean pair) | Add CONTRIBUTING-ko.md. |
| `SEC-003` (🟡 1) | `P1` | Security | Dockerfile present without explicit container scanner in CI | Add Trivy container scanning step to CI. |
| `SEC-004` (🟡 1) | `P1` | Security | CI present without automated SAST | Add CodeQL or language-specific static analysis. |

### dasomel/nfs-quota-agent (`81.8%`)
- **Path:** `<workspace>/nfs-quota-agent`
- **Archetype:** `Developer Tool` | **Profile:** `controller` | **Category:** Storage & Kubernetes Controllers
- **Gaps Identified:** 9

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-003` (🔴 0) | `P2` | Documentation | Found 2 legacy files (docs/feature-guide_ko.md, docs/web-ui_ko.md) | Migrate legacy Korean filenames (2 files) to *-ko.md. |
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 4/25 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🔴 0) | `P1` | Architecture | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `ARCH-004` (🟡 1) | `P1` | Architecture | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. |
| `GH-003` (🟡 1) | `P2` | GitHub | Found CONTRIBUTING.md (missing Korean pair) | Add CONTRIBUTING-ko.md. |
| `DESIGN-001` (🟡 1) | `P1` | Design System | DESIGN.md present without explicit archetype | Declare primary archetype (Developer Tool) in DESIGN.md. |
| `DESIGN-002` (🟡 1) | `P2` | Design System | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. |

### dasomel/kairos (`35.9%`)
- **Path:** `<workspace>/kairos`
- **Archetype:** `Developer Tool` | **Profile:** `standard` | **Category:** Automated Trading Bot
- **Gaps Identified:** 25

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-002` (🔴 0) | `P1` | Documentation | Missing Korean README | Translate canonical README into README-ko.md. |
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 0/6 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-006` (🔴 0) | `P2` | Documentation | No development guide found | Add local development and contribution instructions. |
| `DOC-007` (🔴 0) | `P1` | Documentation | No release guide or changelog found | Add CHANGELOG.md and release process guide. |
| `DOC-008` (🟡 1) | `P3` | Documentation | No explicit version inventory | Add VERSIONS.md or declare in project manifest. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🟡 1) | `P1` | Architecture | No ADR records found (single-purpose project) | Adopt docs/adr/ when cross-cutting decisions arise. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `ARCH-004` (🟡 1) | `P1` | Architecture | Found DESIGN.md (partial token/archetype declaration) | Expand DESIGN.md with product archetype and OpenForge semantic token map. |
| `GH-001` (🔴 0) | `P2` | GitHub | Missing PR template | Add .github/pull_request_template.md. |
| `GH-002` (🔴 0) | `P2` | GitHub | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. |
| `GH-003` (🔴 0) | `P2` | GitHub | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. |
| `GH-004` (🔴 0) | `P2` | GitHub | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. |
| `CI-001` (🔴 0) | `P0` | CI | No GitHub Actions workflows found | Create .github/workflows/ci.yml. |
| `CI-002` (🔴 0) | `P1` | CI | No CI format check | Configure automated format check in CI. |
| `CI-003` (🔴 0) | `P0` | CI | No CI test step | Add automated tests to CI. |
| `CI-005` (🔴 0) | `P2` | CI | No doc validation in CI | Add doc check workflow. |
| `CI-006` (🔴 0) | `P0` | CI | No supply chain validation | Add supply chain security workflow. |
| `SEC-001` (🔴 0) | `P0` | Security | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. |
| `SEC-002` (🔴 0) | `P0` | Security | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. |
| `SEC-004` (🔴 0) | `P1` | Security | No code scanning | Add CodeQL workflow. |
| `AGENT-003` (🟡 1) | `P1` | Agent Engineering | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. |
| `DESIGN-001` (🟡 1) | `P1` | Design System | DESIGN.md present without explicit archetype | Declare primary archetype (Developer Tool) in DESIGN.md. |
| `DESIGN-002` (🟡 1) | `P2` | Design System | DESIGN.md present without complete token mapping | Map project color/surface tokens to OpenForge semantic roles. |

### dasomel/beluga (`33.3%`)
- **Path:** `<workspace>/beluga`
- **Archetype:** `Data Control Plane` | **Profile:** `platform` | **Category:** Data Platform IaC
- **Gaps Identified:** 22

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-002` (🔴 0) | `P1` | Documentation | Missing Korean README | Translate canonical README into README-ko.md. |
| `DOC-004` (🔴 0) | `P2` | Documentation | Only 0/10 docs paired | Provide Korean translations for documents in docs/. |
| `DOC-005` (🟡 1) | `P1` | Documentation | docs/ exists without dedicated architecture doc | Add architecture documentation in docs/architecture.md. |
| `DOC-006` (🔴 0) | `P2` | Documentation | No development guide found | Add local development and contribution instructions. |
| `DOC-007` (🔴 0) | `P1` | Documentation | No release guide or changelog found | Add CHANGELOG.md and release process guide. |
| `ARCH-001` (🔴 0) | `P1` | Architecture | No ADR records found | Introduce docs/adr/ and record durable cross-cutting decisions. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `ARCH-004` (🟡 1) | `P1` | Architecture | No DESIGN.md in headless/non-UI project | Consider adding DESIGN.md declaring CLI/tool archetype. |
| `GH-001` (🔴 0) | `P2` | GitHub | Missing PR template | Add .github/pull_request_template.md. |
| `GH-002` (🔴 0) | `P2` | GitHub | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. |
| `GH-003` (🔴 0) | `P2` | GitHub | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. |
| `GH-004` (🔴 0) | `P2` | GitHub | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. |
| `CI-001` (🔴 0) | `P0` | CI | No GitHub Actions workflows found | Create .github/workflows/ci.yml. |
| `CI-002` (🔴 0) | `P1` | CI | No CI format check | Configure automated format check in CI. |
| `CI-003` (🔴 0) | `P0` | CI | No CI test step | Add automated tests to CI. |
| `CI-005` (🔴 0) | `P2` | CI | No doc validation in CI | Add doc check workflow. |
| `CI-006` (🔴 0) | `P0` | CI | No supply chain validation | Add supply chain security workflow. |
| `SEC-001` (🔴 0) | `P0` | Security | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. |
| `SEC-002` (🔴 0) | `P0` | Security | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. |
| `SEC-004` (🔴 0) | `P1` | Security | No code scanning | Add CodeQL workflow. |
| `SEC-005` (🔴 0) | `P1` | Security | Missing .env.example | Provide .env.example with sanitized placeholder secrets. |
| `AGENT-003` (🟡 1) | `P1` | Agent Engineering | Agent contract present without explicit convergence rules | Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules. |

### dasomel/cka-lab (`19.6%`)
- **Path:** `<workspace>/cka-lab`
- **Archetype:** `Developer Tool` | **Profile:** `lab` | **Category:** Certification & Lab Simulator
- **Gaps Identified:** 26

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-002` (🔴 0) | `P1` | Documentation | Missing Korean README | Translate canonical README into README-ko.md. |
| `DOC-005` (🟡 1) | `P1` | Documentation | Non-platform repository without architecture doc | Add architecture overview. |
| `DOC-006` (🔴 0) | `P2` | Documentation | No development guide found | Add local development and contribution instructions. |
| `DOC-007` (🟡 1) | `P1` | Documentation | Lab/sandbox repository | Add CHANGELOG.md for major milestones. |
| `DOC-008` (🟡 1) | `P3` | Documentation | No explicit version inventory | Add VERSIONS.md or declare in project manifest. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🟡 1) | `P1` | Architecture | No ADR records found (single-purpose project) | Adopt docs/adr/ when cross-cutting decisions arise. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `ARCH-004` (🟡 1) | `P1` | Architecture | No DESIGN.md in headless/non-UI project | Consider adding DESIGN.md declaring CLI/tool archetype. |
| `GH-001` (🔴 0) | `P2` | GitHub | Missing PR template | Add .github/pull_request_template.md. |
| `GH-002` (🔴 0) | `P2` | GitHub | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. |
| `GH-003` (🔴 0) | `P2` | GitHub | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. |
| `GH-004` (🔴 0) | `P2` | GitHub | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. |
| `GH-005` (🔴 0) | `P0` | GitHub | Missing LICENSE file | Add open source LICENSE file (e.g. Apache 2.0 / MIT). |
| `CI-001` (🔴 0) | `P0` | CI | No GitHub Actions workflows found | Create .github/workflows/ci.yml. |
| `CI-002` (🔴 0) | `P1` | CI | No CI format check | Configure automated format check in CI. |
| `CI-003` (🔴 0) | `P0` | CI | No CI test step | Add automated tests to CI. |
| `CI-004` (🔴 0) | `P0` | CI | No CI build step | Add build verification to CI. |
| `CI-005` (🔴 0) | `P2` | CI | No doc validation in CI | Add doc check workflow. |
| `CI-006` (🔴 0) | `P0` | CI | No supply chain validation | Add supply chain security workflow. |
| `SEC-001` (🔴 0) | `P0` | Security | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. |
| `SEC-002` (🔴 0) | `P0` | Security | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. |
| `SEC-004` (🔴 0) | `P1` | Security | No code scanning | Add CodeQL workflow. |
| `AGENT-001` (🔴 0) | `P1` | Agent Engineering | No agent instruction file found | Add AGENTS.md based on OpenForge agent engineering standard. |
| `AGENT-002` (🔴 0) | `P2` | Agent Engineering | No layered agent instructions | Adopt layered instruction model. |
| `AGENT-003` (🔴 0) | `P1` | Agent Engineering | No agent contract | Adopt OpenForge agent contract with convergence rules. |

### dasomel/beluga-manager (`15.6%`)
- **Path:** `<workspace>/beluga-manager`
- **Archetype:** `Data Control Plane` | **Profile:** `standard` | **Category:** Data Platform Management
- **Gaps Identified:** 29

| Metric ID | Priority | Area | Current Evidence | Required Action |
|---|---|---|---|---|
| `DOC-002` (🔴 0) | `P1` | Documentation | Missing Korean README | Translate canonical README into README-ko.md. |
| `DOC-005` (🔴 0) | `P1` | Documentation | No architecture documentation found | Add docs/architecture.md describing core component boundaries. |
| `DOC-006` (🔴 0) | `P2` | Documentation | No development guide found | Add local development and contribution instructions. |
| `DOC-007` (🔴 0) | `P1` | Documentation | No release guide or changelog found | Add CHANGELOG.md and release process guide. |
| `DOC-009` (🟡 1) | `P3` | Documentation | No dedicated lessons log (optional reference practice) | Maintain a lessons/mistakes log for operational retention. |
| `ARCH-001` (🟡 1) | `P1` | Architecture | No ADR records found (single-purpose project) | Adopt docs/adr/ when cross-cutting decisions arise. |
| `ARCH-003` (🟡 1) | `P3` | Architecture | Decision map/standard not separate | Maintain decision traceability index in docs/adr/README.md. |
| `ARCH-004` (🔴 0) | `P1` | Architecture | Missing DESIGN.md in UI project | Create DESIGN.md using OpenForge template with archetype and token mapping. |
| `GH-001` (🔴 0) | `P2` | GitHub | Missing PR template | Add .github/pull_request_template.md. |
| `GH-002` (🔴 0) | `P2` | GitHub | No issue templates found | Create .github/ISSUE_TEMPLATE/ for bug reports and features. |
| `GH-003` (🔴 0) | `P2` | GitHub | Missing CONTRIBUTING.md | Add CONTRIBUTING.md and CONTRIBUTING-ko.md. |
| `GH-004` (🔴 0) | `P2` | GitHub | Missing CODE_OF_CONDUCT.md | Add CODE_OF_CONDUCT.md. |
| `GH-005` (🔴 0) | `P0` | GitHub | Missing LICENSE file | Add open source LICENSE file (e.g. Apache 2.0 / MIT). |
| `CI-001` (🔴 0) | `P0` | CI | No GitHub Actions workflows found | Create .github/workflows/ci.yml. |
| `CI-002` (🔴 0) | `P1` | CI | No CI format check | Configure automated format check in CI. |
| `CI-003` (🔴 0) | `P0` | CI | No CI test step | Add automated tests to CI. |
| `CI-004` (🔴 0) | `P0` | CI | No CI build step | Add build verification to CI. |
| `CI-005` (🔴 0) | `P2` | CI | No doc validation in CI | Add doc check workflow. |
| `CI-006` (🔴 0) | `P0` | CI | No supply chain validation | Add supply chain security workflow. |
| `SEC-001` (🔴 0) | `P0` | Security | Missing Dependabot/Renovate configuration | Add .github/dependabot.yml for automated dependency security updates. |
| `SEC-002` (🔴 0) | `P0` | Security | Missing SECURITY.md | Add SECURITY.md outlining responsible vulnerability disclosure. |
| `SEC-004` (🔴 0) | `P1` | Security | No code scanning | Add CodeQL workflow. |
| `SEC-005` (🔴 0) | `P1` | Security | Missing .env.example | Provide .env.example with sanitized placeholder secrets. |
| `AGENT-001` (🔴 0) | `P1` | Agent Engineering | No agent instruction file found | Add AGENTS.md based on OpenForge agent engineering standard. |
| `AGENT-002` (🔴 0) | `P2` | Agent Engineering | No layered agent instructions | Adopt layered instruction model. |
| `AGENT-003` (🔴 0) | `P1` | Agent Engineering | No agent contract | Adopt OpenForge agent contract with convergence rules. |
| `DESIGN-001` (🔴 0) | `P1` | Design System | Missing archetype declaration | Declare Data Control Plane in DESIGN.md. |
| `DESIGN-002` (🔴 0) | `P2` | Design System | No token mapping found | Map UI tokens to OpenForge semantic tokens in DESIGN.md. |
| `I18N-001` (🟡 1) | `P2` | Localization | UI project without explicit locale resource directory | Configure en-US and ko-KR i18n resources. |
