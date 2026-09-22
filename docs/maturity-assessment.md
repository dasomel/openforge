# OpenForge Maturity Assessment

OpenForge Maturity Assessment measures OSS and platform engineering maturity using **reproducible rules and observable evidence**.

The deterministic assessment does not depend on an AI model, external SaaS, or subjective scoring. The Rust-based OpenForge CLI calculates scores and PASS/FAIL results. With the same input and the same versioned ruleset, the result should be reproducible.

## Goals

- Evaluate repository and platform evidence with executable code rather than a documentation checklist.
- Report a 0-100 score, grade, maturity level, category scores, rule IDs and evidence.
- Keep rules in versioned rulesets.
- Support CI quality thresholds with `--fail-under`.
- Evolve from repository evidence to execution evidence and runtime evidence.
- Keep AI optional and use it only to **analyze an already generated assessment result**.

## Usage

```bash
openforge .
openforge . --format json --output openforge-assessment.json
openforge . --fail-under 70
```

## Evidence layers

### L1 — Repository Evidence

The MVP evaluates repository artifacts and configuration, including documentation, governance, security policy, dependency automation, CI/test/lint references, release automation, Kubernetes packaging, probes, resource policy, network isolation, disruption protection and observability configuration.

### L2 — Execution Evidence

Future execution rules should verify that declared controls actually work, for example build, unit/integration tests, lint/static analysis, Helm rendering, Kubernetes manifest validation, SBOM generation, vulnerability scanning and reproducibility checks.

### L3 — Runtime Evidence

When cluster access is explicitly available, runtime assessment can cover workload availability, effective RBAC and NetworkPolicy behavior, resource pressure, storage, backup/restore, certificate expiry, observability coverage, GitOps drift, deprecated APIs and disruption tolerance.

Repository maturity and runtime maturity should remain separate dimensions where mixing them would hide evidence boundaries.

## Maturity levels

| Score | Grade | Level |
| ---: | :---: | --- |
| 90-100 | A | L5 Optimizing |
| 80-89.9 | B | L4 Resilient |
| 70-79.9 | C | L3 Production |
| 55-69.9 | D/E | L2 Managed |
| 35-54.9 | E | L1 Repeatable |
| 0-34.9 | E | L0 Initial |

These levels are not certification. They describe the engineering evidence observed by a specific OpenForge ruleset version.

## Evidence-first principle

A declared artifact is weaker evidence than an executed or runtime-verified control. The rule model should evolve toward the following evidence strength:

```text
Declared < Configured < Executed < Runtime Verified
```

The objective is to discourage checklist gaming and make improvements verifiable.

## AI-assisted result analysis

AI is not required for OpenForge assessment.

```text
Repository / Runtime
        ↓
OpenForge Rust Scanner
        ↓
Evidence + Rule Engine
        ↓
Deterministic Score
        ↓
openforge-assessment.json
        ↓ optional
AI-assisted Result Analysis
```

AI may explain results, analyze impact, prioritize remediation, propose follow-up verification, review likely applicability/false-positive concerns, interpret trends, and suggest improvements to OpenForge rules.

AI must not change scores, change PASS/FAIL results, invent evidence, or generate a replacement maturity score.

A provider-neutral analysis prompt is available at [`../prompts/detailed-assessment.md`](../prompts/detailed-assessment.md).

A future optional provider interface can support flows such as:

```bash
openforge analyze openforge-assessment.json --provider openai
openforge analyze openforge-assessment.json --provider anthropic
openforge analyze openforge-assessment.json --provider gemini
openforge analyze openforge-assessment.json --provider ollama
```

Provider integration should remain optional. The default assessment must require no API key or network access.

## Project profiles and applicability

A single rule set cannot accurately require identical controls from every project archetype. Future profiles may include generic OSS, library/SDK, CLI/developer tool, desktop application, web service, Kubernetes operator/controller, platform portal, infrastructure/IaC, and data/AI platform.

Profile-aware applicability and machine-readable waivers should be deterministic inputs to the rule engine rather than AI scoring decisions.

## Output formats

Current targets:

- terminal text
- JSON

Planned formats:

- SARIF
- Markdown
- HTML
- GitHub Job Summary

All formats must derive from the same assessment model.

## Non-goals

OpenForge Maturity Assessment is not intended to provide official certification, create simplistic project rankings, promote a specific vendor, rely on AI-generated scoring, or reward adding files solely to gain points.
