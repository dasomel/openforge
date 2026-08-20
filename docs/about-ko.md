# OpenForge 소개

> **오픈소스 프로젝트 Blueprint & Engineering Standards**

OpenForge는 품질 높은 오픈소스 프로젝트를 일관된 Engineering Foundation 위에서 만들고 발전시키고 유지하기 위한 공통 표준입니다.

English | [한국어](about-ko.md)

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
- OSS 라이선스 및 Software Supply Chain 기준
- Repository maturity를 위한 Reference Implementation Metrics
- 재사용 가능한 프로젝트 템플릿

## OpenForge가 아닌 것

OpenForge는 특정 Framework가 아니며 하나의 프로그래밍 언어, Cloud, Runtime 또는 Application Architecture를 강제하지 않습니다.

프로젝트에 필요한 기본 Engineering baseline을 제공합니다. 프로젝트 상황에 따라 예외를 둘 수 있으며, 중요하거나 의도적인 예외는 ADR로 기록합니다.

## 설계 철학

OpenForge는 실제 OSS Engineering 경험을 기반으로 발전합니다. 운영 중인 프로젝트의 사례를 기준으로 표준을 검증하고, 반복 가능한 좋은 관행, 장애, 리뷰 또는 더 나은 Engineering Approach가 발견되면 표준에 다시 반영합니다.

```text
OpenForge
    ↓
OSS Project
    ↓
Implementation / Incident / Review
    ↓
Lessons / Metrics
    ↓
OpenForge Improvement
    ↺
```

## 참고 프로젝트

Reference Implementation에는 Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, Beluga Manager 등의 실제 프로젝트가 포함됩니다.

이 프로젝트들은 의존 대상이 아니라 참고 구현입니다. OpenForge는 반복 가능한 Engineering Practice를 표준화하면서 각 프로젝트의 구현 선택권을 유지합니다.

자세한 내용은 [기존 OSS 구현 사례 기반 메트릭](reference-metrics-ko.md)을 참고합니다.

## 언어 정책

English를 canonical project language로 사용하고 Korean을 first-class translation으로 유지합니다. 한국어 파일명은 `<name>-ko.md` 규칙을 사용합니다.

자세한 문서 정책은 [문서 표준](documentation-ko.md)을 참고합니다.

## 생명주기

OpenForge는 자신이 권장하는 Engineering Discipline을 스스로 적용합니다.

```text
Standard → Apply → Measure → Learn → Improve → Standardize
```
