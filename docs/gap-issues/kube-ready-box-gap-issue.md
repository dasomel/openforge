# chore(compliance): align with OpenForge standards (55.6% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — kube-ready-box

**Current Score:** `55.6%` (30/54 points)
**Maturity Status:** Foundation work required
**Product Archetype:** Developer Tool

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Legacy filename: README.ko.md
- **Target Standard:** README-ko.md present
- **Action Required:** Rename README.ko.md -> README-ko.md per ADR-0002.
- **Guidance / Exception Path:** `ADR-0002 / rename to -ko.md`

#### 2. [Documentation] Korean Filename Standard
- **Current Evidence:** Found 1 legacy files (README.ko.md)
- **Target Standard:** Use <name>-ko.md format
- **Action Required:** Migrate legacy Korean filenames (1 files) to *-ko.md.
- **Guidance / Exception Path:** `ADR-0002 naming standard`

#### 3. [Documentation] Architecture Document
- **Current Evidence:** docs/ directory exists without dedicated architecture doc
- **Target Standard:** docs/architecture*.md
- **Action Required:** Add architecture documentation in docs/architecture.md.
- **Guidance / Exception Path:** `Document core architecture boundaries.`

#### 4. [Documentation] Development Guide
- **Current Evidence:** No development guide found
- **Target Standard:** docs/development.md / CONTRIBUTING.md
- **Action Required:** Add local development and contribution instructions.
- **Guidance / Exception Path:** `Bootstrap from OpenForge CONTRIBUTING.md template.`

#### 5. [Documentation] Lessons & Mistakes Log
- **Current Evidence:** No dedicated lessons log (optional)
- **Target Standard:** lessons-log.md / mistakes-log.md
- **Action Required:** Maintain a lessons/mistakes log for operational retention.
- **Guidance / Exception Path:** `Optional reference practice.`

#### 6. [Architecture] ADR Process
- **Current Evidence:** No ADR records found
- **Target Standard:** docs/adr/ directory with records
- **Action Required:** Introduce docs/adr/ and record durable cross-cutting decisions.
- **Guidance / Exception Path:** `ADR-0001 adoption.`

#### 7. [Architecture] DESIGN.md Contract
- **Current Evidence:** No DESIGN.md in non-UI project
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Consider adding DESIGN.md declaring CLI/tool archetype.
- **Guidance / Exception Path:** `ADR-0007 optional for headless tools.`

#### 8. [GitHub] PR Template
- **Current Evidence:** Missing PR template
- **Target Standard:** .github/pull_request_template.md
- **Action Required:** Add .github/pull_request_template.md.
- **Guidance / Exception Path:** `Use OpenForge PR template baseline.`

#### 9. [GitHub] Issue Templates
- **Current Evidence:** No issue templates found
- **Target Standard:** Bug & Feature issue templates
- **Action Required:** Create .github/ISSUE_TEMPLATE/ for bug reports and features.
- **Guidance / Exception Path:** `Use OpenForge templates.`

#### 10. [GitHub] Contributing Guide (en+ko)
- **Current Evidence:** Missing CONTRIBUTING.md
- **Target Standard:** CONTRIBUTING.md + CONTRIBUTING-ko.md
- **Action Required:** Add CONTRIBUTING.md and CONTRIBUTING-ko.md.
- **Guidance / Exception Path:** `Use OpenForge template.`

#### 11. [GitHub] Code of Conduct
- **Current Evidence:** Missing CODE_OF_CONDUCT.md
- **Target Standard:** CODE_OF_CONDUCT.md
- **Action Required:** Add CODE_OF_CONDUCT.md.
- **Guidance / Exception Path:** `OpenForge standard policy.`

#### 12. [Security] Dependency Update Automation
- **Current Evidence:** Missing Dependabot/Renovate configuration
- **Target Standard:** Dependabot/Renovate config
- **Action Required:** Add .github/dependabot.yml for automated dependency security updates.
- **Guidance / Exception Path:** `Continuous vulnerability management.`

#### 13. [Security] SECURITY Policy (en+ko)
- **Current Evidence:** Missing SECURITY.md
- **Target Standard:** SECURITY.md + SECURITY-ko.md
- **Action Required:** Add SECURITY.md outlining responsible vulnerability disclosure.
- **Guidance / Exception Path:** `OpenForge security standard.`

#### 14. [Security] Code Scanning / SAST
- **Current Evidence:** CI present without automated SAST
- **Target Standard:** CodeQL or SAST in CI
- **Action Required:** Add CodeQL or language-specific static analysis.
- **Guidance / Exception Path:** `Recommended public OSS practice.`

#### 15. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** Agent contract present without explicit convergence rules
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

### Verification Checklist

- [ ] Update filenames to `-ko.md` format where applicable (ADR-0002)
- [ ] Introduce/Update `AGENTS.md` and `DESIGN.md` contracts
- [ ] Ensure CI runs format, test, and supply-chain verification
- [ ] Document intentional exceptions in an ADR if required (ADR-0012)

> Automated by OpenForge Portfolio Compliance Auditor
