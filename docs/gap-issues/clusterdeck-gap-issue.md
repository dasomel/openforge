# chore(compliance): align with OpenForge standards (68.8% maturity)

**Labels:** `compliance, openforge, standard-gap`

## OpenForge Compliance Audit — ClusterDeck

**Current Score:** `68.8%` (44/64 points)
**Maturity Status:** Developing / improvement recommended
**Product Archetype:** Operations Dashboard

### Identified Gaps & Required Actions

#### 1. [Documentation] Lessons & Mistakes Log
- **Current Evidence:** No dedicated lessons log (optional)
- **Target Standard:** lessons-log.md / mistakes-log.md
- **Action Required:** Maintain a lessons/mistakes log for operational retention.
- **Guidance / Exception Path:** `Optional reference practice.`

#### 2. [Architecture] ADR Bilingual Pairs
- **Current Evidence:** 1/1 ADRs missing Korean pair
- **Target Standard:** 100% paired ADRs
- **Action Required:** Add Korean translations for docs/adr/0001-macos-first-tauri-architecture.md.
- **Guidance / Exception Path:** `ADR-0002 bilingual parity.`

#### 3. [Architecture] DESIGN.md Contract
- **Current Evidence:** Missing DESIGN.md in UI project
- **Target Standard:** DESIGN.md with archetype & tokens
- **Action Required:** Create DESIGN.md using OpenForge template with archetype and token mapping.
- **Guidance / Exception Path:** `ADR-0007 required for UI.`

#### 4. [GitHub] Contributing Guide (en+ko)
- **Current Evidence:** Found CONTRIBUTING.md (missing Korean pair)
- **Target Standard:** CONTRIBUTING.md + CONTRIBUTING-ko.md
- **Action Required:** Add CONTRIBUTING-ko.md.
- **Guidance / Exception Path:** `ADR-0002 bilingual guidance.`

#### 5. [CI] Documentation & ADR Validation
- **Current Evidence:** Workflows present without dedicated doc check
- **Target Standard:** Doc/ADR validation step in CI
- **Action Required:** Add documentation / ADR pair verification to CI.
- **Guidance / Exception Path:** `Prevent doc drift.`

#### 6. [CI] Supply Chain & Security Gates
- **Current Evidence:** Standard CI present without supply chain gate
- **Target Standard:** Supply chain / SBOM / Policy gate in CI
- **Action Required:** Add supply-chain and SBOM/dependency verification workflow.
- **Guidance / Exception Path:** `ADR-0006 compliance.`

#### 7. [Security] Dependency Update Automation
- **Current Evidence:** Missing Dependabot/Renovate configuration
- **Target Standard:** Dependabot/Renovate config
- **Action Required:** Add .github/dependabot.yml for automated dependency security updates.
- **Guidance / Exception Path:** `Continuous vulnerability management.`

#### 8. [Security] SECURITY Policy (en+ko)
- **Current Evidence:** Found SECURITY.md (missing Korean pair)
- **Target Standard:** SECURITY.md + SECURITY-ko.md
- **Action Required:** Add SECURITY-ko.md per ADR-0002.
- **Guidance / Exception Path:** `Vulnerability disclosure path.`

#### 9. [Security] Code Scanning / SAST
- **Current Evidence:** CI present without automated SAST
- **Target Standard:** CodeQL or SAST in CI
- **Action Required:** Add CodeQL or language-specific static analysis.
- **Guidance / Exception Path:** `Recommended public OSS practice.`

#### 10. [Security] .env.example Template
- **Current Evidence:** Missing .env.example
- **Target Standard:** .env.example present
- **Action Required:** Provide .env.example with sanitized placeholder secrets.
- **Guidance / Exception Path:** `Prevent accidental credential exposure.`

#### 11. [Agent Engineering] Evidence & Convergence Rules
- **Current Evidence:** Agent contract present without explicit convergence rules
- **Target Standard:** Explicit stop conditions & evidence requirements
- **Action Required:** Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.
- **Guidance / Exception Path:** `ADR-0009 compliance.`

#### 12. [Design System] Product Archetype Declaration
- **Current Evidence:** Missing archetype declaration
- **Target Standard:** Archetype declared in DESIGN.md
- **Action Required:** Declare Operations Dashboard in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 design contract.`

#### 13. [Design System] Semantic Token Mapping
- **Current Evidence:** No token mapping found
- **Target Standard:** OpenForge token aliases in DESIGN.md
- **Action Required:** Map UI tokens to OpenForge semantic tokens in DESIGN.md.
- **Guidance / Exception Path:** `ADR-0007 semantic tokens.`

#### 14. [Localization] UI i18n (en-US & ko-KR)
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
