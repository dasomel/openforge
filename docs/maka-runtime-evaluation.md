# Apache Maka Runtime Evaluation for OpenForge

Verified against Apache Maka (Incubating) public documentation and repository on **2026-09-09**.

Decision: **partially adopt architectural patterns; do not make Maka a core OpenForge runtime dependency now.**

OpenForge remains runtime/model neutral. Maka is a useful reference implementation and optional evaluation harness, especially for durable event logs, one execution authority, workspace instructions, permission boundaries, Agent Graph, and declarative multi-arm evaluation.

## Current Maka architecture relevant to OpenForge

Apache Maka currently describes one execution authority: **Runtime Host**. Desktop, TUI, CLI, bots, and Eval are clients. Runtime Host owns Session/Turn identity, agent lifecycle, continuation, tools, permissions, and runtime events.

The Runtime Event Log is the durable source for model messages, tool calls/results, permission decisions, and termination facts; UI/context/recovery are projections rather than the only copy.

Current public surfaces include:

- Desktop workspace
- interactive TUI / `maka` CLI
- non-interactive `maka run`
- `maka eval run <spec> --out <directory>`
- Agent Graph execution
- local tools such as Read/Write/Edit/Bash/Glob/Grep
- permission policy, watchdog/abort/error classification
- multiple model connections
- append-only/immutable evaluation attempts and result artifacts

References:

- https://github.com/apache/maka
- https://github.com/apache/maka/blob/main/ARCHITECTURE.md
- https://github.com/apache/maka/blob/main/docs/architecture/runtime-host-architecture.md
- https://github.com/apache/maka/blob/main/packages/cli/README.md
- https://github.com/apache/maka/blob/main/packages/eval/README.md

## OpenForge mapping

| Maka concept | OpenForge mapping | Adoption |
|---|---|---|
| Runtime Host as sole execution authority | Agent Execution Security request/runtime authority boundary | pattern adopted |
| Runtime Event Log | execution evidence / behavior trace / audit lineage | pattern adopted |
| Workspace instructions | `AGENTS.md` + linked engineering standards | already adopted |
| Permission engine | canonical resolved invocation + authorization/approval contract | concept adopted, implementation stays project-specific |
| Agent Graph | task decomposition / child-agent orchestration | optional, not baseline |
| Eval Experiment/Cell/Attempt/Result | Agent Behavior + deterministic evaluation evidence | pattern compatible |
| Model connection catalog | runtime-specific provider configuration | intentionally outside OpenForge core |
| Desktop/TUI product | developer UX | not an OpenForge baseline dependency |

## Security boundary assessment

Maka's architecture is directionally aligned with OpenForge in important ways:

1. one component owns runtime execution state rather than every client owning authority;
2. dangerous tools pass through a permission boundary;
3. durable execution history supports recovery/audit;
4. Eval does not become a second execution authority;
5. remote Runtime Host profiles explicitly bind a target/root and credentials.

OpenForge still requires stronger project-specific guarantees where a side effect matters:

- authorization must consume the canonical fully resolved tool/target/arguments artifact;
- high-risk authority should be bounded/expiring;
- human approval, where required, binds the exact invocation digest;
- request-side denial must occur before executor/sandbox handoff;
- post-state/effective enforcement is distinct from successful command return;
- evidence must be recomputable at the project's real mutation boundary.

Therefore Maka's permission/runtime model is a useful substrate/reference but is not treated as proof that an OpenForge project's execution-security profile is complete.

## Credential and local-data considerations

The released Maka CLI currently requires a configured model connection for agent turns; first-run setup uses provider credentials. Maka's public documentation also describes local credential/profile storage and notes that the CLI is beta/under active development.

OpenForge must not automate a user's interactive provider login, copy browser/session credentials, or bypass provider account controls merely to satisfy a benchmark. Model credentials remain user/runtime-owned secrets.

## Optional repository PoC protocol

A repository can evaluate Maka without making it a required dependency.

Prerequisites:

```bash
node --version                 # >= Maka's documented minimum
npm install --global maka-agent@next
maka --version
```

From a clean clone of the target repository:

```bash
maka run "Read AGENTS.md and the linked engineering standards. Review one open issue, propose the smallest coherent implementation plan, list required verification, and do not mutate files."
```

Then repeat the same task with another configured model connection/profile. Record:

- repository revision
- Maka version
- model/provider identity
- exact task text
- permission decisions
- tool calls
- result status
- duration/usage where available
- whether the output respected AGENTS/security/evidence boundaries

For a real benchmark, prefer Maka Eval's declarative experiment semantics and immutable per-cell attempts rather than manually comparing unrelated sessions.

## Multi-model comparison policy

Issue #9 originally proposed executing at least two of GPT / Claude / Gemini. That remains a valid **optional experiment**, but it is not a prerequisite for OpenForge architecture adoption because:

- model credentials are external user/runtime state;
- OpenForge does not own those provider accounts;
- a credential-dependent ad-hoc run would not be reproducible CI evidence;
- OpenForge already has model-neutral Agent Behavior rules and repository-specific execution-security evidence;
- making Maka core depends on runtime stability/operational value, not one model leaderboard.

If a maintainer chooses to run the comparison, the same frozen task/revision/budget/verifier must be used for every arm. Unmatched/failed cells should not be silently dropped from comparison.

## What OpenForge adopts now

Adopt as shared principles:

- one explicit execution authority per runtime boundary;
- append-only/recomputable execution evidence;
- model/provider separation from repository engineering policy;
- workspace-level instructions;
- explicit permissions before dangerous tool effects;
- graph orchestration only when decomposition adds value;
- evaluation attempts/results as durable evidence rather than screenshots/claims.

## What OpenForge does not adopt now

- Maka as a mandatory dependency of generated repositories;
- Maka-specific profile/data formats as OpenForge standards;
- provider credentials managed by OpenForge;
- mandatory Desktop/TUI workflow;
- an assumption that a Maka permission approval is sufficient for project-specific privileged mutation;
- autonomous destructive execution.

## Re-evaluation triggers

Revisit a stronger integration when at least one of these becomes true:

- two or more portfolio projects need the same persistent agent runtime rather than project-local execution;
- Maka reaches a stability level suitable for a shared operational dependency;
- OpenForge needs cross-model benchmark experiments that its current Agent Behavior harness cannot express;
- Agent Graph materially reduces cycle time on measured portfolio work without weakening evidence/permission boundaries.

Until then the sustainable choice is **partial architectural adoption + optional PoC, no core dependency**.