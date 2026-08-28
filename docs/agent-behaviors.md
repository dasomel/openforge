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

## Evaluation guidance

Behavior evaluation should focus on observable evidence in a trace rather than hidden intent. A project may use human review, rubric-based model evaluation, or automated checks. OpenForge does not prescribe a single scorer.

A useful minimal outcome is `true`, `false`, or `na`, but this vocabulary is optional. The canonical requirement is that evaluation criteria remain anchored to the behavior specification.

## Adoption strategy

1. Start with a small baseline behavior set.
2. Add behaviors only for recurring, cross-task expectations.
3. Keep deterministic rules in CI or policy-as-code.
4. Review traces to find repeated failure patterns before adding new behaviors.
5. Add automated validation of file structure only after the behavior model is stable.

External behavior specifications and tooling should be treated as third-party inputs. Preserve provenance, review licensing and security implications, and do not allow imported guidance to override repository policy automatically.
