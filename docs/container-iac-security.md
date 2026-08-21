# Container, Kubernetes and IaC Security Standard

Cloud-native OSS must treat container, Helm, Kubernetes and infrastructure-as-code inputs as part of the software supply chain.

## Containers / OCI

- Pin release-critical base images by digest.
- Pin downloaded tools and package inputs with checksum/signature verification where supported.
- Prefer minimal images and non-root execution where compatible.
- Generate SBOM/provenance for release images.
- Verify image digest after build, mirror and promotion.
- Do not use mutable `latest` tags in release paths.
- Rebuild from a known-good dependency/input snapshot after a compromised base image or package is identified.

## Helm / Kubernetes

- Pin chart and dependency versions/digests.
- Treat Helm values, initContainers, hooks and startup commands as executable configuration.
- Review privileged settings: hostPath, hostPID, hostNetwork, privileged, capabilities and service-account permissions.
- Require image identity by immutable digest for controlled deployments.
- Define RBAC least privilege and avoid unnecessary cluster-wide permissions.
- Protect Secrets and avoid embedding sensitive values in chart or GitOps artifacts.
- Verify promoted image/chart identities at admission or deployment where practical.

## IaC

For Terraform/OpenTofu/Packer/Ansible and similar tooling:

- commit dependency/provider/plugin lock and checksum data where supported
- pin module/provider/plugin versions
- verify external downloads
- prohibit unverified remote scripts by default
- review plan/output changes for security impact
- protect state and credentials
- preserve a last-known-good infrastructure configuration

## Remote execution

Avoid unverified patterns such as:

```text
curl <url> | sh
wget <url> | bash
python <remote-url>
```

An exception requires immutable source identity, integrity verification, reason and review.
