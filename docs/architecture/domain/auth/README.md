# Auth: 서비스 로그인과 세션

> ID: `AUTH` · 소유: `backend/app/domain/auth` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 로그인·세션·인증 의존성을 변경할 때

## 소유권과 구조

GitHub로 사용자를 인증하고 우리 서비스의 로그인 상태를 만든다. 저장소 설치·Workspace 역할·분석 정책은 소유하지 않는다.

```text
auth/
├─ api.py               CurrentPrincipal·인증 공개 계약
├─ router.py            로그인 시작/Callback/갱신/로그아웃
├─ service.py           OAuth 완료·세션 발급/철회
├─ repository.py        OAuth 시도·Refresh Session 저장
├─ models.py            LoginAttempt·RefreshSession
├─ dto.py               LoginResult·SessionResult
├─ dependencies.py      인증 사용자 획득
├─ exceptions.py        LoginRejected·SessionExpired
└─ schema/
   ├─ request.py
   └─ response.py
```

## 흐름

GitHub OAuth 로그인만 제공한다. 이메일/비밀번호 회원가입은 MVP에서 제외한다. 로그인 시작 시 서버에 만료되는 일회성 state를 기록한다. Callback의 state를 원자적으로 소비하고 OAuth code를 서버에서 교환한다. GitHub 사용자 숫자 ID로 `user.api`를 통해 계정을 조회/생성한다. 로그인 이름이나 이메일을 계정 고유키로 사용하지 않는다.

OAuth web flow의 외부 계약은 [S-GH-OAUTH](../../reference/SOURCES.md#s-gh-oauth)를 기준으로 구현/검증한다.

OAuth access token은 GitHub 사용자 확인에만 사용하고 목적 완료 뒤 보존하지 않는다. 저장소 접근은 `repository`의 GitHub App 설치 계약을 따른다. GitHub token과 우리 서비스 access token을 서로 대체하지 않는다.

## 세션 기본값 — 설계 제안

Access JWT는 15분, Refresh는 서버 DB에 해시만 저장하는 불투명 난수 토큰으로 7일을 제안한다. 숫자 조정은 이 문서만 수정한다. Access는 프론트 메모리, Refresh는 `Secure; HttpOnly; SameSite=Lax; Path=/`인 host-only 쿠키에 둔다. 브라우저 API를 프론트 동일 출처 `/api` 프록시로 통일한 경우의 설정이다. 직접 cross-site 호출로 바꾸면서 이 설정을 그대로 쓰지 않는다.

Refresh는 원자적 rotation과 token family 철회를 지원한다. 프론트는 갱신 요청을 single-flight로 묶어 동시 갱신 경쟁을 줄인다. 로그아웃은 해당 세션을 철회한다. MVP의 Access token은 만료 전까지 남을 수 있으므로 Worker/중요 동작은 사용자 활성 상태와 권한을 다시 확인한다.

JWT의 알고리즘 allowlist·issuer·audience·exp를 검증한다. 역할을 JWT에 넣어 영구 권한으로 신뢰하지 않는다. OAuth redirect URL/return URL은 allowlist로 제한한다. 쿠키를 사용하는 갱신·로그아웃에는 Origin 검사와 CSRF 보호를 적용한다. 실제 OAuth 옵션 지원 여부와 프록시 Cookie 전달은 구현 시 통합 테스트 대상이다.

## 데이터와 경계

`LoginAttempt(state_hash, expires_at, consumed_at)` 및 `RefreshSession(user_id, token_hash, family_id, expires_at, revoked_at)`는 auth 소유다. 개인정보 프로필은 user 소유다. 요청/로그에 code·state·token 원문을 남기지 않는다.

물리 컬럼·인덱스는 [인증 스키마](../../contracts/schema/IDENTITY.md)를 따른다. LoginAttempt는 purpose로 로그인/설치 state를 분리하고 브라우저 바인딩 해시를 검증한다. 설치 목적에는 사용자·Workspace를 바인딩하며 repository는 auth 공개 계약으로 생성·소비한다. Refresh 계열은 최초 발급 시 정한 절대 만료를 유지하고 rotation으로 연장하지 않는다. 재사용 판별을 위해 교체된 행도 계열 만료/보관 정책까지 유지한다.

## 검증

state 재사용·만료·위조, Callback URL 변조, 같은 GitHub ID의 동시 로그인, Refresh 재사용, 동시 갱신, 로그아웃, cookie 속성, cross-workspace 권한 차이를 테스트한다. Provider 연동 실패를 내부 500 원문 노출로 처리하지 않는다.

관련: [User](../user/README.md), [공통 Security](../../shared/security/README.md), [프론트 경계](../../frontend/README.md).
