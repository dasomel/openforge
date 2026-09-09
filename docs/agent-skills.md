# Agent Skills Standard

OpenForge treats agent skills as versioned engineering workflows, not as a collection of generic prompts. A skill should reduce repeated discovery, encode project/domain procedures that models cannot safely infer, and remain small enough to load only when needed.

This standard follows the Agent Skills `SKILL.md` format and complements `docs/agent-engineering.md`.

## Instruction layers

```text
AGENTS.md
  -> short, agent-neutral repository execution contract

CLAUDE.md / tool-specific rules
  -> adapter-only behavior for that runtime
  -> import/reference AGENTS.md instead of copying generic rules

SKILL.md
  -> repeatable task/domain workflow loaded on demand

scripts / Makefile / tests / policy / CI
  -> deterministic execution and enforcement
```

Do not move deterministic checks into prose. Do not copy the same engineering rule into AGENTS.md, CLAUDE.md, and multiple skills.

## Skill scopes

OpenForge uses three scopes.

| Scope | Owner | Use |
|---|---|---|
| `core` | OpenForge | Portfolio-wide workflow that is repository-independent |
| `domain` | OpenForge or a domain owner | Reusable workflow for a technical family such as Kubernetes platform, Go CLI, Next.js portal, Packer/Vagrant, or identity |
| `project` | The project repository | Project-specific source of truth, operational workflow, boundaries, and verification |

A project workflow should remain in the project repository unless at least two repositories use essentially the same procedure without project-specific assumptions. Promote common behavior upward instead of copying it.

## Canonical source and adapters

Each skill has exactly one canonical editable copy.

- Project skills live with the project that owns the workflow.
- Core/domain templates and portfolio guidance live in OpenForge.
- `.claude/skills/`, `.agents/skills/`, plugins, or other runtime-specific locations may act as adapters/discovery locations.
- If a runtime requires a copy or link, generate or link it from the canonical source. Do not hand-edit both copies.
- Record the canonical owner and scope in `metadata`.
- Do not depend on personal absolute paths such as `/Users/name/...` or `/home/name/...`.

A repository may keep an existing runtime-specific canonical location during migration. The important rule is one source of truth and no divergent mirrors.

## `SKILL.md` format

Every skill directory contains a `SKILL.md` with YAML frontmatter. Keep it compatible with the Agent Skills specification.

```yaml
---
name: project-task
# Describe both what the skill does and when it should be activated.
description: Perform the project-specific task safely. Use when ...
license: Apache-2.0
compatibility: Requires the repository checkout and documented project toolchain.
metadata:
  openforge-scope: project
  openforge-owner: owner/repository
  openforge-maturity: verified
  openforge-version: "1"
---
```

`name` and `description` are required by the Agent Skills format. Keep custom OpenForge metadata values as strings for portability.

### Naming

- Use lowercase kebab-case.
- Project skills should normally use `<project>-<task>` so globally installed skills do not collide.
- Avoid generic names such as `verification`, `build`, `deploy`, or `debug` for project-scoped skills.
- Domain/core skills may use a domain prefix such as `kubernetes-platform-verification`.

### Description

The description is routing metadata, not marketing copy. It must say both what the skill does and when to use it. Prefer concrete paths, task classes, or system boundaries over broad trigger lists such as `fix`, `version`, or `install`.

## Recommended body

Keep the main body concise and move detailed references to `references/`.

```text
# Skill title
## Use When
## Do Not Use When
## Inputs
## Workflow
## Verification
## Stop / Escalate When
## References
```

Use `scripts/` when steps are deterministic. Use `references/` for long-lived project knowledge and `assets/` for templates or data. Keep reference chains shallow.

OpenForge target: normally less than 250 lines; Agent Skills compatibility ceiling: less than 500 lines.

## What belongs in a skill

Good candidates are tasks that can be phrased as "how we do X here": adding a Narwhal platform component, validating NFS project quota behavior, changing a Beluga integration contract, or building a Kube Ready Box matrix.

Keep the following elsewhere:

- Generic model advice -> remove or keep in user/runtime configuration.
- Repository-wide non-negotiable boundaries -> `AGENTS.md`.
- Claude-only team lanes, slash commands, hooks, or model routing -> `CLAUDE.md` / `.claude/rules/`.
- Architecture and stable system facts -> architecture/design docs.
- Historical incidents -> lessons/mistakes logs; skills should reference the relevant discriminator.
- Formatter/linter/testable rules -> executable tooling.

## Claude adapter standard

`CLAUDE.md` is an adapter, not a second repository constitution.

A healthy file normally:

1. imports or references `AGENTS.md`;
2. adds only Claude-specific harness/routing/command behavior;
3. points to project skills instead of re-embedding their workflows;
4. contains no personal machine paths or required dependence on a maintainer's global `~/.claude/CLAUDE.md`;
5. leaves generic engineering rules in `AGENTS.md` or linked standards.

Large legacy CLAUDE.md files should be split without deleting valuable project knowledge. Move stable facts to docs, repeatable workflows to skills, incidents to the lessons log, and deterministic rules to scripts/CI.

## Lifecycle

Use `metadata.openforge-maturity` with one of:

- `draft`: workflow exists but has not been replayed from a clean context;
- `verified`: successfully replayed with explicit evidence;
- `stable`: repeated successful use with no known trigger ambiguity;
- `deprecated`: retained only for migration; description must point at the replacement.

For material changes, increment `metadata.openforge-version`.

## Verification

A skill is not verified because its Markdown looks reasonable.

Before promoting to `verified`:

1. validate the `SKILL.md` format (`skills-ref validate` when available);
2. run the workflow in a fresh session without relying on the conversation that created it;
3. exercise at least one known failure/edge case;
4. confirm the expected files/commands/results, including what must not change;
5. verify on every supported agent runtime when portability is claimed;
6. record failures as regression scenarios or deterministic checks where practical.

A successful unit/stub path must not be presented as proof of a real cluster, filesystem, network, identity, or cloud behavior.

## Security

A skill is guidance, not an authorization boundary. `allowed-tools` is experimental and must not be treated as a security control. Side-effecting tools still require the capability, approval, sandbox, and evidence controls defined in `docs/agent-execution-security.md`.

## Review and cleanup

Review the skill inventory when a major agent/runtime changes or at least quarterly for active projects.

Remove or merge a skill when:

- it is no longer invoked;
- the model/tool now handles the generic task without project knowledge;
- its workflow is fully enforced by scripts/CI;
- another skill has the same trigger/body;
- its instructions conflict with the current repository.

Do not grow the catalog merely to increase coverage. Fewer precise skills are preferred to many overlapping ones.
