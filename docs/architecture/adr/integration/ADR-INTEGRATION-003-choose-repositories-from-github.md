# ADR-INTEGRATION-003: GitHub에서 허용한 저장소 목록에서 골라 연결

> ID: `ADR-INTEGRATION-003` · 소유: `INTEGRATION` · 기준: `2026-10-06`
> 읽는 때: 저장소 연결 시작·콜백·선택 연결 구현을 변경할 때

- 상태: `ACCEPTED`
- 근거: 사용자가 2026-10-06 채팅에서 연결 방식을 owner/name 직접 입력에서 "버튼으로 GitHub가 허용한 저장소를 모두 가져와 원하는 것만 연결"로 바꾸도록 요청하고, 가져오기 방식(목록만 불러와 체크한 것만 연결)·권한 기준(admin 유지)·기존 입력 방식(완전 교체)을 선택했다.
- 대체하는 ADR: [ADR-INTEGRATION-002](ADR-INTEGRATION-002-verified-app-connection.md)의 **연결 시작·검증 절차**. 002의 PR 단계별 조회, 권한 범위, 기존 리뷰 처리, sync cursor 계약은 그대로 유지한다.
- 대체한 ADR: 없음.

## 배경

연결 방식은 사용자가 GitHub 앱을 설치한 뒤 `owner/repository`를 직접 입력하는 두 단계였다. 이름을 잘못 입력하기 쉽고, 앱이 이미 허용받은 저장소를 사용자가 다시 적어야 했다.

## 결정

1. `POST /workspaces/{w}/repositories/connect`는 본문이 없다. 팀 `manage` 권한을 확인하고 일회성 `GITHUB_INSTALL` state(10분, 브라우저 PKCE 바인딩)를 만들어 GitHub 인증 URL을 돌려준다. 사용자가 입력한 문자열은 state에 들어가지 않는다.
2. 콜백은 사용자 토큰을 교환해(저장하지 않음) `/user`의 숫자 ID가 요청자와 같은지 확인한 뒤 `GET /user/installations`로 사용자의 앱 설치를 가져온다. `app_id`가 우리 앱이 아니거나 정지됐거나 contents·pull_requests·issues 권한이 부족한 설치는 건너뛰고 개수만 기록한다. 설치마다 `/user/installations/{id}/repositories`로 저장소와 `permissions.admin`을 읽는다. 설치 20개·저장소 300개·설치당 3페이지가 상한이고 초과하면 `truncated`로 표시한다. 한 항목의 형식이 이상해도 나머지는 살린다.
3. 결과는 `repository_candidate_sets`에 (팀, 사용자)당 1건으로 15분만 보관한다. 새 콜백은 이전 목록을 교체하고 만료분은 저장·조회 시 삭제한다. 사용자·설치 토큰은 저장하지 않는다. 콜백은 아무것도 연결하지 않고 `/?repository_result=choose&team={w}`로 돌려보낸다.
4. `GET /workspaces/{w}/repositories/candidates`는 호출자 본인의 목록만 `AVAILABLE`/`CONNECTED`/`ADMIN_REQUIRED`/`OTHER_TEAM` 상태와 함께 돌려준다. 목록이 없거나 만료되면 404 `CANDIDATES_NOT_FOUND`다.
5. `POST /workspaces/{w}/repositories/connect-selected`는 `github_repository_ids`(1~20개, 중복·추가 필드 금지)를 받는다. ID는 저장된 목록에 있어야 하고, **저장된 admin 값**으로 다시 판단하며(요청 본문은 신뢰하지 않음), 저장소마다 별도 트랜잭션으로 기존 연결 규칙(설정 v1, 첫 sync 접수)을 적용한다. 결과는 저장소별 `CONNECTED`/`ALREADY_CONNECTED`/`ADMIN_REQUIRED`/`NOT_IN_LIST`/`CONFLICT`/`FAILED`이며 한 건의 실패가 다른 건을 막지 않는다.
6. 체크하지 않은 저장소에는 연결 행도 sync 작업도 만들지 않는다. admin 권한이 있는 저장소만 연결할 수 있다는 002의 기준은 유지한다.
7. 직접 입력 연결 경로와 `ConnectRequest`는 제거한다.

## 대안

- 허용된 저장소를 모두 연결하고 화면에서만 숨기기: 모든 저장소의 PR이 서버에 저장되고 호출량·노출 범위가 커져 채택하지 않았다.
- 사용자 토큰을 장기 저장해 선택을 이어가기: 002에서 이미 배제한 방식이다. 15분 목록으로 대체했다.
- 선택을 콜백 직후 서버 보관 없이 URL로 전달하기: 비공개 저장소 이름이 URL·기록에 남아 제외했다.

## 영향과 한계

- 목록에는 비공개 저장소 이름이 포함되지만 요청 사용자·팀 한 쌍에게만 보이고 15분 뒤 삭제된다.
- 목록 시점의 admin 값을 연결 시점에 다시 확인하지 않는다(최대 15분 지연). 이후 권한 변경은 기존처럼 sync 실패(SUSPENDED)로 반영된다.
- 허용 저장소를 바꾸려면 GitHub 설정에서 바꾼 뒤 다시 가져와야 한다.
- 실제 GitHub의 응답 형태는 공식 문서 기준으로 설계했고 모의 응답으로 검증했다. 실제 App 설치·콜백 확인은 별도다.
- 신규 테이블은 migration 0011 파일로만 작성했고 운영 DB에는 적용하지 않았다.

## 소유 문서와 검증

[Repository](../../domain/repository/README.md), [HTTP API](../../contracts/HTTP_API.md), [GitHub·PR 스키마](../../contracts/schema/GITHUB.md), [반출/보관](../../operations/SECURITY_PRIVACY.md), [화면](../../frontend/README.md)이 현재 계약을 소유한다. 백엔드는 실제 PostgreSQL과 MockTransport로 설치 필터·상한·중복·타인 토큰·만료·부분 성공·다른 팀 충돌·권한을 검증하고, 프론트엔드는 응답 검증과 화면 상태를 검증한다. 로컬 서버·브라우저(GitHub는 모의 응답)에서 목록 표시, 검색, 선택 연결, 만료 안내, 모바일 폭을 확인했다.

GitHub 공식 근거: [사용자 설치 목록](https://docs.github.com/en/rest/apps/installations#list-app-installations-accessible-to-the-user-access-token), [설치 저장소 목록](https://docs.github.com/en/rest/apps/installations#list-repositories-accessible-to-the-user-access-token).
