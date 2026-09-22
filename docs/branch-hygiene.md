# Branch Hygiene

OpenForge-managed repositories should keep long-lived branches intentional and delete short-lived implementation branches after their pull request is merged.

## Policy

- `main` or the repository default branch is never deleted automatically.
- Protected/release branches are retained.
- Branches with an open pull request are retained.
- Branches from forks are never deleted by repository automation.
- A same-repository pull-request head may be deleted automatically only after `pull_request.merged == true`.
- Unmerged/closed branches are not deleted automatically because they may contain unpublished work; remove them only after an explicit stale-work review.
- Generated/audit branches should use a recognizable prefix and be deleted after the corresponding PR is merged or superseded.
- Branch deletion is repository hygiene only; merged commit/PR/audit history remains the evidence source.

## Recommended branch classes

| Class | Examples | Retention |
| --- | --- | --- |
| default | `main` | permanent |
| release | `release/*` | intentional, reviewed |
| active feature/fix/docs | `feat/*`, `fix/*`, `docs/*`, `refactor/*`, `chore/*` | until PR merged/closed review |
| generated audit/status | `agent-audit/*`, `portfolio-status/*` | delete after merge/supersession |
| dependency automation | `dependabot/*`, Renovate equivalents | provider/PR lifecycle |
| temporary | `tmp`, `test/*`, ad-hoc scratch | remove as soon as no longer required |

## Safe automatic cleanup

Use the reusable template in `templates/github/cleanup-merged-branch.yml`. It runs only for a merged pull request whose head repository is the same repository, requests only `contents: write`, rejects the default branch, and deletes only that exact merged head ref.

Existing branches require a separate one-time audit because squash/rebase merge histories do not always make `git merge-base --is-ancestor` sufficient to prove that a branch is disposable. The safe proof is the PR relationship plus merged/superseded state.

## Portfolio review rule

Branch hygiene should be reviewed together with stale pull requests. Before deleting a branch, record at least one of:

1. the branch is the head of a merged PR;
2. the branch is generated output whose newer canonical PR/state supersedes it; or
3. an explicit maintainer decision marks the unmerged work as abandoned.

Never infer disposability from branch age alone.
