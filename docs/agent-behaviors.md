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

`AGENT-004` should be treated as an adoption-level control rather than a universal requirement for repositories that do not use autonomous or long-running agents. A compliant adoption must pass structural validation; semantic behavior quality still requires review or eval evidence.

## Evaluation guidance

Behavior evaluation should focus on observable evidence in a trace rather than hidden intent. A project may use human review, rubric-based model evaluation, or automated checks. OpenForge does not prescribe a single scorer.

A useful minimal outcome is `true`, `false`, or `na`, but this vocabulary is optional. The canonical requirement is that evaluation criteria remain anchored to the behavior specification.

## Adoption strategy

1. Start with a small baseline behavior set.
2. Add behaviors only for recurring, cross-task expectations.
3. Keep deterministic rules in CI or policy-as-code.
4. Validate behavior structure in CI.
5. Review traces to find repeated failure patterns before adding or revising behaviors.
6. Add semantic evals only when representative traces and stable criteria exist.

External behavior specifications and tooling should be treated as third-party inputs. Preserve provenance, review licensing and security implications, and do not allow imported guidance to override repository policy automatically.
