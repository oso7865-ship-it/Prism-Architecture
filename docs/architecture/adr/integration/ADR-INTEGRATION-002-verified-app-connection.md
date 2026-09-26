# ADR-INTEGRATION-002: 검증된 GitHub App 연결과 단계별 PR 조회

> ID: `ADR-INTEGRATION-002` · 소유: `INTEGRATION` · 기준: `2026-09-26`
> 읽는 때: GitHub App 연결·콜백·PR 조회 구현을 변경할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-26`
- 근거: 사용자 팀·저장소 연결 묶음 구현 위임과 기존 테넌트/설치 검증 계약
- 대체하는 ADR: 없음
- 대체한 ADR: 없음

## 배경
로그인 OAuth App과 GitHub App 설치 권한은 다르다. installation_id 또는 공개 저장소 조회 성공만으로 팀 연결을 승인할 수 없다. 실제 키 등록 전에도 거부 경계와 작업 복구를 검증해야 한다.

## 결정
GitHub App 설치 화면은 별도 링크로 열고 허용 저장소를 선택한다. 팀 OWNER/ADMIN이 owner/repository를 입력해 연결 시작 API를 호출한다. auth의 GITHUB_INSTALL state는 사용자·팀·대상 이름·브라우저 PKCE verifier에 묶고 DB에는 hash만 보존한다. 일회성 소비를 commit한 뒤 App user OAuth 토큰을 교환한다.
서버가 /user 숫자 ID 일치, 사용자 저장소 admin 권한, App JWT로 확인한 저장소 설치와 app_id·suspension·필요 권한, 사용자 설치의 허용 저장소 목록을 모두 검사한다. 사용자 토큰·installation token·private key는 DB에 저장하지 않는다. 연결 저장 전에 팀 권한을 다시 확인한다.
연결 성공은 저장소·설정 v1·SyncRun·Job을 한 트랜잭션에 저장한 뒤 SPA로 복귀한다. 생성형 API 대신 POST /workspaces/{w}/repositories/connect → GET /github-app/callback의 브라우저 인증 흐름을 구체화한다. 첫 sync는 최신 갱신 PR 30개이며 분석을 접수하지 않는다.
현재 단계의 기존 리뷰는 작성자·리뷰 상태·커밋 식별자와 GitHub 링크를 제공한다. 원문 코멘트·commit message·diff_hunk는 전송/저장하지 않고 GitHub에서 보도록 안내한다. 원문 안전 렌더링·선별 마스킹 기능은 별도 확장으로 남긴다.
PR sync HTTP 입력 page는 1~10,000의 검증된 정수다. DB request_cursor/next_cursor에는 정규 십진수 문자열만 기록한다. URL cursor는 허용하지 않는다. 내부 목록은 팀/저장소 스코프의 UUID anchor cursor를 사용한다.

## 대안
installation_id만 제출하는 방식은 사용자 권한 증명이 없어 제외했다. 사용자 토큰을 장기 저장해 저장소 선택을 이어가는 방식 대신 일회성 callback 안에서 검증해 저장·암호화·갱신 운영을 피했다. 코멘트 원문은 불완전한 비밀 탐지로 노출하기보다 현재 단계에서 GitHub 링크로 연결한다.

## 영향과 한계
연결자는 GitHub 저장소 관리자여야 한다. App 설치 승인 대기/권한 부족은 연결 실패로 안내한다. 초기 기능은 자동 분석과 AI를 OFF로 유지한다. App 등록 전 실제 연결 완료를 주장하지 않는다. Webhook 설치 제거 이벤트는 후속 묶음이며 현재 sync 실패 시 SUSPENDED로 차단한다. 공개 운영 전 설치 철회 자동 반영을 검증해야 한다.

## 소유 문서와 검증
- [Repository](../../domain/repository/README.md)
- [PR](../../domain/pull_request/README.md)
- [Sync](../../domain/pull_request/SYNC_POLICY.md)
- [HTTP API](../../contracts/HTTP_API.md)
백엔드 test_workspace.py/test_repository_sync.py에서 실제 PostgreSQL과 MockTransport로 검증한다. 실제 App 설치·콜백은 사용자 등록 후 별도 확인한다.

GitHub 공식 근거: [App 사용자 토큰](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app), [App REST API](https://docs.github.com/en/rest/apps/apps).
