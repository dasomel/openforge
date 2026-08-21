# Container, Kubernetes 및 IaC 보안 표준

Cloud-native OSS에서는 container, Helm, Kubernetes, IaC input을 software supply chain의 일부로 취급합니다.

## Container / OCI

- release-critical base image를 digest로 고정합니다.
- downloaded tool과 package input은 가능한 경우 checksum/signature로 검증합니다.
- compatibility가 허용하면 최소 image와 non-root 실행을 우선합니다.
- release image에 SBOM/provenance를 생성합니다.
- build, mirror, promotion 후 image digest를 검증합니다.
- release path에서 mutable `latest` tag를 사용하지 않습니다.
- compromised base image/package 발생 시 검증된 last-known-good input으로 rebuild합니다.

## Helm / Kubernetes

- chart와 dependency version/digest를 고정합니다.
- Helm values, initContainer, hook, startup command를 executable configuration으로 취급합니다.
- privileged, hostPath, hostPID, hostNetwork, capability, ServiceAccount 권한을 검토합니다.
- controlled deployment에서는 immutable image digest를 사용합니다.
- RBAC least privilege를 적용합니다.
- Secret을 chart/GitOps artifact에 평문으로 넣지 않습니다.
- 가능한 경우 admission/deployment에서 image/chart identity를 검증합니다.

## IaC

Terraform/OpenTofu/Packer/Ansible 등은 lock/checksum, version pinning, external download 검증, remote script 제한, plan security review, state/credential 보호, last-known-good 구성을 적용합니다.

## Remote Execution

다음을 검증 없이 사용하지 않습니다.

```text
curl <url> | sh
wget <url> | bash
python <remote-url>
```

예외에는 immutable source identity, integrity verification, reason, review가 필요합니다.
