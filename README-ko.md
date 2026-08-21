English | [한국어](README-ko.md)

# OpenForge

> **오픈소스 프로젝트 Blueprint & Engineering Standards**

OpenForge는 품질 높은 오픈소스 프로젝트를 만들고 발전시키고, 배포하고, 운영하고 유지하기 위한 재사용 가능한 Engineering Foundation입니다.

Repository structure, documentation, GitHub workflow, CI/CD, security, supply-chain, change impact, upgrade/compatibility, developer environment, AI-assisted engineering, container/IaC, release, maintainer governance, resilience, tooling, deployment baseline, 디자인 템플릿과 프로젝트 lifecycle을 공통 기준으로 관리합니다.

## 핵심 원칙

- English를 canonical project language로 사용하고 Korean을 first-class translation으로 제공합니다.
- 프로젝트는 기본적으로 재현 가능하고, 문서화되고, 테스트 가능하며, 관측 가능하고, 접근 가능하며, 안전해야 합니다.
- GitHub Issue와 Pull Request를 주요 변경 관리 수단으로 사용합니다.
- Architecture Decision은 ADR로 기록합니다.
- Merge 전에 CI가 품질을 검증합니다.
- Security와 Supply Chain을 프로젝트 생명주기에 포함합니다.
- Dependency 호환성만으로 최신 버전을 즉시 채택하지 않습니다.
- Dependency/runtime/toolchain 변경은 workflow 전체 영향 분석을 수행합니다.
- AI agent와 repository-local instruction은 잠재적으로 untrusted execution input으로 취급합니다.
- 단독 maintainer OSS도 사람 수가 아니라 risk와 automated control을 기준으로 governance를 적용합니다.
- Template은 출발점이며 모든 프로젝트에 그대로 적용되는 drop-in configuration이 아닙니다.

## 재사용 가능한 템플릿

```text
templates/
├── github/          # PR / CODEOWNERS
├── workflows/       # CI / release / SBOM
├── scripts/         # toolchain / validation
├── policy/          # dependency / engineering policy
├── container/       # Docker baseline
├── kubernetes/      # Deployment / Service / Ingress / NetworkPolicy / PDB / Kustomize
├── gitops/          # Argo CD / GitOps
├── identity/        # OIDC / SSO
├── observability/   # health / metrics / traces / logs
├── backup/          # backup / restore
├── offline/         # air-gap bundle
└── design/          # README / landing / diagram / status / design tokens
```

각 템플릿은 대상 프로젝트의 runtime, permission, platform, deployment model, threat model에 맞게 조정해야 합니다.

## 프로젝트 생명주기

```text
Idea → Definition → Repository Bootstrap → Standards + Templates
→ Implementation → Impact / Supply Chain Review → CI / Security / Testing
→ Release / Publish Verification → Operations → Incident Learning → OpenForge Improvement
```

## 참고 프로젝트

OpenForge는 Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, Beluga Manager 등의 실제 OSS 개발 사례에서 반복 가능한 Engineering Practice를 추출합니다.

## License

Apache License 2.0.
