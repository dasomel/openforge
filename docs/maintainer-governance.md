# OSS Maintainer Governance Standard

OpenForge supports both single-maintainer and multi-maintainer projects. Human-count requirements MUST NOT become a barrier to small OSS projects.

## 1. Maintainer model

A project MUST document at least:

- who currently owns/maintains the repository
- who can merge changes
- who can publish releases/packages when applicable
- security reporting contact
- recovery/contact path

A single maintainer is an accepted project state.

## 2. Risk-based review

Review requirements are determined by change risk, not maintainer count.

| Change | Default control |
|---|---|
| Documentation-only | Automated CI; self-review acceptable |
| Low-risk code/test change | CI + maintainer review according to project policy |
| Dependency/runtime/toolchain change | CI + dependency/change-impact evidence |
| `.github/workflows`, OIDC, publishing, security/IAM changes | Elevated review where another qualified reviewer is available; otherwise explicit self-approval + automated security gates + documented exception |
| Emergency security change | Emergency path + post-change independent review when available |

## 3. Two-person review

Two-person approval is a RECOMMENDED control for high-impact changes, not a universal requirement.

When a project has only one active maintainer:

- use mandatory automated checks
- use CODEOWNERS or protected paths when another qualified contributor exists
- require explicit change classification and impact analysis
- require release/security evidence
- prefer delayed or staged rollout for high-impact releases where practical
- perform retrospective review after emergency changes

## 4. Maintainer account security

Even single-maintainer projects SHOULD use:

- MFA/passkeys
- short-lived credentials where possible
- minimal GitHub permissions
- separate release/publish credentials
- protected release branches/tags
- private security reporting
- credential recovery documentation

## 5. Succession and recovery

Projects should document a recovery path for repository ownership, package publishing and release credentials without requiring a permanent second maintainer.

## 6. Governance principle

The objective is **independent control where feasible**, not an artificial staffing requirement.

```text
small project
→ strong automation
→ explicit risk classification
→ protected security-sensitive paths
→ independent review when available
```
