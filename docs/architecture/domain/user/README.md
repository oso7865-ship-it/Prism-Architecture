# User: 서비스 사용자

> ID: `USER` · 소유: `backend/app/domain/user` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 사용자 식별·프로필·활성 상태를 변경할 때

## 책임

GitHub 숫자 ID와 우리 서비스 user_id를 연결하고 최소 프로필·활성 상태를 소유한다. WorkspaceRole, OAuth state, Refresh Token, GitHub App installation은 다른 소유자의 데이터다.

```text
user/
├─ api.py          UserLookup·UserSnapshot·활성 상태 조회
├─ router.py       내 프로필 조회
├─ service.py      프로필 반영·사용자 생성
├─ repository.py   DB 접근
├─ models.py       User
├─ dto.py
├─ exceptions.py
└─ schema/response.py
```

`User(id, github_user_id, login, display_name, avatar_url, status, created_at, updated_at)`를 기본 모델로 한다. `github_user_id`에 UNIQUE 제약을 둔다. 동시 첫 로그인 시 select-then-insert만 믿지 않고 DB 충돌을 처리한다. GitHub login 변경 시 새로운 계정을 만들지 않는다.

외부에는 필요한 프로필만 반환한다. 이메일은 필수로 수집하지 않는다. URL·이름은 신뢰하지 않는 표시 데이터다. 임의 avatar URL을 서버가 대신 가져오는 프록시를 만들지 않는다.

공개 계약은 `get_active_user(user_id)`와 `upsert_github_identity(identity)`다. ORM 객체를 다른 도메인에 반환하지 않는다. `CurrentPrincipal` 구성은 auth의 책임이다.

## 제외와 테스트

비밀번호 변경·이메일 인증·계정 자동 병합은 제외한다. 데이터 파괴가 수반되는 회원 탈퇴는 보관/Workspace 소유권 정책을 정한 후 구현한다. MVP에서 버튼만 제공하거나 OWNER 탈퇴로 팀을 고아 상태로 만들지 않는다.

유일키 경쟁, login 변경, 비활성 계정 차단, 다른 사용자 프로필 접근, 반환 필드의 비밀정보 누출 여부를 검증한다.

물리 컬럼·제약·인덱스와 논리 참조 검증은 [스키마 계약](../../contracts/schema/IDENTITY.md)을 따른다. 물리 FK는 생성하지 않는다.
