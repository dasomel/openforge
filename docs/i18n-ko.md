# 다국어 표준

UI를 제공하는 프로젝트는 처음부터 다국어를 고려합니다.

## 초기 locale

```text
en-US — English
ko-KR — 한국어
```

## 규칙

- 최초 방문 시 브라우저 locale을 감지합니다.
- 사용자가 언어를 직접 선택할 수 있어야 합니다.
- 선택한 locale을 유지합니다.
- 사용자 노출 문자열을 하드코딩하지 않습니다.
- Translation key를 사용합니다.
- 날짜, 시간, 숫자를 locale에 맞게 표시합니다.
- Backend API와 Domain Model은 locale-neutral로 유지합니다.
- Topic, Table, Job, Namespace와 같은 실제 리소스 이름은 번역하지 않습니다.
- 사용자 노출 key를 추가할 때 English와 Korean 번역을 함께 추가합니다.
- 가능한 경우 CI에서 번역 key 누락을 검증합니다.

## Resource

```text
locales/
├── en-US/
└── ko-KR/
```
