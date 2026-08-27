# chore(compliance): align with OpenForge standards (54.8% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — KubeMetal

**Current Score:** `54.8%` (34/62 points)
**Maturity Status:** Foundation work required
**Product Archetype:** Desktop Operator

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Legacy filename: README_ko.md
- **Target Standard:** README-ko.md present
- **Action Required:** Rename README_ko.md -> README-ko.md per ADR-0002.
- **Guidance / Exception Path:** `ADR-0002 / rename to -ko.md`

#### 2. [Documentation] Korean Filename Standard
- **Current Evidence:** Found 2 legacy files (CHANGELOG.ko.md, README_ko.md)
- **Target Standard:** Use <name>-ko.md format
- **Action Required:** Migrate legacy Korean filenames (2 files) to *-ko.md.
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

#### 5. [Architecture] ADR Process
- **Current Evidence:** No ADR records found
- **Target Standard:** docs/adr/ directory with records
- **Action Required:** Introduce docs/adr/ and record durable cross-cutting decisions.
- **Guidance / Exception Path:** `ADR-0001 adoption.`

#### 6. [Architecture] DESIGN.md Contract
- **Current Evidence:** Found DESIGN.md (partial token/archetype declaration)
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Expand DESIGN.md with product archetype and OpenForge semantic token map.
- **Guidance / Exception Path:** `ADR-0007 adoption.`

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

#### 14. [Security] .env.example Template
- **Current Evidence:** Missing .env.example
- **Target Standard:** .env.example present
- **Action Required:** Provide .env.example with sanitized placeholder secrets.
- **Guidance / Exception Path:** `Prevent accidental credential exposure.`

#### 15. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** Agent contract present without explicit convergence rules
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

#### 16. [Design System] Product Archetype Declaration
- **Current Evidence:** DESIGN.md present without explicit archetype
- **Target Standard:** Archetype declared in DESIGN.md
- **Action Required:** Declare primary archetype (Desktop Operator) in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 archetype standard.`

#### 17. [Design System] Semantic Token Mapping
- **Current Evidence:** DESIGN.md present without complete token mapping
- **Target Standard:** OpenForge token aliases in DESIGN.md
- **Action Required:** Map project color/surface tokens to OpenForge semantic roles.
- **Guidance / Exception Path:** `ADR-0007 design tokens.`

#### 18. [Localization] UI i18n (en-US & ko-KR)
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
