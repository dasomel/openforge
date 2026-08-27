# chore(compliance): align with OpenForge standards (66.1% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — NFS Quota Agent

**Current Score:** `66.1%` (41/62 points)
**Maturity Status:** Developing / improvement recommended
**Product Archetype:** Developer Tool

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Legacy filename: README_ko.md
- **Target Standard:** README-ko.md present
- **Action Required:** Rename README_ko.md -> README-ko.md per ADR-0002.
- **Guidance / Exception Path:** `ADR-0002 / rename to -ko.md`

#### 2. [Documentation] Korean Filename Standard
- **Current Evidence:** Found 3 legacy files (README_ko.md, docs/feature-guide_ko.md)
- **Target Standard:** Use <name>-ko.md format
- **Action Required:** Migrate legacy Korean filenames (3 files) to *-ko.md.
- **Guidance / Exception Path:** `ADR-0002 naming standard`

#### 3. [Documentation] Lessons & Mistakes Log
- **Current Evidence:** No dedicated lessons log (optional)
- **Target Standard:** lessons-log.md / mistakes-log.md
- **Action Required:** Maintain a lessons/mistakes log for operational retention.
- **Guidance / Exception Path:** `Optional reference practice.`

#### 4. [Architecture] ADR Process
- **Current Evidence:** No ADR records found
- **Target Standard:** docs/adr/ directory with records
- **Action Required:** Introduce docs/adr/ and record durable cross-cutting decisions.
- **Guidance / Exception Path:** `ADR-0001 adoption.`

#### 5. [Architecture] DESIGN.md Contract
- **Current Evidence:** Found DESIGN.md (partial token/archetype declaration)
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Expand DESIGN.md with product archetype and OpenForge semantic token map.
- **Guidance / Exception Path:** `ADR-0007 adoption.`

#### 6. [GitHub] PR Template
- **Current Evidence:** Missing PR template
- **Target Standard:** .github/pull_request_template.md
- **Action Required:** Add .github/pull_request_template.md.
- **Guidance / Exception Path:** `Use OpenForge PR template baseline.`

#### 7. [GitHub] Issue Templates
- **Current Evidence:** No issue templates found
- **Target Standard:** Bug & Feature issue templates
- **Action Required:** Create .github/ISSUE_TEMPLATE/ for bug reports and features.
- **Guidance / Exception Path:** `Use OpenForge templates.`

#### 8. [GitHub] Contributing Guide (en+ko)
- **Current Evidence:** Found CONTRIBUTING.md (missing Korean pair)
- **Target Standard:** CONTRIBUTING.md + CONTRIBUTING-ko.md
- **Action Required:** Add CONTRIBUTING-ko.md.
- **Guidance / Exception Path:** `ADR-0002 bilingual guidance.`

#### 9. [GitHub] Code of Conduct
- **Current Evidence:** Missing CODE_OF_CONDUCT.md
- **Target Standard:** CODE_OF_CONDUCT.md
- **Action Required:** Add CODE_OF_CONDUCT.md.
- **Guidance / Exception Path:** `OpenForge standard policy.`

#### 10. [Security] SECURITY Policy (en+ko)
- **Current Evidence:** Missing SECURITY.md
- **Target Standard:** SECURITY.md + SECURITY-ko.md
- **Action Required:** Add SECURITY.md outlining responsible vulnerability disclosure.
- **Guidance / Exception Path:** `OpenForge security standard.`

#### 11. [Security] .env.example Template
- **Current Evidence:** Missing .env.example
- **Target Standard:** .env.example present
- **Action Required:** Provide .env.example with sanitized placeholder secrets.
- **Guidance / Exception Path:** `Prevent accidental credential exposure.`

#### 12. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** Agent contract present without explicit convergence rules
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

#### 13. [Design System] Product Archetype Declaration
- **Current Evidence:** DESIGN.md present without explicit archetype
- **Target Standard:** Archetype declared in DESIGN.md
- **Action Required:** Declare primary archetype (Developer Tool) in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 archetype standard.`

#### 14. [Design System] Semantic Token Mapping
- **Current Evidence:** DESIGN.md present without complete token mapping
- **Target Standard:** OpenForge token aliases in DESIGN.md
- **Action Required:** Map project color/surface tokens to OpenForge semantic roles.
- **Guidance / Exception Path:** `ADR-0007 design tokens.`

### Verification Checklist

- [ ] Update filenames to `-ko.md` format where applicable (ADR-0002)
- [ ] Introduce/Update `AGENTS.md` and `DESIGN.md` contracts
- [ ] Ensure CI runs format, test, and supply-chain verification
- [ ] Document intentional exceptions in an ADR if required (ADR-0012)

> Automated by OpenForge Portfolio Compliance Auditor
