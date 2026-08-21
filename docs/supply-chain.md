# Supply Chain Security Standard

OpenForge defines software supply-chain security as a portfolio-wide engineering control. Compatibility is necessary for an upgrade, but compatibility alone is never a trust decision.

## Adoption flow

```text
discover
  → compatibility
  → integrity / provenance
  → release age / cooling
  → dependency diff review
  → isolated build / test
  → security / evidence checks
  → canary
  → progressive adoption
```

"Latest compatible" MUST NOT by itself justify adoption.

## Immutable inputs

Release-critical inputs SHOULD have an immutable, auditable identity.

- Use lockfiles and exact versions for application dependencies.
- Verify package integrity/checksum metadata.
- Pin container images, Helm/OCI artifacts and downloaded tools to immutable digests or verified checksums.
- Pin GitHub Actions to commit SHA.
- Do not use `latest`, floating image tags, unbounded dependency ranges or mutable download URLs in release paths without an explicit exception.
- Record source revision, dependency lock state, builder/tool versions and artifact digest.

## Cooling and freshness

The portfolio default for routine third-party dependency adoption is a **14-day minimum release-age/cooling period**.

Cooling is a risk-reduction control, not a replacement for vulnerability scanning. Security/emergency updates may bypass cooling only through an explicit exception recording the exact version, reason, affected scope, evidence, approver, rollback target and review date.

## Dependency update review

Every dependency update should expose:

- previous and new version
- direct and transitive dependency changes
- lockfile/checksum changes
- release age/timestamp
- integrity and provenance status
- build/install script or generated-code changes
- advisory, revocation or withdrawal status
- affected artifacts

Prefer automated dependency-diff evidence in pull requests.

## Build-time trust boundary

Install hooks, build scripts, proc-macros, code generators, plugins, test helpers and package-manager hooks are executable supply-chain inputs.

High-risk build/test jobs SHOULD:

- use least-privilege credentials
- use isolated runners or containers where practical
- restrict outbound network access to allowlisted services
- fail on unexpected outbound access
- avoid credentials unnecessary for compilation/testing
- preserve investigation evidence

A successful application test does not prove that the build process was trustworthy.

## SBOM and provenance

Release evidence SHOULD cover runtime and build-time dependencies.

```text
source revision
  → dependency/tool manifest
  → builder identity/version
  → build/test evidence
  → artifact digest
  → release/promotion record
```

## Canary and progressive adoption

A newly verified dependency release MUST NOT be rolled out blindly across all governed repositories.

Use a designated canary, clean build/regression tests, security/provenance checks and controlled promotion. Promote the exact verified version/digest rather than re-resolving a floating range.

## Quarantine and rollback

Each release line SHOULD retain a last-known-good dependency manifest or lock snapshot.

When a version is suspected to be malicious, compromised, withdrawn or unexpectedly altered:

1. quarantine the affected version/digest
2. prevent new promotion
3. identify affected repositories/artifacts
4. restore the last-known-good dependency set
5. rebuild and verify from immutable inputs
6. preserve incident/evidence records

Rollback MUST NOT depend on whatever the upstream registry currently resolves.

## Offline and air-gapped verification

Offline release profiles MUST be reproducible from an approved dependency/artifact/cache bundle without live external resolution.

Bundles SHOULD contain exact manifests/lockfiles, package artifacts, checksums/signatures, tool versions, base-image or OCI references and SBOM/provenance evidence.

Missing or unverified inputs SHOULD fail closed.

## Emergency updates

Security urgency may justify bypassing the cooling period, but not bypassing integrity and provenance checks.

Emergency updates MUST still use an exact immutable version/digest, verify available integrity/provenance, run focused regression tests, record approval and rollback, and receive post-emergency review.

## Ecosystem minimums

| Ecosystem | Minimum control |
|---|---|
| npm / pnpm | lockfile, frozen install, integrity verification, lifecycle-script review |
| Go | `go.sum`, checksum verification, pinned toolchain/tools |
| Rust | `Cargo.lock`, locked builds, checksum/registry verification |
| Python | lock or hash-pinned requirements, pinned build tools |
| Maven / Gradle | dependency/plugin version control, repository integrity, dependency-tree review |
| OCI / Helm | immutable digest, provenance/signature verification where available |
| Packer / OS images | pinned packages/tools, checksums/signatures, input manifest |
| Nix | flake/input lock, immutable source references, offline cache verification |
| GitHub Actions | commit-SHA pinning and reviewed action updates |

Projects MAY add stricter controls based on privilege, artifact sensitivity or deployment environment.

## Governance

OpenForge is the reference implementation for portfolio policy. Repository-specific supply-chain policies SHOULD link back to this standard instead of inventing incompatible rules.

This standard is maintained together with `docs/change-management.md`, which requires dependency/runtime/toolchain changes to perform workflow-wide impact analysis.
