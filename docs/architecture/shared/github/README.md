# GitHub Adapter: 통신과 Provider DTO

> ID: `GITHUB-ADAPTER` · 소유: `backend/app/shared/github` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: GitHub HTTP·OAuth·설치 token adapter를 변경할 때

```text
shared/github/
├─ client.py             검증된 host·HTTP·pagination
├─ oauth_client.py       OAuth code 교환·사용자 조회
├─ installation_auth.py  App JWT·installation token 획득
├─ provider_models.py    GitHub 응답 모델, 업무 모델 아님
└─ errors.py             rate limit·권한·timeout의 중립 오류
```

Auth, Repository, PR, Webhook/분석 흐름이 공통으로 쓰는 기술 adapter다. '최근 30개', '새 PR 자동 분석', 'OWNER만 연결'은 domain 정책이며 client에 하드코딩하지 않는다.

OAuth token은 사용자 인증용, installation token은 설치된 저장소 접근용이다. token scope를 필요한 설치/저장소/권한으로 제한한다. provider DTO를 domain 계약으로 바꾸는 작업은 소비 domain이 수행한다. [S-GH-APP](../../reference/SOURCES.md#s-gh-app), [S-GH-INSTALL](../../reference/SOURCES.md#s-gh-install)

Host·scheme·redirect를 검증하고 credential이 다른 host로 전달되지 않게 한다. TLS 검증을 켠다. PR body의 URL/설치 ID/파일 경로를 그대로 fetch 명령으로 사용하지 않는다. path는 인코딩/정규화하고 허용한 GitHub API 경로로만 조립한다.

pagination Link, ETag/304, rate-limit headers, Retry-After를 지원한다. 401은 token 갱신 가능 여부, 403은 권한/한도, 404는 가용성/권한 문제로 구별한다. 긴 대기는 Job available_at으로 넘기고 API loop에서 sleep하지 않는다. [S-GH-RATE](../../reference/SOURCES.md#s-gh-rate)

설치 token은 단기 메모리 cache만 허용하며 DB에 영구 저장하지 않는다. 필요할 때 재발급하고 private key는 서버 비밀 설정으로 관리한다. 원문 응답 body는 로그/trace에 남기지 않는다. 요청/응답 크기와 timeout을 모두 제한한다.

테스트: 실제 GitHub 호출 없이 HTTP fixture로 pagination·304·권한 철회·rate limit·token 만료·악성 redirect를 검증한다. 별도로 테스트 저장소를 사용한 수동 contract smoke test를 한다. 이 문서 패키지 자체는 그 테스트를 실행한 결과가 아니다.
