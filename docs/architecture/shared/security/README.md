# Security: 중립 기술 기반

> ID: `SECURITY` · 소유: `backend/app/shared/security` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: token codec·비밀 값 처리 기술을 변경할 때

```text
shared/security/
├─ token_codec.py    JWT 서명/검증
├─ hashing.py        난수 token hash·constant-time 비교
└─ secrets.py        비밀 값 래핑·마스킹 보조
```

`WorkspaceRole`, `require_owner`, 멤버십 조회는 workspace 도메인 소유다. 로그인 lifecycle은 auth, GitHub HMAC protocol은 webhook 소유다. security라는 이름으로 모든 인가 정책을 끌어오지 않는다.

JWT decoder는 허용 알고리즘을 고정하고 issuer/audience/expiry를 확인한다. body의 user_id를 인증된 주체로 사용하지 않는다. 난수 Refresh/초대 token은 충분한 엔트로피로 생성하고 hash만 저장한다. 비밀번호 회원가입은 없으므로 불필요한 password.py는 만들지 않는다.

서버 Secret은 로그·API 응답·AI 입력·job payload에 넣지 않는다. 사용자 저장소 URL에서 임의 host를 fetch하지 않는다. TLS 검증 비활성화·모든 Origin 허용·개발용 auth bypass를 운영에서 허용하지 않는다.

CORS는 인증/인가의 대체가 아니다. 브라우저 외 클라이언트도 모든 API 권한 검사를 받는다. Webhook은 사용자 JWT 대신 자체 서명을 쓰는 별도 수신 경계다.

검증 기준은 변조/만료/알고리즘 오염 token, secret repr, 잘못된 origin, 권한 없는 직접 API 호출이다. 로그/외부 반출 정책은 [보안·보관](../../operations/SECURITY_PRIVACY.md)이 소유한다.
