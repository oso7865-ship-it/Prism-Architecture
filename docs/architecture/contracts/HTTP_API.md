# HTTP API 경계와 초기 경로

> ID: `HTTP-API` · 소유: `http-contracts` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: endpoint·직렬화·오류 응답의 외부 계약을 변경할 때

이 문서는 endpoint 지도다. 필드의 업무 의미·상태는 각 도메인이 소유한다. 구현 시 Pydantic/OpenAPI 스키마를 생성하고 이 지도와 동기화한다. 현재는 실행 중인 API 명세가 아니다.

## 공통

Base path는 `/api/v1`. JSON은 snake_case, ID는 문자열 UUID, 시각은 UTC ISO 8601로 통일한다. GitHub 숫자 ID와 내부 UUID를 혼동하지 않는다. 목록은 cursor 기반 `items/next_cursor`, 최대 size는 [Database](../shared/database/README.md)를 따른다.

401은 비인증, 403은 소속팀에서 권한 부족, 404는 존재하지 않거나 다른 Workspace의 리소스, 409는 중복/상태 충돌, 422는 입력 형식 오류, 429는 접수량 제한이다. 응답 형식은 [공통 Exception](../shared/exception/README.md)이 소유한다.

| Method / Path | 책임 | 성공 |
|---|---|---|
| GET /auth/github/start | auth, state 생성 후 이동 | 302 |
| GET /auth/github/callback | auth, 로그인 완료 | 302 |
| POST /auth/refresh | auth, rotation | 200 |
| POST /auth/logout | auth, 세션 철회 | 204 |
| GET /users/me | user | 200 |
| POST /workspaces | workspace | 201 |
| GET /workspaces | 내 멤버십에 속한 팀만 | 200 |
| GET /workspaces/{w}/members | workspace | 200 |
| POST /workspaces/{w}/invitations | workspace | 201 |
| GET /workspaces/{w}/invitations | 대기 초대 목록(토큰 미포함) | 200 |
| DELETE /workspaces/{w}/invitations/{i} | 초대 철회 | 204 |
| DELETE /workspaces/{w}/members/{u} | 멤버 제거 또는 본인 탈퇴 | 204 |
| POST /invitations/accept | 대상 ID 확인·일회성 소비 | 200 |
| PATCH /workspaces/{w}/members/{u} | workspace, 역할 변경 | 200 |
| POST /workspaces/{w}/transfer-ownership | workspace | 200 |
| GET /github-app | App 설정 상태·설치 링크 | 200 |
| POST /workspaces/{w}/repositories/connect | 인증된 팀 관리자 연결 시작, state/PKCE 쿠키·GitHub 인증 URL | 200 |
| GET /github-app/callback | 검증 후 연결 + 최초 sync 원자적 접수, SPA 복귀 | 302 |
| GET /workspaces/{w}/repositories | repository | 200 |
| PATCH /workspaces/{w}/repositories/{r}/settings | 설정 새 버전 | 200 |
| DELETE /workspaces/{w}/repositories/{r} | 논리적 연결 해제 | 204 |
| POST /workspaces/{w}/repositories/{r}/syncs | PR sync Job | 202 |
| GET /workspaces/{w}/repositories/{r}/syncs/{s} | sync 상태 | 200 |
| GET /workspaces/{w}/repositories/{r}/pull-requests | PR 목록 | 200 |
| GET /workspaces/{w}/pull-requests/{p} | PR 상세 | 200 |
| GET /workspaces/{w}/pull-requests/{p}/github-reviews | 기존 리뷰 on-demand | 200 |
| POST /workspaces/{w}/analyses | analysis Job | 202 |
| GET /workspaces/{w}/analyses/{a} | 상태·coverage | 200 |
| GET /workspaces/{w}/analyses/{a}/findings | 정적 Finding (중요도/ID cursor, 100개) | 200 |
| GET /workspaces/{w}/analyses/{a}/files | 파일별 상태·규칙 평가 (cursor, 100개) | 200 |
| GET /workspaces/{w}/pull-requests/{p}/analyses | 최근 분석 50개·활성 규칙·runner 상태 | 200 |
| POST /workspaces/{w}/analyses/{a}/cancel | 취소 요청 | 202 |
| POST /workspaces/{w}/analyses/{a}/reviews | 별도 AI Job | 202 |
| GET /workspaces/{w}/reviews/{review_id} | AI 실행/결과 | 200 |

Webhook은 API prefix 밖 `POST /webhooks/github`. health는 `/health/live`, `/health/ready`. 이 두 경계를 사용자 API의 JWT 처리와 섞지 않는다.

## 분석 접수 예시

```json
{"pr_id":"<internal-pr-uuid>","expected_head_sha":"<full-commit-sha>"}
```

```json
{"analysis_id":"<uuid>","status":"PENDING","status_url":"/api/v1/workspaces/<w>/analyses/<a>"}
```

요청 본문의 user_id는 받지 않는다. w/p/a가 서로 같은 테넌트 관계인지 검증한다. source code를 업로드하는 public endpoint는 MVP에 없다.

중복 실행 키는 같은 분석을 반환한다. 명시적 재분석은 `rerun_of` 같은 별도 검증 필드로 구분하고 generation을 서버에서 증가시킨다. 단순한 네트워크 재시도가 새 과금/분석을 생성하지 않도록 한다.

## 공개 계약과 승인

API response_model은 반환 필드를 allowlist로 제한한다. ORM 전체를 자동 직렬화하지 않는다. private 응답에는 no-store를 적용한다. 기능별 permission 상세는 [Workspace](../domain/workspace/README.md)를 따른다. DELETE Workspace·회원 탈퇴·자동 GitHub 댓글은 이 초기 API 표에 포함하지 않는다.

현재 구현의 연결·PR 리뷰 응답 범위는 [ADR-INTEGRATION-002](../adr/integration/ADR-INTEGRATION-002-verified-app-connection.md)를 따른다. 설정 PATCH·AI 리뷰 경로는 후속 구현이다. 분석과 Webhook은 현재 working-tree에서 구현했으며 검증 범위는 IMPLEMENTATION을 따른다. Sync POST는 page(기본1) 또는 pr_number를 받고, 외부 리뷰 GET은 kind(reviews/comments/review_comments/commits)와 page를 받는다.
