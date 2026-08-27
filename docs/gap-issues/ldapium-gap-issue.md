# chore(compliance): align with OpenForge standards (76.6% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — ldapium

**Current Score:** `76.6%` (49/64 points)
**Maturity Status:** Healthy / minor gaps
**Product Archetype:** Admin Console

### Identified Gaps & Required Actions

#### 1. [Documentation] Korean README
- **Current Evidence:** Legacy filename: README_ko.md
- **Target Standard:** README-ko.md present
- **Action Required:** Rename README_ko.md -> README-ko.md per ADR-0002.
- **Guidance / Exception Path:** `ADR-0002 / rename to -ko.md`

#### 2. [Documentation] Korean Filename Standard
- **Current Evidence:** Found 8 legacy files (CONTRIBUTING_ko.md, RELEASING_ko.md)
- **Target Standard:** Use <name>-ko.md format
- **Action Required:** Migrate legacy Korean filenames (8 files) to *-ko.md.
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
- **Current Evidence:** Missing DESIGN.md in UI project
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Create DESIGN.md using OpenForge template with archetype and token mapping.
- **Guidance / Exception Path:** `ADR-0007 required for UI.`

#### 7. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** Agent contract present without explicit convergence rules
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

#### 8. [Design System] Product Archetype Declaration
- **Current Evidence:** Missing archetype declaration
- **Target Standard:** Archetype declared in DESIGN.md
- **Action Required:** Declare Admin Console in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 design contract.`

#### 9. [Design System] Semantic Token Mapping
- **Current Evidence:** No token mapping found
- **Target Standard:** OpenForge token aliases in DESIGN.md
- **Action Required:** Map UI tokens to OpenForge semantic tokens in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 semantic tokens.`

#### 10. [Localization] UI i18n (en-US & ko-KR)
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
