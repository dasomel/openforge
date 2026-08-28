# OpenForge Adoption Guide

> OpenForge succeeds when one repository can adopt one engineering standard, verify it, and understand the gap — not when every template is copied at once.

## 1. Smallest useful adoption

Choose one concrete need such as documentation structure, security policy, ADR governance, Agent Behavior, CI/supply-chain policy, or design-system governance.

1. Read the corresponding standard/template.
2. Apply the smallest coherent change to one repository.
3. Run the relevant validator/audit.
4. Review the evidence and gaps.
5. Adopt the next standard only when it solves a real repository need.

## 2. Portfolio scores

OpenForge portfolio scores are **standards-compliance evidence**, not product maturity, quality, popularity, or external-adoption scores. A lower score can simply mean a standard is not applicable or not yet adopted.

## 3. Agent engineering path

The canonical model is:

```text
Instructions -> Skills -> Behaviors -> Evidence -> Traces -> Evals -> CI/Policy
```

Behavior/eval tooling evaluates observable structured evidence. It does not require or inspect hidden chain-of-thought.

## 4. Documentation path

- `docs/documentation.md` — documentation standard
- `docs/portfolio-documentation-status.md` — current portfolio review
- `docs/decision-management.md` and ADRs — decision governance
- Agent evaluation/governance docs — operational agent evidence
- templates/scripts — deterministic validation/audit tools

## 5. Adoption principle

Prefer **Time to First Verified Success** over document count. Do not mass-copy controls that a repository cannot maintain. Standards should be adopted with repository-specific runtime, security, and evidence boundaries intact.