# 릴리스 표준

예측 가능한 릴리스 생명주기를 사용하고 릴리스 산출물을 특정 commit으로 추적 가능하게 유지합니다.

## 버전 관리

라이브러리와 애플리케이션은 가능한 경우 Semantic Versioning을 사용합니다.

```text
MAJOR.MINOR.PATCH
```

Breaking change는 명확하게 문서화합니다.

## 변경 기록

다음 두 파일을 유지합니다.

```text
CHANGELOG.md
CHANGELOG-ko.md
```

English와 Korean 변경 기록은 의미가 일치해야 합니다.

## 릴리스 체크리스트

- 릴리스 commit의 CI 통과
- 보안/dependency 검사 검토
- 버전 일관성 확인
- changelog 업데이트
- 영/한 release note 작성
- 알려진 commit에서 artifact 생성
- 필요한 경우 rollback/recovery 문서화
