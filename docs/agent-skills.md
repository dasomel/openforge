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
  openforge-maturity: draft
  openforge-version: "1"
---
```

`name` and `description` are required by the Agent Skills format. Keep custom OpenForge metadata values as strings for portability. New or materially changed skills start at `draft`; do not use `verified` in a template or new skill merely because the workflow was reviewed.

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

- `draft`: workflow exists but has not been replayed from a clean context with the required evidence artifact;
- `verified`: successfully replayed with explicit machine-readable evidence;
- `stable`: repeated successful use after verification with no known trigger ambiguity;
- `deprecated`: retained only for migration; description must point at the replacement.

For material changes, increment `metadata.openforge-version`. A material skill-version change invalidates old verification evidence until the evidence `skillVersion` matches the new version.

## Verification

A skill is not verified because its Markdown looks reasonable or because unrelated repository CI is green.

Before promoting to `verified`:

1. validate the `SKILL.md` format (`skills-ref validate` when available);
2. run the workflow in a fresh session without relying on the conversation that created it;
3. exercise at least one known failure/edge case;
4. confirm the expected files/commands/results, including what must not change;
5. run repository-owned deterministic verification and record its result;
6. distinguish static/unit/stub evidence from real cluster/filesystem/network/browser/device/service evidence;
7. verify on every supported agent runtime when portability is claimed;
8. store the machine-readable verification artifact described below.

A successful unit/stub path must not be presented as proof of a real cluster, filesystem, network, identity, or cloud behavior.

### Verification evidence artifact

A `verified` or `stable` skill MUST have:

```text
.agents/skill-evals/<skill-name>.json
```

Use `templates/agent-skill-verification.json` as the starting point. The artifact is evidence metadata, not a transcript dump. It points at project-local traces, CI runs, reports, tests, or runtime artifacts instead of copying large logs.

Required contract:

```json
{
  "schemaVersion": "openforge-agent-skill-verification/v1",
  "skill": "project-task",
  "skillVersion": "1",
  "freshSession": true,
  "agentRuntime": "runtime-and-version-or-channel",
  "happyPath": {
    "status": "passed",
    "scenario": "Representative workflow",
    "evidence": ["artifact:path/or-reference"]
  },
  "edgeCase": {
    "status": "passed",
    "scenario": "Known failure/edge regression",
    "evidence": ["artifact:path/or-reference"]
  },
  "deterministicChecks": [
    {"command": "make verify", "status": "passed", "scope": "repository baseline"}
  ],
  "runtimeEvidence": [],
  "unverified": [],
  "verifiedAt": "YYYY-MM-DD"
}
```

`unverified` is not a failure by itself. It is the explicit boundary of the claim. A skill may be `verified` for its documented scope while naming a runtime path that was not exercised, provided the skill does not claim that unverified property.

`templates/scripts/audit-agent-skills.py` treats missing or malformed evidence as an error when `openforge-maturity` is `verified` or `stable`. Therefore maturity cannot be promoted by frontmatter-only edits.

Do not grandfather a skill solely because it existed before this rule. Existing skills must produce the same evidence artifact before retaining `verified`/`stable` under this standard.

## Repository-local agent contract gate

Agent engineering contracts (`AGENTS.md`, `CLAUDE.md`, `.agents/skills/**`, `.claude/skills/**`, verification evidence, and the commands they reference) are first-class CI inputs, not documentation that only the portfolio-wide audit eventually notices. `templates/scripts/audit-agent-skills.py` is the reusable, dependency-free check; a repository adopts it locally rather than waiting for a central refresh.

### Adopt it

Copy [`templates/github/agent-contract-gate.yml`](../templates/github/agent-contract-gate.yml) into `.github/workflows/agent-contract-gate.yml`. It calls the reusable `dasomel/openforge/.github/workflows/agent-contract-gate.yml` workflow, which:

1. checks out the caller repository and a pinned OpenForge ref (`openforge-ref`, default `main`);
2. diffs changed paths against the base revision and runs the audit only when a contract path changed (`paths-filter` input);
3. runs `audit-agent-skills.py . --strict` when it does run, so the gate is fail-closed.

### `--strict` and what it escalates

`audit-agent-skills.py`'s default severities are unchanged by `--strict` - the central portfolio audit and downstream repositories that only read plain findings keep their existing meaning. `--strict` additionally treats a named, documented set of otherwise-advisory codes as gate failures for the purpose of the CLI exit code:

- `CLAUDE-NO-AGENTS` - `CLAUDE.md` does not reference `AGENTS.md`.
- `CLAUDE-GLOBAL-DEPENDENCY` - repository behavior depends on a maintainer-global `~/.claude/CLAUDE.md`.
- `SKILL-OWNER` - a project-scope skill has no `openforge-owner`.
- `SKILL-SCOPE-MISSING` - a skill has no `openforge-scope`/`owner`/`maturity`/`version` metadata.
- `SKILL-MATURITY-MISSING` - a canonical (`.agents/skills`) skill has no `openforge-maturity`. Adapter copies under `.claude/skills`/`skills` are not required to repeat it.
- `SKILL-VERIFICATION-COMMAND-OWNER` - a `deterministicChecks[].command` in a skill's verification evidence does not resolve to a repository-local owner (a `make <target>` whose `Makefile` has no such target, an `npm`/`pnpm`/`yarn` script the `package.json` does not define, or a script path that does not exist). This check is deliberately conservative: only a small set of common command forms are machine-checkable, and an unrecognized form is never flagged, because a false positive here would turn into a wrong red build across every repository that adopts `--strict`. For the same reason a `make` target is reported as unknown rather than missing when the `Makefile` has an `include` directive that could define it, and a yarn built-in such as `yarn audit` is never resolved against `package.json` scripts.

`error`-severity findings (malformed frontmatter, missing verification evidence for `verified`/`stable`, invalid names/scopes, and similar) already fail the gate in both the default and `--strict` modes; `--strict` only changes the advisory codes above.

### Why the caller does not use `on.pull_request.paths`

The caller template intentionally triggers on every pull request instead of filtering with `paths:`. If this job is configured as a required status check and GitHub skips the run because of a `paths` filter, the required check never reports and the PR is blocked indefinitely - a well-known GitHub Actions pitfall. The reusable workflow's own diff step decides internally whether to run the audit, so an application-only pull request still gets a fast, green "skipped" result instead of forcing a full contract audit or a stuck required check.

### The central portfolio audit is still second-line

`templates/scripts/audit-agent-engineering.py` records `local_agent_ci_gate` for every scanned repository - whether a repository-local gate is configured, its evidence workflow file, and, when not configured, why (`no-workflows`, `no-gate-workflow`, `missing-pull-request-trigger`, or `failure-neutralized`, the last meaning the gate workflow exists but carries `continue-on-error: true`). `generate-agent-audit-matrix.py` renders this as the `Local gate` column. A repository-local gate remains the first line of defense; the portfolio audit's role is to catch a repository that has not adopted one yet, not to be where an invalid contract is discovered for the first time.

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
