# Plugin Supply-Chain Intake Standard

OpenForge treats every externally sourced AI agent plugin, skill, hook, script, and repository as untrusted input until it passes an explicit intake policy.

## Trust model

Repository ownership, organization name, star count, publisher identity, or repository popularity MUST NOT be treated as sufficient proof of trust.

The installation decision is based on four independent properties:

| Property | Required evidence |
|---|---|
| Source identity | repository URL + immutable commit/tag reference |
| Content integrity | content digest/checksum or equivalent immutable artifact identity |
| Dependency integrity | lockfile/manifest + checksums where supported |
| Executable behavior | static inspection of hooks/scripts/install/build commands |

A trusted source does not make untrusted executable content safe.

## Intake record

Every accepted plugin SHOULD produce an installation evidence record containing:

```yaml
source:
  repository: https://example.invalid/plugin
  revision: <immutable-commit-sha>
  reference_type: commit
content:
  digest: sha256:<content-digest>
dependencies:
  manifest: <path-or-inline-reference>
  lockfile: <path-or-inline-reference>
installer:
  name: openforge
  version: <installer-version>
assessment:
  static_policy: pass
  network_policy: restricted
  approved_by: <maintainer-or-policy-id>
  approved_at: <timestamp>
rollback:
  known_good_revision: <immutable-reference>
```

The exact schema MAY be adapted to the host platform, but source identity, integrity, installer version, assessment and rollback identity must remain recoverable.

## Resolution rules

Plugin resolution MUST prefer the following order:

1. pre-approved offline trusted catalog entry
2. immutable commit or immutable artifact digest from an approved source
3. signed/tagged release with independently verified artifact identity
4. mutable branch/tag only through an explicit, auditable exception

Unpinned branch heads such as `main`, `master`, `develop`, or arbitrary version ranges MUST NOT be accepted by a release-grade installer without an explicit exception.

A mutable reference that resolves successfully today MUST NOT be assumed to resolve to the same plugin tomorrow.

## Static inspection policy

Before installation, inspect repository metadata and executable content for at least:

- package-manager lifecycle scripts
- `preinstall`, `install`, `postinstall`, build and release hooks
- shell, Python, Node, Bun, PowerShell or other executable files
- commands that fetch or execute remote content
- dynamic command construction (`eval`, shell interpolation, command execution APIs)
- credential, token, SSH key, kubeconfig or cloud metadata access
- archive extraction and writes outside the installation boundary
- network clients and hard-coded external endpoints
- persistence mechanisms and background process creation
- obfuscated or encoded executable payloads

Detection SHOULD be policy-based and explainable. A static check is a gate, not proof of safety.

## Network boundary

Plugin installation and build execution SHOULD run in an isolated environment with:

- no credentials by default
- an allowlist for package registries and required artifact stores
- DNS/network logging where available
- failure on unexpected outbound destinations when practical
- a filesystem boundary that prevents modification of unrelated repositories or host configuration

Architecture-dependent controls that cannot be enforced MUST be documented as an explicit residual risk.

## Quarantine and revocation

Maintain a denylist/quarantine record keyed by immutable revision and content digest.

When a plugin or repository is suspected to be compromised:

1. mark the affected revision/digest as quarantined
2. stop new installations and promotions
3. identify installations using the revision/digest
4. restore the last-known-good immutable revision
5. rebuild/reinstall from the known-good identity
6. retain the incident and evidence record

Revocation MUST be identity-specific. Removing only the repository name is insufficient because a compromised repository can later publish a different malicious revision.

## Offline trusted catalog

An offline catalog MUST contain immutable plugin identity and integrity metadata. A minimal entry is:

```yaml
plugins:
  - name: example-plugin
    repository: https://example.invalid/example-plugin
    revision: 0123456789abcdef0123456789abcdef01234567
    digest: sha256:<digest>
    dependencies:
      lockfile_sha256: <digest>
    installer_min_version: <version>
    status: approved
```

Offline installation MUST fail closed when the requested plugin is absent from the catalog or when the resolved content does not match the recorded digest.

## Change management integration

Plugin updates are Class C or Class D changes under [`change-management.md`](change-management.md) when they alter dependencies, executable hooks, release behavior, security boundaries, or production artifacts.

The update review MUST include:

- previous and new immutable identity
- content/dependency diff
- executable hook/script diff
- release age and cooling status
- affected workflows and runtime/toolchain requirements
- rollback identity
- security and provenance evidence

## Negative cases

Reference implementations SHOULD reject at least these cases:

| Case | Expected result |
|---|---|
| typo-squatted repository/name | reject or quarantine |
| floating branch without exception | reject |
| mutable artifact URL in release path | reject |
| install script downloads and executes remote code | reject/quarantine |
| hook accesses credentials without declared need | reject |
| digest mismatch | reject |
| revoked revision | reject |
| plugin absent from offline catalog | reject in offline mode |

## Relationship to the core standard

This standard extends [`supply-chain.md`](supply-chain.md) for repositories that consume executable plugins or AI agent skills. General dependency governance, cooling, provenance, rollback, and offline requirements remain authoritative there.
