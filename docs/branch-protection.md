# Branch Protection and Required Status Checks Standard

English | [한국어](branch-protection-ko.md)

> Standardizing branch protection, required status checks, and merge safety across the OpenForge OSS portfolio.

## 1. Purpose

Continuous Integration (CI) provides automated assurance, but CI workflows only guarantee software quality if merges to canonical branches (`main`) are gated on passing status checks. Without branch protection, unverified changes or failing checks can bypass quality and supply-chain controls.

This standard establishes the baseline required status checks for canonical branches across all OpenForge-aligned OSS repositories, balancing assurance with maintainer velocity according to [ADR-0003](adr/0003-risk-based-oss-security-governance.md).

## 2. Standard Required Status Checks Matrix

For canonical repositories, the default merge gate on `main` requires the following checks:

```text
main
 ├─ Markdown Check (Naming conventions, language pairs, formatting)
 ├─ Repository Baseline Check (Required files, license, editorconfig)
 ├─ ADR Validation (Bilingual pairs, index registration, status/date)
 ├─ Supply-Chain Baseline (Policy-as-code, immutable action pins)
 └─ Project Test & Build (Deterministic unit/integration test, compilation)
       ↓
 Required before merge
```

### Check Definitions

| Status Check Context | Workflow / Tool | Scope | Criticality |
|---|---|---|---|
| `markdown` | `.github/workflows/markdown.yml` | Validates `-ko.md` naming convention and root bilingual pairings | High |
| `repository-check` | `.github/workflows/ci.yml` | Validates mandatory OSS files (`README.md`, `LICENSE`, `SECURITY.md`, etc.) | Critical |
| `Validate ADR decision history` | `templates/scripts/validate-adrs.sh` | Enforces ADR pair consistency, status, date, and index synchronization | Critical for ADR repos |
| `Verify supply-chain baseline` | `templates/scripts/verify-supply-chain.sh` | Enforces dependency intake policy, immutable action SHA pins | Critical |
| `test` / `build` | Project CI workflows | Unit tests, static analysis, artifact build validation | Critical |

## 3. Governance Models by Project Tier

In alignment with [ADR-0003 (Risk-Based OSS Security Governance)](adr/0003-risk-based-oss-security-governance.md):

### Tier 1: Canonical Standards & Production Libraries (`openforge`, `narwhal`, `ldapium`)
- **Branch Protection:** Enabled on `main`.
- **Require Status Checks to Pass:** Yes (Strict / Up-to-date with branch required).
- **Require Pull Request Reviews:** Optional for solo maintainers, recommended for multi-contributor projects.
- **Enforce Admins:** Recommended to prevent accidental direct pushes.
- **Linear History / Squash Merges:** Enforced to keep release changelog traceable.

### Tier 2: Active Desktop & Platform Operators (`clusterdeck`, `kubemetal`, `beluga-manager`)
- **Branch Protection:** Enabled on `main`.
- **Require Status Checks to Pass:** Yes (`ci.yml`, `markdown.yml`, `test`).
- **Direct Pushes:** Restricted; changes land via PR or verified staging branch.

### Tier 3: Experimental Labs & Prototypes (`cka-lab`)
- **Branch Protection:** Advisory / CI-backed.
- **Merge Gate:** Manual maintainer review with local verification before fast-forward merge.

## 4. Verification and Enforcement via `gh` CLI

OpenForge provides a verification script (`templates/scripts/check-branch-protection.sh`) to audit branch protection status via the GitHub CLI:

```bash
# Check branch protection status
bash templates/scripts/check-branch-protection.sh dasomel/openforge

# Apply OpenForge baseline protection rule (requires admin repository permissions)
gh api -X PUT "repos/dasomel/openforge/branches/main/protection" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "markdown",
      "repository-check"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```

## 5. Traceability

- **ADR-0003:** Risk-Based OSS Security Governance
- **ADR-0006:** Release Supply Chain Security Controls
- **ADR-0011:** CI Resilience Must Preserve Assurance
- **ADR-0012:** Document and Time-Bound Intentional Exceptions
- **Reference Metrics:** [docs/reference-metrics.md](reference-metrics.md)
