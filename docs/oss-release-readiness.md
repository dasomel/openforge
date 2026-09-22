# OSS Release Readiness Standard

File presence is not the same as external readiness. A repository can pass every existing OpenForge metric — bilingual docs present, CI green, LICENSE committed — and still fail a real first-time visitor or first-time contributor. This standard closes that gap.

> Verified against `dasomel/nfs-quota-agent` (81.8% under the existing metrics) by independent cross-model review (Claude, Codex/GPT, Gemini/agy). All three converged on the same six gaps below; each was confirmed against the live repository, not assumed.

## Rules

- **Links must resolve, not just exist.** Checking that `README-ko.md` exists does not catch a `README.md` that links to `README_ko.md`. Validate internal markdown links (and periodically, external links) in CI — do not rely on file-presence checks alone.
- **Publish discoverability metadata, not just files.** A public repository needs GitHub `topics`, a `description`, and (recommended) a social preview image and homepage URL. None of this lives in the working tree, so file-presence audits cannot see it — check it separately, e.g. via `gh repo view` / `gh api repos/<owner>/<repo>/topics`.
- **A quickstart must be exercised, not just written.** README "Quick Start" text is a claim, not evidence. Where practical, wire a clean-environment smoke test into CI (build/install/run against the documented steps) so quickstart drift is caught automatically instead of discovered by a frustrated first-time user.
- **Inbound contributions need explicit terms.** Outbound licensing (`docs/oss-compliance.md`) is not the same as inbound contribution terms. Require Developer Certificate of Origin (`Signed-off-by`) on external PRs at minimum; a full CLA is a project-specific escalation, not a portfolio default. Label a small set of issues for first-time contributors (e.g. `good first issue`) when the backlog supports it.
- **Security disclosure must be operable, not templated.** `docs/security.md` requires publishing a vulnerability-reporting process; this standard requires that the process actually works: a real private reporting channel (GitHub Private Vulnerability Reporting enabled, or an addressable maintainer contact — not a placeholder), a stated response-time expectation, and a supported-version policy. A `SECURITY.md` that promises a 48-hour response with no reachable channel behind it is worse than no promise.
- **Code of Conduct enforcement needs a real contact.** A CoC that directs reports to undefined "community leaders" with no name, address, or form is not enforceable. Name an actual reachable reporting path, even for single-maintainer projects (see `docs/maintainer-governance.md` §1).
- **Publication clearance is a judgment call, not a mandatory file.** Before flipping a repository public, the maintainer should briefly confirm there is no trademark, export-control, or third-party-privacy blocker. This is a lightweight self-attestation, not a document requirement — do not add a mandatory file for it.

## Explicitly not required portfolio-wide

`CITATION.cff` and `FUNDING.yml` are legitimate for research-adjacent or sponsorship-seeking projects, but both models agreed these are project-specific judgment calls, not a certification gate. Do not flag their absence as a compliance gap.

## Already covered elsewhere — do not duplicate

Release integrity (`docs/release.md`), maintainer governance (`docs/maintainer-governance.md`), and baseline OSS legal compliance (`docs/oss-compliance.md`) were independently reviewed and found adequate. This standard only adds what those do not cover.

## Relationship to the automated audit

`templates/scripts/audit-portfolio.py` currently scores file presence and cannot evaluate any of the rules above (a resolved link, a working GitHub API call, and an exercised quickstart are not filesystem facts). Treat this document as manual/CI-supplementary guidance until the audit engine grows the capability to check them — do not assume a high portfolio score implies compliance with this standard.

See the Korean translation: [docs/oss-release-readiness-ko.md](oss-release-readiness-ko.md).
