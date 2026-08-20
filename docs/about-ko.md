# OpenForge 소개

> 오픈소스 프로젝트 Blueprint & Engineering Standards

OpenForge는 오픈소스 프로젝트를 일관된 기반 위에서 만들고 발전시키고 유지하기 위한 기준 Engineering Standard입니다.

## OpenForge가 제공하는 것

- Repository 및 문서 표준
- 영/한 문서 작성 규칙
- GitHub Issue, Pull Request, Workflow 표준
- CI/CD 및 보안 기본 기준
- Release 및 버전 관리
- 개발 도구 및 언어별 표준
- Code Intelligence 및 아키텍처 분석 가이드
- AI-assisted development 지침
- Internationalization / Localization 가이드
- OSS 라이선스 및 Supply Chain 기준
- Repository maturity를 위한 Reference Implementation Metrics
- 재사용 가능한 프로젝트 템플릿

## OpenForge가 아닌 것

OpenForge는 특정 Framework가 아니며 하나의 프로그래밍 언어, Cloud, Runtime 또는 Application Architecture를 강제하지 않습니다.

프로젝트에 필요한 기본 Engineering baseline을 제공합니다. 프로젝트 상황에 따라 예외를 둘 수 있으며, 의도적인 변경은 ADR로 기록하는 것을 원칙으로 합니다.

## 설계 철학

OpenForge는 실제 프로젝트 경험을 기반으로 발전합니다. 운영 중인 OSS 저장소의 사례를 기준으로 표준을 검증하고, 반복 가능한 좋은 관행이나 장애, 리뷰를 통해 더 나은 방법이 발견되면 표준에 다시 반영합니다.

```text
OpenForge
    ↓
OSS Project
    ↓
Implementation / Incident / Review
    ↓
Lessons & Metrics
    ↓
OpenForge Improvement
    ↺
```

## 참고 프로젝트

Reference Metrics는 Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, Beluga Manager 등의 실제 프로젝트 사례를 기반으로 합니다.

자세한 내용은 [기존 OSS 구현 사례 기반 메트릭](reference-metrics-ko.md)을 참고합니다.
