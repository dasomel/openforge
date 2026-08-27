# chore(compliance): align with OpenForge standards (38.3% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — eGovFrame Launcher

**Current Score:** `38.3%` (23/60 points)
**Maturity Status:** Foundation work required
**Product Archetype:** Developer Tool

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Missing Korean README
- **Target Standard:** README-ko.md present
- **Action Required:** README-ko.md is missing.
- **Guidance / Exception Path:** `Translate canonical README into README-ko.md.`

#### 2. [Documentation] Architecture Document
- **Current Evidence:** docs/ directory exists without dedicated architecture doc
- **Target Standard:** docs/architecture*.md
- **Action Required:** Add architecture documentation in docs/architecture.md.
- **Guidance / Exception Path:** `Document core architecture boundaries.`

#### 3. [Documentation] Development Guide
- **Current Evidence:** No development guide found
- **Target Standard:** docs/development.md / CONTRIBUTING.md
- **Action Required:** Add local development and contribution instructions.
- **Guidance / Exception Path:** `Bootstrap from OpenForge CONTRIBUTING.md template.`

#### 4. [Documentation] Lessons & Mistakes Log
- **Current Evidence:** No dedicated lessons log (optional)
- **Target Standard:** lessons-log.md / mistakes-log.md
- **Action Required:** Maintain a lessons/mistakes log for operational retention.
- **Guidance / Exception Path:** `Optional reference practice.`

#### 5. [Architecture] ADR Process
- **Current Evidence:** No ADR records found
- **Target Standard:** docs/adr/ directory with records
- **Action Required:** Introduce docs/adr/ and record durable cross-cutting decisions.
- **Guidance / Exception Path:** `ADR-0001 adoption.`

#### 6. [Architecture] DESIGN.md Contract
- **Current Evidence:** Missing DESIGN.md in UI project
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Create DESIGN.md using OpenForge template with archetype and token mapping.
- **Guidance / Exception Path:** `ADR-0007 required for UI.`

#### 7. [GitHub] PR Template
- **Current Evidence:** Missing PR template
- **Target Standard:** .github/pull_request_template.md
- **Action Required:** Add .github/pull_request_template.md.
- **Guidance / Exception Path:** `Use OpenForge PR template baseline.`

#### 8. [GitHub] Issue Templates
- **Current Evidence:** No issue templates found
- **Target Standard:** Bug & Feature issue templates
- **Action Required:** Create .github/ISSUE_TEMPLATE/ for bug reports and features.
- **Guidance / Exception Path:** `Use OpenForge templates.`

#### 9. [GitHub] Contributing Guide (en+ko)
- **Current Evidence:** Missing CONTRIBUTING.md
- **Target Standard:** CONTRIBUTING.md + CONTRIBUTING-ko.md
- **Action Required:** Add CONTRIBUTING.md and CONTRIBUTING-ko.md.
- **Guidance / Exception Path:** `Use OpenForge template.`

#### 10. [GitHub] Code of Conduct
- **Current Evidence:** Missing CODE_OF_CONDUCT.md
- **Target Standard:** CODE_OF_CONDUCT.md
- **Action Required:** Add CODE_OF_CONDUCT.md.
- **Guidance / Exception Path:** `OpenForge standard policy.`

#### 11. [CI] Format & Lint Check in CI
- **Current Evidence:** CI present but no explicit format check detected
- **Target Standard:** Automated format/lint step
- **Action Required:** Add format/lint validation step to CI.
- **Guidance / Exception Path:** `Deterministic rule enforcement.`

#### 12. [CI] Documentation & ADR Validation
- **Current Evidence:** Workflows present without dedicated doc check
- **Target Standard:** Doc/ADR validation step in CI
- **Action Required:** Add documentation / ADR pair verification to CI.
- **Guidance / Exception Path:** `Prevent doc drift.`

#### 13. [CI] Supply Chain & Security Gates
- **Current Evidence:** Standard CI present without supply chain gate
- **Target Standard:** Supply chain / SBOM / Policy gate in CI
- **Action Required:** Add supply-chain and SBOM/dependency verification workflow.
- **Guidance / Exception Path:** `ADR-0006 compliance.`

#### 14. [Security] Dependency Update Automation
- **Current Evidence:** Missing Dependabot/Renovate configuration
- **Target Standard:** Dependabot/Renovate config
- **Action Required:** Add .github/dependabot.yml for automated dependency security updates.
- **Guidance / Exception Path:** `Continuous vulnerability management.`

#### 15. [Security] SECURITY Policy (en+ko)
- **Current Evidence:** Missing SECURITY.md
- **Target Standard:** SECURITY.md + SECURITY-ko.md
- **Action Required:** Add SECURITY.md outlining responsible vulnerability disclosure.
- **Guidance / Exception Path:** `OpenForge security standard.`

#### 16. [Security] Code Scanning / SAST
- **Current Evidence:** CI present without automated SAST
- **Target Standard:** CodeQL or SAST in CI
- **Action Required:** Add CodeQL or language-specific static analysis.
- **Guidance / Exception Path:** `Recommended public OSS practice.`

#### 17. [Agent Engineering] Agent Root Contract
- **Current Evidence:** No agent instruction file found
- **Target Standard:** AGENTS.md / CLAUDE.md
- **Action Required:** Add AGENTS.md based on OpenForge agent engineering standard.
- **Guidance / Exception Path:** `ADR-0008 adoption.`

#### 18. [Agent Engineering] Layered Instructions Model
- **Current Evidence:** No layered agent instructions
- **Target Standard:** Concise root + CODING_STANDARDS.md
- **Action Required:** Adopt layered instruction model.
- **Guidance / Exception Path:** `ADR-0008 compliance.`

#### 19. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** No agent contract
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Adopt OpenForge agent contract with convergence rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

#### 20. [Design System] Product Archetype Declaration
- **Current Evidence:** Missing archetype declaration
- **Target Standard:** Archetype declared in DESIGN.md
- **Action Required:** Declare Developer Tool in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 design contract.`

#### 21. [Design System] Semantic Token Mapping
- **Current Evidence:** No token mapping found
- **Target Standard:** OpenForge token aliases in DESIGN.md
- **Action Required:** Map UI tokens to OpenForge semantic tokens in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 semantic tokens.`

#### 22. [Localization] UI i18n (en-US & ko-KR)
- **Current Evidence:** UI project without explicit locale resource directory
- **Target Standard:** Locale resources for UI
- **Action Required:** Configure en-US and ko-KR i18n resources.
- **Guidance / Exception Path:** `ADR-0002 bilingual UI requirement.`

### Verification Checklist

- [ ] Update filenames to `-ko.md` format where applicable (ADR-0002)
- [ ] Introduce/Update `AGENTS.md` and `DESIGN.md` contracts
- [ ] Ensure CI runs format, test, and supply-chain verification
- [ ] Document intentional exceptions in an ADR if required (ADR-0012)

> Automated by OpenForge Portfolio Compliance Auditor
