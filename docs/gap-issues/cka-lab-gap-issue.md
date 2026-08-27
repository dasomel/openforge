# chore(compliance): align with OpenForge standards (13.0% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — cka-lab

**Current Score:** `13.0%` (7/54 points)
**Maturity Status:** Foundation work required
**Product Archetype:** Developer Tool

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Missing Korean README
- **Target Standard:** README-ko.md present
- **Action Required:** README-ko.md is missing.
- **Guidance / Exception Path:** `Translate canonical README into README-ko.md.`

#### 2. [Documentation] Architecture Document
- **Current Evidence:** No architecture documentation
- **Target Standard:** docs/architecture*.md
- **Action Required:** Add architecture overview and diagram.
- **Guidance / Exception Path:** `Required for platform & operator archetypes.`

#### 3. [Documentation] Development Guide
- **Current Evidence:** No development guide found
- **Target Standard:** docs/development.md / CONTRIBUTING.md
- **Action Required:** Add local development and contribution instructions.
- **Guidance / Exception Path:** `Bootstrap from OpenForge CONTRIBUTING.md template.`

#### 4. [Documentation] Release Guide & Changelog
- **Current Evidence:** No release guide or changelog found
- **Target Standard:** RELEASING.md / CHANGELOG.md
- **Action Required:** Add CHANGELOG.md and release process guide.
- **Guidance / Exception Path:** `Follow Keep a Changelog format.`

#### 5. [Documentation] Version Inventory
- **Current Evidence:** No explicit version file
- **Target Standard:** VERSIONS.md / manifest
- **Action Required:** Add version inventory.
- **Guidance / Exception Path:** `N/A for minimal prototypes.`

#### 6. [Documentation] Lessons & Mistakes Log
- **Current Evidence:** No dedicated lessons log (optional)
- **Target Standard:** lessons-log.md / mistakes-log.md
- **Action Required:** Maintain a lessons/mistakes log for operational retention.
- **Guidance / Exception Path:** `Optional reference practice.`

#### 7. [Architecture] ADR Process
- **Current Evidence:** No ADR records found
- **Target Standard:** docs/adr/ directory with records
- **Action Required:** Introduce docs/adr/ and record durable cross-cutting decisions.
- **Guidance / Exception Path:** `ADR-0001 adoption.`

#### 8. [Architecture] DESIGN.md Contract
- **Current Evidence:** No DESIGN.md in non-UI project
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Consider adding DESIGN.md declaring CLI/tool archetype.
- **Guidance / Exception Path:** `ADR-0007 optional for headless tools.`

#### 9. [GitHub] PR Template
- **Current Evidence:** Missing PR template
- **Target Standard:** .github/pull_request_template.md
- **Action Required:** Add .github/pull_request_template.md.
- **Guidance / Exception Path:** `Use OpenForge PR template baseline.`

#### 10. [GitHub] Issue Templates
- **Current Evidence:** No issue templates found
- **Target Standard:** Bug & Feature issue templates
- **Action Required:** Create .github/ISSUE_TEMPLATE/ for bug reports and features.
- **Guidance / Exception Path:** `Use OpenForge templates.`

#### 11. [GitHub] Contributing Guide (en+ko)
- **Current Evidence:** Missing CONTRIBUTING.md
- **Target Standard:** CONTRIBUTING.md + CONTRIBUTING-ko.md
- **Action Required:** Add CONTRIBUTING.md and CONTRIBUTING-ko.md.
- **Guidance / Exception Path:** `Use OpenForge template.`

#### 12. [GitHub] Code of Conduct
- **Current Evidence:** Missing CODE_OF_CONDUCT.md
- **Target Standard:** CODE_OF_CONDUCT.md
- **Action Required:** Add CODE_OF_CONDUCT.md.
- **Guidance / Exception Path:** `OpenForge standard policy.`

#### 13. [GitHub] License
- **Current Evidence:** Missing LICENSE file
- **Target Standard:** LICENSE file present
- **Action Required:** Add open source LICENSE file (e.g. Apache 2.0 / MIT).
- **Guidance / Exception Path:** `Legal baseline.`

#### 14. [CI] Automated CI Workflows
- **Current Evidence:** No GitHub Actions workflows found
- **Target Standard:** .github/workflows/*.yml
- **Action Required:** Create .github/workflows/ci.yml.
- **Guidance / Exception Path:** `Core engineering standard.`

#### 15. [CI] Format & Lint Check in CI
- **Current Evidence:** No CI format check
- **Target Standard:** Automated format/lint step
- **Action Required:** Configure automated format check in CI.
- **Guidance / Exception Path:** `Required for reproducible quality.`

#### 16. [CI] Automated Tests in CI
- **Current Evidence:** No CI test step
- **Target Standard:** Automated test execution in CI
- **Action Required:** Add automated tests to CI.
- **Guidance / Exception Path:** `Required for regression prevention.`

#### 17. [CI] Automated Build in CI
- **Current Evidence:** No CI build step
- **Target Standard:** Build validation step in CI
- **Action Required:** Add build verification to CI.
- **Guidance / Exception Path:** `Prevent broken builds.`

#### 18. [CI] Documentation & ADR Validation
- **Current Evidence:** No doc validation in CI
- **Target Standard:** Doc/ADR validation step in CI
- **Action Required:** Add doc check workflow.
- **Guidance / Exception Path:** `Recommended baseline.`

#### 19. [CI] Supply Chain & Security Gates
- **Current Evidence:** No supply chain validation
- **Target Standard:** Supply chain / SBOM / Policy gate in CI
- **Action Required:** Add supply chain security workflow.
- **Guidance / Exception Path:** `Required for secure releases.`

#### 20. [Security] Dependency Update Automation
- **Current Evidence:** Missing Dependabot/Renovate configuration
- **Target Standard:** Dependabot/Renovate config
- **Action Required:** Add .github/dependabot.yml for automated dependency security updates.
- **Guidance / Exception Path:** `Continuous vulnerability management.`

#### 21. [Security] SECURITY Policy (en+ko)
- **Current Evidence:** Missing SECURITY.md
- **Target Standard:** SECURITY.md + SECURITY-ko.md
- **Action Required:** Add SECURITY.md outlining responsible vulnerability disclosure.
- **Guidance / Exception Path:** `OpenForge security standard.`

#### 22. [Security] Code Scanning / SAST
- **Current Evidence:** No code scanning
- **Target Standard:** CodeQL or SAST in CI
- **Action Required:** Add CodeQL workflow.
- **Guidance / Exception Path:** `Static vulnerability prevention.`

#### 23. [Agent Engineering] Agent Root Contract
- **Current Evidence:** No agent instruction file found
- **Target Standard:** AGENTS.md / CLAUDE.md
- **Action Required:** Add AGENTS.md based on OpenForge agent engineering standard.
- **Guidance / Exception Path:** `ADR-0008 adoption.`

#### 24. [Agent Engineering] Layered Instructions Model
- **Current Evidence:** No layered agent instructions
- **Target Standard:** Concise root + CODING_STANDARDS.md
- **Action Required:** Adopt layered instruction model.
- **Guidance / Exception Path:** `ADR-0008 compliance.`

#### 25. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** No agent contract
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Adopt OpenForge agent contract with convergence rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

### Verification Checklist

- [ ] Update filenames to `-ko.md` format where applicable (ADR-0002)
- [ ] Introduce/Update `AGENTS.md` and `DESIGN.md` contracts
- [ ] Ensure CI runs format, test, and supply-chain verification
- [ ] Document intentional exceptions in an ADR if required (ADR-0012)

> Automated by OpenForge Portfolio Compliance Auditor
