# Package and Artifact Identity Standard

Package names, namespaces and publisher identities are part of the supply chain trust model.

## Threats

Projects SHOULD consider:

- typosquatting
- dependency confusion
- namespace squatting
- evil-twin packages/extensions
- ownership transfer
- unexpected publisher changes
- suspicious low-age or low-download dependencies

## Requirements

- Verify package source and publisher/namespace identity for new dependencies.
- Do not resolve an internal/private dependency from a public registry merely because the public name matches.
- Review ownership, namespace and publisher changes for security impact.
- Apply cooling/review to newly published packages where practical.
- Record immutable package identity and integrity metadata.
- Prefer approved registries/mirrors for release builds.
- Quarantine known-malicious or withdrawn packages.

## Developer tooling

The same rules apply to IDE extensions, agent plugins, CLI tools and registry artifacts.
