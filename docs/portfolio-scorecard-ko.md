# OpenForge 포트폴리오 컴플라이언스 스코어카드

> OpenForge 엔지니어링 표준을 기준으로 Dasomel 활성 OSS 리포지토리를 자동 진단한 스코어카드입니다.

**전체 포트폴리오 평균 완성도:** `52.6%`
**진단 대상 리포지토리:** 14 projects

## 1. 포트폴리오 성숙도 순위

| 리포지토리 | 분류 | 아키타입 | 점수 | 성숙도 상태 |
|---|---|---|---:|---|
| **OpenForge** | Standards & Blueprints | `Developer Tool` | 🟢 **96.7%** (58/60) | 프로덕션 레디 기반 (90%+) |
| **ldapium** | Identity & Directory Service | `Admin Console` | 🟡 **76.6%** (49/64) | 양호 / 경미한 Gap (75-89%) |
| **ClusterDeck** | Kubernetes Operations | `Operations Dashboard` | 🟠 **68.8%** (44/64) | 개선 권장 (60-74%) |
| **NFS Quota Agent** | Storage & Kubernetes Controllers | `Developer Tool` | 🟠 **66.1%** (41/62) | 개선 권장 (60-74%) |
| **Narwhal Portal** | Internal Developer Platform | `Platform Portal` | 🟠 **64.1%** (41/64) | 개선 권장 (60-74%) |
| **Narwhal** | Internal Developer Platform | `Platform Portal` | 🟠 **63.8%** (37/58) | 개선 권장 (60-74%) |
| **kube-ready-box** | OS & VM Infrastructure | `Developer Tool` | 🔴 **55.6%** (30/54) | 기반 작업 필요 (<60%) |
| **KubeMetal** | Apple Silicon Hybrid MLOps | `Desktop Operator` | 🔴 **54.8%** (34/62) | 기반 작업 필요 (<60%) |
| **dasomel.github.io** | Community Tech Blog | `Platform Portal` | 🔴 **50.0%** (31/62) | 기반 작업 필요 (<60%) |
| **eGovFrame Launcher** | eGovFrame Developer Tooling | `Developer Tool` | 🔴 **38.3%** (23/60) | 기반 작업 필요 (<60%) |
| **Kairos** | Automated Trading Bot | `Developer Tool` | 🔴 **35.0%** (21/60) | 기반 작업 필요 (<60%) |
| **Beluga** | Data Platform IaC | `Data Control Plane` | 🔴 **33.9%** (19/56) | 기반 작업 필요 (<60%) |
| **cka-lab** | Certification & Lab Simulator | `Developer Tool` | 🔴 **13.0%** (7/54) | 기반 작업 필요 (<60%) |
| **Beluga Manager** | Data Platform Management | `Data Control Plane` | 🔴 **12.9%** (8/62) | 기반 작업 필요 (<60%) |

## 2. 요구사항 추적 및 리포지토리별 Gap 요약

### OpenForge (`96.7%`)
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/openforge`
- **아키타입:** `Developer Tool` | **분류:** Standards & Blueprints
- **식별된 Gap 건수:** 2

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
|---|---|---|---|
| Documentation | **Lessons & Mistakes Log** (🟡 Partial (1)) | No dedicated lessons log (optional) | Maintain a lessons/mistakes log for operational retention. `Optional reference practice.` |
| CI | **Format & Lint Check in CI** (🟡 Partial (1)) | CI present but no explicit format check detected | Add format/lint validation step to CI. `Deterministic rule enforcement.` |

### ldapium (`76.6%`)
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/ldapium`
- **아키타입:** `Admin Console` | **분류:** Identity & Directory Service
- **식별된 Gap 건수:** 10

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/clusterdeck`
- **아키타입:** `Operations Dashboard` | **분류:** Kubernetes Operations
- **식별된 Gap 건수:** 14

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/nfs-quota-agent`
- **아키타입:** `Developer Tool` | **분류:** Storage & Kubernetes Controllers
- **식별된 Gap 건수:** 14

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/idp/narwhal-portal`
- **아키타입:** `Platform Portal` | **분류:** Internal Developer Platform
- **식별된 Gap 건수:** 16

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/idp/narwhal`
- **아키타입:** `Platform Portal` | **분류:** Internal Developer Platform
- **식별된 Gap 건수:** 15

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/kube-ready-box`
- **아키타입:** `Developer Tool` | **분류:** OS & VM Infrastructure
- **식별된 Gap 건수:** 15

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/kubemetal`
- **아키타입:** `Desktop Operator` | **분류:** Apple Silicon Hybrid MLOps
- **식별된 Gap 건수:** 18

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/dasomel.github.io`
- **아키타입:** `Platform Portal` | **분류:** Community Tech Blog
- **식별된 Gap 건수:** 18

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/21.egov/egovframe-launcher`
- **아키타입:** `Developer Tool` | **분류:** eGovFrame Developer Tooling
- **식별된 Gap 건수:** 22

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/kairos`
- **아키타입:** `Developer Tool` | **분류:** Automated Trading Bot
- **식별된 Gap 건수:** 23

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/beluga`
- **아키타입:** `Data Control Plane` | **분류:** Data Platform IaC
- **식별된 Gap 건수:** 20

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/cka-lab`
- **아키타입:** `Developer Tool` | **분류:** Certification & Lab Simulator
- **식별된 Gap 건수:** 25

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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
- **경로:** `/Users/m/Documents/IdeaProjects/20.dasomel/beluga-manager`
- **아키타입:** `Data Control Plane` | **분류:** Data Platform Management
- **식별된 Gap 건수:** 28

| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |
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

## 3. 권장 후속 개선 순서

1. **영한 파일명 표준화 (ADR-0002)**: `narwhal`, `narwhal-portal`, `kubemetal`, `nfs-quota-agent`, `ldapium`, `kube-ready-box` 내 레거시 `_ko.md` / `.ko.md`를 `-ko.md`로 정리.
2. **DESIGN.md 및 아키타입 적용 (ADR-0007)**: `clusterdeck`, `beluga-manager`, `ldapium`, `dasomel.github.io`에 시맨틱 토큰 매핑 및 아키타입을 명시한 `DESIGN.md` 수립.
3. **에이전트 계약 수립 (ADR-0008, ADR-0009)**: `beluga-manager`, `cka-lab`, `egovframe-launcher`에 간결한 `AGENTS.md` 루트 계약 배치.
4. **CI 공급망 게이트 및 Branch Protection (ADR-0003, ADR-0006)**: `main` 브랜치에 필수 상태 검사 및 공급망 검증 워크플로 구성.
