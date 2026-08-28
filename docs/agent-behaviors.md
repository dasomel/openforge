# Agent Behaviors

OpenForge separates agent execution instructions from the recurring behaviors used to evaluate whether an agent worked well over time.

## Why behaviors are a separate layer

A long-running agent may make hundreds of local decisions. A final artifact alone cannot show whether it consistently verified evidence, respected scope, recovered safely, or handled uncertainty well.

OpenForge therefore models agent engineering as:

```text
Instructions  -> what the agent must follow during execution
Skills        -> how specialized work is performed
Behaviors     -> what good recurring conduct looks like
Evidence      -> what supports claims and decisions
Traces        -> what actually happened
Evals         -> whether observed conduct matches the behavior specification
CI / Policy   -> what can be deterministically enforced
```

These layers should remain distinct. A behavior is not automatically injected into every agent prompt, and a behavior file should not duplicate a formatter, linter, test, or policy rule that can be enforced deterministically.

## Compatibility profile

OpenForge adopts the portable Agent Behavior directory convention:

```text
.agents/behaviors/<name>/BEHAVIOR.md
```

A behavior file contains YAML frontmatter with `name` and `description`. The body remains Markdown. OpenForge recommends organizing high-value behaviors around intent, evidence, decisions, execution, recovery, and failure modes, while avoiding unnecessary schema constraints.

## What belongs in each layer

| Layer | Purpose | Typical contents |
| --- | --- | --- |
| `AGENTS.md` | runtime execution contract | scope, boundaries, required verification, stop conditions |
| skills | task method | release, migration, review, incident, or domain-specific workflows |
| behaviors | recurring quality expectations | evidence discipline, safe recovery, source trust, cost/safety judgment |
| tests / CI / policy | deterministic enforcement | syntax, formatting, security rules, API and policy checks |
| traces | observed execution | tool calls, decisions, outcomes, failures |
| evals | assessment | human review, rubrics, automated behavior scoring |

## OpenForge baseline behavior profile

The initial baseline captures recurring principles already present in the Agent Engineering Standard:

1. `evidence-before-claim`
2. `scope-discipline`
3. `bug-fix-verification`
4. `task-convergence`
5. `trust-and-provenance`

Projects may add domain-specific behaviors, but should keep canonical behavior names portable and avoid copying equivalent rules into every vendor-specific agent file.

## Validation boundary

Run the repository-local validator with:

```bash
bash templates/scripts/validate-behaviors.sh
```

The validator checks only deterministic structure:

- behavior files exist under `.agents/behaviors/<name>/BEHAVIOR.md`
- YAML frontmatter opens and closes correctly
- `name` is present and matches the parent directory
- `description` is present

It intentionally does **not** score semantic quality, judge whether a behavior is useful, or claim that an agent actually followed the behavior. Those judgments belong to trace review and evals.

## OpenForge compliance mapping

Behavior support extends the Agent Engineering compliance profile without replacing the existing root-contract checks.

- `AGENT-001` — concise agent root contract exists.
- `AGENT-002` — runtime instructions and detailed engineering guidance remain layered.
- `AGENT-003` — evidence, reproduction, and convergence rules are explicit.
- `AGENT-004` — recurring cross-task conduct is represented as valid Agent Behavior specifications when a repository adopts the behavior profile.

`AGENT-004` is part of metric set `2026.09` and remains an adoption-level control rather than a universal requirement.

Portfolio configuration can control adoption explicitly:

```yaml
agent_behaviors: true   # required; missing behavior directory is a gap
agent_behaviors: false  # explicitly N/A
# omitted               # auto-detect from .agents/behaviors/
```

When the field is omitted, repositories without `.agents/behaviors/` receive `N/A`; once the directory exists, the auditor evaluates its structural validity. This prevents the new metric from penalizing projects that do not use long-running or autonomous agents while still making intentional adoption enforceable.

## Canonical portfolio audit

`AGENT-004` is now registered by the canonical audit entrypoint:

```bash
python3 templates/scripts/audit-portfolio.py --config portfolio.yml --summary-only
```

The previous `audit-agent-behaviors.py` command remains only as a compatibility shim. New automation should call `audit-portfolio.py` directly.

The audit implementation is split into:

```text
audit-portfolio.py       -> canonical entrypoint and extension registration
audit-core.py            -> stable portfolio audit implementation
agent_behavior_metric.py -> AGENT-004 registration and 2026.09 compatibility policy
```

This keeps the mature audit core stable while allowing additive metric revisions to remain isolated and testable.

## Metric-set compatibility

Metric set `2026.09` adds `AGENT-004` to the previous `2026.08` set.

Comparison with a `2026.08` baseline is reported as `additive-compatible` rather than fully incompatible. Existing scores remain directly comparable when `AGENT-004` is `N/A`; repositories that adopt the behavior profile may gain a new applicable metric, so their score denominator can change.

Audit JSON includes a `metricSetChange` field describing this addition so downstream reporting can distinguish engineering regressions from metric-set evolution.

## Evaluation guidance

Behavior evaluation should focus on observable evidence in a trace rather than hidden intent. A project may use human review, rubric-based model evaluation, or automated checks. OpenForge does not prescribe a single scorer.

A useful minimal outcome is `true`, `false`, or `na`, but this vocabulary is optional. The canonical requirement is that evaluation criteria remain anchored to the behavior specification.

## Adoption strategy

1. Start with a small baseline behavior set.
2. Add behaviors only for recurring, cross-task expectations.
3. Keep deterministic rules in CI or policy-as-code.
4. Validate behavior structure in CI.
5. Mark required adoption with `agent_behaviors: true` when the project depends on the behavior profile.
6. Review traces to find repeated failure patterns before adding or revising behaviors.
7. Add semantic evals only when representative traces and stable criteria exist.

External behavior specifications and tooling should be treated as third-party inputs. Preserve provenance, review licensing and security implications, and do not allow imported guidance to override repository policy automatically.
