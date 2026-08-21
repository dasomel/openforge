# Reproducible Build Standard

Release-critical builds SHOULD be reproducible from immutable source, dependency and toolchain inputs.

## Build identity

Record or bind:

- source commit
- dependency lock/checksum state
- compiler/interpreter/runtime version
- build tool version
- base image/builder identity
- relevant environment/profile
- generated input versions
- resulting artifact digest

## Controls

- Pin release-critical inputs.
- Prefer hermetic/isolated builds where practical.
- Do not rely on undeclared runner-preinstalled tools.
- Normalize timestamps and nondeterministic metadata where possible.
- Compare repeated clean builds for important artifacts.
- Support offline reproduction when the project claims air-gap/offline capability.
- Preserve build evidence needed to reconstruct the dependency and builder context.

## Trust principle

A reproducible build proves consistency of a process and inputs; it does not by itself prove that the source or dependency set is benign. Apply supply-chain, malware and security policy separately.
