# Model-Agnostic Agent Instruction Design

OpenForge optimizes agent instructions for durable behavior, not for a specific model generation.

The canonical rule is:

> Standardize invariants, boundaries, and completion evidence. Do not fork repository prompts by model name unless a repeated, measured compatibility failure justifies a narrow override.

## Instruction architecture

```text
AGENTS.md
  -> minimal persistent execution contract

behaviors / skills
  -> task-specific conduct and workflow selection

references / scripts
  -> progressive disclosure and executable support

CLAUDE.md / GEMINI.md / tool-specific files
  -> thin adapters only

formatter / linter / tests / policy-as-code / CI
  -> deterministic enforcement
```

## 1. Minimum persistent instructions

Keep `AGENTS.md` limited to instructions that are relevant to nearly every substantive task in the repository.

Prefer:

```text
Inspect repository guidance and documentation relevant to the current task before editing.
```

Avoid unconditional requirements such as reading every README, design document, contribution guide, or architecture document before trivial or unrelated changes.

Persistent instructions should primarily define:

- scope and architecture boundaries;
- high-risk actions and authorization requirements;
- canonical verification expectations;
- bug-fix evidence policy;
- completion and escalation conditions;
- project-specific constraints that cannot be inferred safely from code or tooling.

If a deterministic rule can be enforced by formatter, linter, test, policy, schema, or CI, prefer executable enforcement over repeating the rule in prose.

## 2. Progressive disclosure

Task-specific detail should be loaded only when needed.

A skill that covers multiple workflows should route to focused references or scripts instead of embedding all procedures in its root file.

```text
task
  -> narrow skill trigger
  -> choose relevant workflow
       -> reference
       -> script
       -> executable check
```

Good skill roots explain:

- when the skill applies;
- which workflow to select;
- which reference or script to load next;
- what outcome or evidence is required.

They should not preload unrelated examples, troubleshooting, or every possible workflow.

## 3. Narrow activation

Skill and behavior descriptions should be short and specific enough that an agent can distinguish when they apply.

Avoid descriptions such as "use for all database work" when the skill is only for schema migration.

Prefer non-overlapping triggers and one clear responsibility per skill. If multiple skills appear to own the same work, narrow or merge them.

## 4. Explicit autonomy boundary

Safe, local, reversible, and disposable work should not require repeated approval when it is already within the requested scope.

Examples that may normally proceed autonomously:

- inspect relevant repository files;
- edit files within the requested scope;
- run local build, lint, unit, integration, or disposable-environment tests;
- fix failures caused by the requested change;
- re-run relevant verification;
- create temporary local artifacts that do not affect external systems.

Require explicit authorization unless it has already been granted for actions such as:

- production or shared-environment mutation;
- destructive external actions or irreversible data changes;
- credential, permission, RBAC, or trust-boundary changes beyond the requested design;
- publishing releases, packages, images, or public announcements;
- charging money or changing paid resources;
- modifying unrelated repositories or external systems.

Repository prose is not itself a security boundary. Side-effecting tools must still enforce authorization and policy at execution time.

## 5. Completion over procedure

Prefer verified end states over rigid step-by-step instructions.

For example:

```text
Implement the requested change, perform verification appropriate to its risk and user impact, fix failures caused by the change, and continue until the work is verified or a concrete blocker is isolated.
```

This is usually more durable than prescribing a fixed sequence of reads and tests for every task.

The agent may choose the shortest reliable path, but it must report the evidence actually obtained and must not imply a stronger guarantee than that evidence supports.

For user-facing, installation, configuration, upgrade, integration, or high-risk changes, apply the [User-Centric Validation Standard](user-centric-validation.md). Select only the gates relevant to the task's risk and user impact; the standard does not require every gate for every change.

## 6. Tool- and model-specific files are adapters

`CLAUDE.md`, `GEMINI.md`, Codex-specific rules, editor instructions, or local agent configuration may coexist with the canonical contract.

Use these files only for:

- syntax or file-layout requirements of the tool;
- capabilities or limitations unique to the tool;
- high-value integration guidance that cannot be expressed portably.

Do not duplicate generic engineering policy in each adapter. Prefer a thin pointer back to `AGENTS.md` or the canonical OpenForge standard.

Example:

```markdown
# CLAUDE.md

Follow the repository-wide contract in `AGENTS.md`.
Load project skills and references only when relevant to the current task.
```

## 7. Model-specific compatibility overrides

Do not maintain files such as `prompt-gpt-x.md`, `prompt-claude-y.md`, or similar forks by default.

A model-specific mitigation is justified only when all of the following are true:

1. the failure is observed repeatedly on a relevant task class;
2. the expected behavior is already clear in the canonical contract;
3. the failure is reproducible or represented in an eval;
4. a narrow mitigation measurably improves the result;
5. the mitigation does not weaken safety or contradict canonical policy;
6. the override has an owner or removal/review condition.

Record at minimum:

```yaml
model_or_runtime: <identifier>
observed_failure: <specific behavior>
evidence: <eval, issue, trace, or reproduction>
mitigation: <minimal instruction or adapter change>
review_condition: <when to retest or remove>
```

Model release notes alone are not sufficient evidence for a repository-wide prompt fork.

## 8. Instruction-debt audit

Use this decision tree for each instruction:

```text
Is it required for nearly every task?
  yes -> keep in AGENTS.md
  no  -> Is it task-specific behavior?
           yes -> move to a behavior/skill
           no  -> Is it supporting detail?
                    yes -> move to reference/example/script
                    no  -> Is tooling able to enforce it?
                             yes -> enforce in tooling and remove prose duplication
                             no  -> remove or justify explicitly
```

Also inspect for:

- duplicate rules across `AGENTS.md`, `CLAUDE.md`, skills, and references;
- broad or overlapping skill triggers;
- unconditional document-reading or test-running requirements;
- instructions already enforced deterministically;
- approval gates that interrupt safe local work;
- procedural instructions that can be replaced by completion criteria;
- model-specific guidance without measured evidence;
- stale instructions referring to removed tools, files, or workflows.

## 9. Measuring whether simplification helped

Do not judge instruction cleanup only by token count.

Compare representative tasks before and after changes using measures such as:

- task completion rate;
- verified correctness / user-journey pass rate;
- unnecessary tool calls or document reads;
- repeated approval requests during safe local work;
- context consumed by persistent instructions;
- number of skills activated per task;
- duplicate or conflicting instruction findings;
- time or steps to first useful implementation;
- regressions caused by omitted high-value constraints.

A shorter prompt is an improvement only when it preserves or improves verified outcomes.

## 10. Downstream adoption

Downstream repositories should reference this standard rather than copy it wholesale:

```markdown
For agent instruction design and maintenance, follow the OpenForge Model-Agnostic Agent Instruction Design standard:
https://github.com/dasomel/openforge/blob/main/docs/model-agnostic-agent-instructions.md
```

Project-specific rules should remain local. Canonical model-independent policy should stay in OpenForge so it can evolve without drifting across repositories.
