---
name: instruction-debt-audit
description: Audit agent instructions for unnecessary persistence, duplication, broad triggers, stale rules, and unsupported model-specific overrides.
---

# Instruction Debt Audit

## Intent

Keep repository instructions small, relevant, model-agnostic by default, and backed by executable enforcement or measured evidence where possible.

## Evidence to inspect

Inspect only instruction surfaces relevant to the audit scope, including as needed:

- `AGENTS.md` and nested instruction files;
- `CLAUDE.md`, `GEMINI.md`, Codex/editor/tool-specific rules;
- skill/behavior descriptions and routing files;
- linked references and scripts;
- formatter/linter/test/policy/CI configuration that may already enforce a prose rule;
- evals, issues, traces, or reproductions cited by model-specific compatibility guidance.

Do not read every repository document merely because an audit exists.

## Decision

For each instruction, classify it:

```text
persistent invariant -> AGENTS.md
specific task/workflow -> behavior or skill
supporting detail -> reference/example/script
deterministically enforceable -> tooling
unsupported/redundant/stale -> remove
```

## Audit checks

Flag instructions that are:

- duplicated across agent-specific files and canonical guidance;
- always loaded but relevant only to a narrow task;
- vague enough to activate a skill for unrelated work;
- overlapping with another skill's responsibility;
- already enforced by formatter, linter, schema, tests, policy, or CI;
- forcing unconditional repository-wide document reads;
- forcing broad test suites when risk-scoped verification is sufficient;
- requiring repeated approval for safe, local, reversible work already within scope;
- prescribing a rigid procedure where a verified completion state would be sufficient;
- specific to a model/runtime without reproducible failure evidence;
- stale because referenced tools, files, commands, or workflows no longer exist.

## Execution

Prefer the smallest coherent cleanup:

1. retain high-value invariants;
2. move narrow instructions behind progressive disclosure;
3. replace prose with executable enforcement when reliable;
4. keep tool/model files thin and point them to canonical policy;
5. preserve necessary high-risk constraints;
6. remove unsupported duplication;
7. verify that representative tasks still have the guidance required to complete safely and correctly.

For model-specific guidance, require an observed failure, evidence, a minimal mitigation, and a review/removal condition.

## Verification

Compare before and after using representative tasks when practical. Useful evidence includes:

- instruction/context size;
- unnecessary reads/tool calls;
- skill activation count and trigger accuracy;
- repeated approval interruptions;
- completion and verified-correctness rate;
- user-journey or regression results;
- loss of previously enforced safety or architecture constraints.

Do not claim that shorter instructions are better unless verified outcomes are preserved or improved.

## Recovery

If removing or moving an instruction causes a regression, restore the minimum necessary constraint at the narrowest appropriate layer and record the failure evidence.

## Failure modes

- optimizing only for token count;
- deleting inconvenient safety or architecture constraints;
- creating per-model prompt forks from release notes or anecdotes;
- moving all detail into one giant skill that is still always loaded;
- replacing clear completion criteria with vague autonomy;
- treating repository prose as the enforcement boundary for destructive or external actions.
