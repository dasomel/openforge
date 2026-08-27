# chore(compliance): align with OpenForge standards (63.8% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — Narwhal

**Current Score:** `63.8%` (37/58 points)
**Maturity Status:** Developing / improvement recommended
**Product Archetype:** Platform Portal

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Legacy filename: README_ko.md
- **Target Standard:** README-ko.md present
- **Action Required:** Rename README_ko.md -> README-ko.md per ADR-0002.
- **Guidance / Exception Path:** `ADR-0002 / rename to -ko.md`

#### 2. [Documentation] Korean Filename Standard
- **Current Evidence:** Found 4 legacy files (README_ko.md, CHANGELOG_ko.md)
- **Target Standard:** Use <name>-ko.md format
- **Action Required:** Migrate legacy Korean filenames (4 files) to *-ko.md.
- **Guidance / Exception Path:** `ADR-0002 naming standard`

#### 3. [Documentation] Architecture Document
- **Current Evidence:** docs/ directory exists without dedicated architecture doc
- **Target Standard:** docs/architecture*.md
- **Action Required:** Add architecture documentation in docs/architecture.md.
- **Guidance / Exception Path:** `Document core architecture boundaries.`

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
- **Current Evidence:** No DESIGN.md in non-UI project
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Consider adding DESIGN.md declaring CLI/tool archetype.
- **Guidance / Exception Path:** `ADR-0007 optional for headless tools.`

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
- **Current Evidence:** Found CONTRIBUTING.md (missing Korean pair)
- **Target Standard:** CONTRIBUTING.md + CONTRIBUTING-ko.md
- **Action Required:** Add CONTRIBUTING-ko.md.
- **Guidance / Exception Path:** `ADR-0002 bilingual guidance.`

#### 10. [GitHub] Code of Conduct
- **Current Evidence:** Missing CODE_OF_CONDUCT.md
- **Target Standard:** CODE_OF_CONDUCT.md
- **Action Required:** Add CODE_OF_CONDUCT.md.
- **Guidance / Exception Path:** `OpenForge standard policy.`

#### 11. [Security] SECURITY Policy (en+ko)
- **Current Evidence:** Found SECURITY.md (missing Korean pair)
- **Target Standard:** SECURITY.md + SECURITY-ko.md
- **Action Required:** Add SECURITY-ko.md per ADR-0002.
- **Guidance / Exception Path:** `Vulnerability disclosure path.`

#### 12. [Security] Container Security Scan
- **Current Evidence:** Dockerfile present without explicit container scanner in CI
- **Target Standard:** Trivy / Hadolint in CI
- **Action Required:** Add Trivy container scanning step to CI.
- **Guidance / Exception Path:** `Container security standard.`

#### 13. [Security] Code Scanning / SAST
- **Current Evidence:** CI present without automated SAST
- **Target Standard:** CodeQL or SAST in CI
- **Action Required:** Add CodeQL or language-specific static analysis.
- **Guidance / Exception Path:** `Recommended public OSS practice.`

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

### Verification Checklist

- [ ] Update filenames to `-ko.md` format where applicable (ADR-0002)
- [ ] Introduce/Update `AGENTS.md` and `DESIGN.md` contracts
- [ ] Ensure CI runs format, test, and supply-chain verification
- [ ] Document intentional exceptions in an ADR if required (ADR-0012)

> Automated by OpenForge Portfolio Compliance Auditor
