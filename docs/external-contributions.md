# External Contributions Registry

Korean: [external-contributions-ko.md](external-contributions-ko.md)

OpenForge records public discussions and contributions that external developers bring to portfolio repositories: who, which thread, what, and its current state. The registry is reviewable data in `portfolio/external-contributions.json`, rendered into the [portfolio dashboard](portfolio-dashboard.md). It is a record of attention and credit, not a measure of quality, endorsement or commitment to adopt anything.

## What counts as external

- The account is not the repository owner and not a maintainer of the portfolio.
- The account is not a bot or automation (dependabot, CI apps, release tooling).
- The thread is public on GitHub and the account resolves on GitHub.

Accounts that cannot be verified are excluded: a name seen only in a secondhand summary, an account that does not resolve on GitHub, or one with no trace in the cited thread is not recorded. Re-add it only after the thread itself shows the contribution.

## Files

| Path | Role |
|------|------|
| `schemas/external-contributions-v1.schema.json` | Versioned contract (`openforge-external-contributions/v1`) |
| `portfolio/external-contributions.json` | The registry: `schema_version`, `observed_at`, `entries[]` |
| `templates/scripts/validate-external-contributions.py` | Schema plus semantic validation; run in CI |
| `tests/fixtures/external-contributions/` | Synthetic fixtures only; never copied into `portfolio/` |

## Entry fields

| Field | Rule |
|-------|------|
| `id` | Kebab-case, unique |
| `repository` | `owner/name` of a project in `portfolio/projects.json` |
| `kind` | `issue` or `pull_request` |
| `number` | Thread number; `(repository, number)` is unique |
| `url` | Exactly `https://github.com/<repository>/issues/<number>` for `issue`, `.../pull/<number>` for `pull_request` |
| `contributors` | Non-empty list of bare GitHub handles, unique and sorted case-insensitively |
| `contribution_type` | See below |
| `summary` | Short English description, at most 240 characters |
| `state` | `open`, `closed` or `merged` (`merged` only for pull requests) |
| `outcome` | Optional short text, for example what was adopted |
| `observed_at` | UTC `YYYY-MM-DDTHH:MM:SSZ`; not in the future and not later than the record's `observed_at` |

Entries are sorted by `(repository, number)`.

`contribution_type` values:

| Value | Meaning |
|-------|---------|
| `design` | Design artwork or a design reference |
| `proposal` | A change or capability proposal |
| `design-review` | Review of an existing design from the contributor's own perspective |
| `support-offer` | An offer of help or collaboration from a related project |
| `bug-report` | A defect report |
| `docs` | Documentation contribution |

## Privacy rule

- Store GitHub handles only, without `@`. No emails, real names or other personal data; the validator rejects `@` in a handle.
- Record public threads only. Never summarize private reports, security disclosures or private messages.

## State is a snapshot

`state` and `outcome` describe the thread as of `observed_at`; they are not live. The dashboard says so next to the numbers. A thread can change after the observation, so re-check before relying on a state.

## Refreshing

```bash
gh issue view <number> --repo <owner>/<repo> --json state,closedAt,url,author
gh pr view <number> --repo <owner>/<repo> --json state,mergedAt,url,author
gh issue view <number> --repo <owner>/<repo> --comments   # confirm who actually contributed
```

Update `state`, `outcome` and both `observed_at` values, then regenerate and validate:

```bash
python3 templates/scripts/validate-external-contributions.py
python3 templates/scripts/generate-portfolio.py
python3 templates/scripts/generate-portfolio.py --check
```

`--now YYYY-MM-DDTHH:MM:SSZ` makes the future-timestamp check deterministic.

## Dashboard

`generate-portfolio.py` adds an `external_contributions` key to `portfolio/dashboard.json` (counts by state, type and repository, plus the entries with URLs) and an "External contributions" section to the dashboard page. The key is additive: `openforge-dashboard/v1` is unchanged, and it is omitted when the registry file is absent.
