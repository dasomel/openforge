# CI/CD Security Standard

CI/CD is a security boundary, not only a build mechanism. Treat workflows, runners, caches, credentials, artifacts and triggers as security-sensitive infrastructure.

## 1. Workflow trust boundaries

- Treat fork PRs, issues, comments, external events and generated content as untrusted input.
- Prefer `pull_request` for untrusted code validation.
- Do not execute fork-controlled code in privileged contexts such as release or publish workflows.
- Avoid `pull_request_target`; if unavoidable, document the trust boundary and prohibit untrusted checkout/execution.
- Separate validation, release and publishing workflows.

## 2. Permissions

- Set `permissions: {}` at workflow level where possible and grant only required job permissions.
- Restrict `contents: write`, `packages: write`, `id-token: write`, deployments and secret access to the smallest job/environment.
- Release identity MUST NOT be inherited by ordinary test/build jobs.
- Prefer short-lived OIDC credentials over long-lived tokens.

## 3. Actions and reusable workflows

- Pin third-party actions to immutable commit SHAs.
- Treat reusable workflows and composite actions as dependencies.
- Review action source, transitive dependencies, ownership changes and release changes.
- Do not trust mutable tags as security identity.
- Apply the dependency cooling/review policy to action upgrades where practical.

## 4. Runner security

- Prefer ephemeral runners for untrusted or high-impact jobs.
- Separate untrusted-build runners from release/publish runners.
- Clean workspaces, credentials, caches and temporary files between jobs when runners are reused.
- Do not expose persistent developer credentials or production credentials to general CI runners.
- Monitor high-risk runner jobs for unexpected processes and network destinations.

## 5. Cache security

Cache is untrusted state and a supply-chain asset.

- Separate PR, main, release and publish caches.
- Separate dependency caches from release/publish caches.
- Do not allow untrusted workflows to write privileged caches.
- Include trust context in cache keys where practical.
- Validate restored cache content before use for release-critical jobs.
- Add cache-poisoning regression tests for high-risk workflows.

## 6. Network egress

- Build/test jobs SHOULD use allowlisted registries and services.
- Arbitrary outbound connections from privileged build/release jobs SHOULD be denied.
- Record exceptions for external services and remote download requirements.
- Investigate unexpected DNS, HTTP(S), webhook or other outbound activity from build steps.

## 7. OIDC and publishing identity

- Scope OIDC subject/audience/trust policies to repository, branch and environment.
- Grant `id-token: write` only to the job that needs it.
- Separate build identity from publish identity.
- A valid OIDC token is an authorization mechanism, not proof that executed code is safe.

## 8. Artifact handling

- Do not treat artifacts from untrusted workflows as trusted release inputs.
- Bind release artifacts to immutable commit, dependency set and builder identity.
- Verify checksums/digests after transfer or cache restore.
- Freeze the exact artifact before publish.

## 9. Security-sensitive paths

Recommended protected paths include:

```text
.github/workflows/**
.github/actions/**
Dockerfile*
package.json
lockfiles
release scripts
publishing configuration
OIDC/trust configuration
CODEOWNERS
SECURITY.md
```

Changes to these paths SHOULD receive elevated review according to the repository's governance policy.

## 10. Regression requirements

Known CI failures must become deterministic checks where practical. A runtime/toolchain migration MUST verify every workflow that can invoke the affected build, packaging or release contract.
