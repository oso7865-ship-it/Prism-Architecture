# 테이블 설명과 관계 참조 안내

> ID: `DB-RELATIONS` · 소유: `data-contracts` · 기준: `2026-09-25`
> 읽는 때: 테이블의 용도·컬럼 설명 위치·테이블 사이의 참조를 확인할 때

현재 설계는 **17개 테이블**이다. 이 문서는 기존 설계를 쉽게 읽기 위한 지도이며, 컬럼의 정확한 타입·NULL·제약은 아래에 연결한 상세 명세가 기준이다. 0007까지 로컬 DB에 적용되었다.

## 먼저 알아둘 표기

- **테이블**은 같은 종류의 기록을 모은 곳, **컬럼**은 각 기록에 저장하는 항목이다. 예를 들어 users의 한 행은 사용자 한 명, login 컬럼은 그 사용자의 GitHub 로그인 이름이다.
- 모든 테이블의 `id`는 우리 서비스가 발급한 UUID 기본키(PK), `created_at`은 행 생성 시각이다. 이 두 컬럼은 [공통 명세](README.md)에 한 번만 정의되어 있다.
- `workspace_id`는 어느 팀 데이터인지 나타낸다. 같은 사용자가 여러 팀에 속할 수 있으므로 user_id와 의미가 다르다.
- `자식.컬럼 → 부모.id`는 논리 참조다. **물리 FK는 없으며**, 참조 ID가 유효한지와 같은 팀인지는 애플리케이션이 검사한다. 물리 FK 없이도 JOIN으로 관계를 조회할 수 있다.
- 아래 `1:N`은 부모 하나에 자식이 여러 개 연결될 수 있다는 뜻이다. 아직 자식이 없는 부모도 가능하다. `선택` 참조는 NULL을 허용한다.
- 명세의 NULL `N`은 필수, `Y`는 비워둘 수 있음이다. `UQ`는 중복 금지, `IDX`는 조회용 인덱스다. `/`로 묶어 쓴 컬럼 이름은 각각 별도 컬럼이다.

## 테이블별 용도와 컬럼 설명

| 테이블·상세 명세 | 한 행이 의미하는 것 | 주요 컬럼의 역할 |
|---|---|---|
| [users](IDENTITY.md#table-users) | 서비스 사용자 한 명 | github_user_id: 외부 계정 식별, login: 표시용 로그인 이름, status: 이용 가능 상태 |
| [login_attempts](IDENTITY.md#table-login_attempts) | 로그인 또는 GitHub 설치의 일회성 시도 | purpose: 목적, state_hash: 요청 검증값 해시, expires_at/consumed_at: 만료·사용 여부 |
| [refresh_sessions](IDENTITY.md#table-refresh_sessions) | 발급한 Refresh 토큰 한 개의 서버 기록 | user_id: 사용자, token_hash: 토큰 해시, family_id: 같은 로그인 세션 계열, replaced_by_id: 교체 후 토큰 기록 |
| [workspaces](IDENTITY.md#table-workspaces) | 팀 또는 개인 작업 공간 하나 | name: 이름, created_by: 최초 생성자, status: 현재 활성 상태 |
| [workspace_members](IDENTITY.md#table-workspace_members) | 사용자 한 명의 특정 팀 가입 관계 | workspace_id/user_id: 소속 관계, role: OWNER·ADMIN·MEMBER, status: 가입·탈퇴·제거 상태 |
| [invitations](IDENTITY.md#table-invitations) | 특정 GitHub 사용자를 팀에 초대한 기록 | target_github_user_id: 초대 대상, invited_by: 초대한 사람, token_hash: 초대 링크 검증, accepted_by: 수락한 사용자 |
| [repository_connections](GITHUB.md#table-repository_connections) | 팀에 연결한 GitHub 저장소 | github_repository_id: 외부 저장소, installation_id: App 설치, connection_generation: 재연결 세대, current_config_version_id: 현재 설정 |
| [rule_config_versions](GITHUB.md#table-rule_config_versions) | 저장소 분석 설정의 특정 버전 | version: 버전 번호, rules/layer_mappings/ignored_paths: 설정, config_digest: 설정 내용 지문 |
| [pull_requests](GITHUB.md#table-pull_requests) | 연결 저장소의 PR 한 개 | pr_number: 저장소 내 PR 번호, base_sha/head_sha: 비교할 commit, github_updated_at: 외부 갱신 시각 |
| [pull_request_sync_runs](GITHUB.md#table-pull_request_sync_runs) | PR 목록·단건 동기화 요청 한 번 | mode: 동기화 범위, status: 실행 상태, cursor: 페이지 식별 정보, fetched_count: 반영 조회 수 |
| [analysis_runs](RESULTS.md#table-analysis_runs) | 고정 commit·규칙·설정으로 접수한 분석 한 번 | execution_key: 중복 실행 식별, config_version_id: 당시 설정, status: 실행 상태, coverage_status: 검사 범위 |
| [analysis_file_results](RESULTS.md#table-analysis_file_results) | 한 분석에서 파일 하나를 처리한 결과 | file_path: 경로, status: 포함·제외·실패, rule_outcomes: 규칙별 평가 여부, finding_limit_reached: 결과 상한 도달 |
| [findings](RESULTS.md#table-findings) | 정적 분석이 발견한 항목 하나 | rule_id: 규칙, severity: 중요도, confidence: 근거 확실성, start_line/end_line: 위치, fingerprint: 분석 내 중복 식별 |
| [review_runs](RESULTS.md#table-review_runs) | 제한된 코드 문맥의 AI 리뷰 요청 한 번 | analysis_id: 대상 분석, model: 모델, result: 검증된 결과, call_attempts: 호출 시도, 토큰 사용량 |
| [jobs](EXECUTION.md#table-jobs) | 백그라운드에서 처리할 작업 하나 | kind: 작업 종류, aggregate_id: 업무 대상, state: 대기·실행·종료, lease_generation: 오래된 실행의 저장 차단 |
| [webhook_deliveries](EXECUTION.md#table-webhook_deliveries) | 검증 후 접수한 GitHub 이벤트 하나 | delivery_id: 전달 식별자, event/action: 사건 종류, body_digest: 본문 지문, status: 처리 상태 |

## 사용자·인증·팀 관계

| 참조하는 컬럼 | 참조 대상 | 관계·설명 |
|---|---|---|
| login_attempts.user_id | users.id | 1:N, 설치 흐름에만 필수; 일반 로그인은 NULL |
| login_attempts.workspace_id | workspaces.id | 1:N, 설치 대상 팀; 일반 로그인은 NULL |
| refresh_sessions.user_id | users.id | 1:N, 사용자에게 여러 세션/교체 토큰이 있을 수 있음 |
| refresh_sessions.replaced_by_id | refresh_sessions.id | 선택 1:1 자기 참조, 이전 토큰 → 다음 토큰 |
| workspaces.created_by | users.id | 1:N, 최초 생성자 기록이며 현재 OWNER와 다를 수 있음 |
| workspace_members.user_id | users.id | 1:N, 사용자 한 명이 여러 팀에 가입 |
| workspace_members.workspace_id | workspaces.id | 1:N, 팀 하나에 여러 멤버 |
| invitations.workspace_id | workspaces.id | 1:N, 초대를 보낸 팀 |
| invitations.invited_by | users.id | 1:N, 초대한 사용자 |
| invitations.accepted_by | users.id | 선택 1:N, 수락 전 NULL |

users와 workspaces는 **workspace_members를 사이에 둔 N:M 관계**다. 같은 (workspace_id,user_id)는 한 행만 존재하며, 활성 OWNER는 팀당 정확히 한 명이다. family_id는 여러 Refresh 행을 묶는 값이고 별도 family 테이블의 FK가 아니다.

## 저장소·PR 관계

| 참조하는 컬럼 | 참조 대상 | 관계·설명 |
|---|---|---|
| repository_connections.workspace_id | workspaces.id | 1:N, 저장소 연결의 소유 팀 |
| repository_connections.connected_by / ai_policy_changed_by | users.id | 각각 연결자/AI 정책 변경자; 정책 변경자는 선택 |
| repository_connections.current_config_version_id | rule_config_versions.id | 현재 설정 하나를 선택; 반드시 자신의 설정 버전 |
| rule_config_versions.repository_connection_id | repository_connections.id | 1:N, 연결 하나의 불변 설정 버전들 |
| rule_config_versions.created_by | users.id | 1:N, 설정을 변경한 사용자 |
| pull_requests.repository_connection_id | repository_connections.id | 1:N, 연결 저장소의 PR들 |
| pull_request_sync_runs.repository_connection_id | repository_connections.id | 1:N, 동기화 이력들 |
| pull_request_sync_runs.requested_by | users.id | 선택 1:N, USER 요청이면 필수, SYSTEM 요청이면 NULL |

rule_config_versions, pull_requests, pull_request_sync_runs의 **workspace_id는 모두 workspaces.id를 참조**하며 repository_connections.workspace_id와 같아야 한다. 설정 이력의 소속과 현재 설정 포인터가 서로를 참조하지만 물리 FK 순환은 없다.

PR 번호는 전역 고유값이 아니다. 예를 들어 저장소 A의 PR #12와 B의 PR #12는 다른 PR이며 `(repository_connection_id, pr_number)`로 중복을 구분한다.

## 분석·AI 관계

| 참조하는 컬럼 | 참조 대상 | 관계·설명 |
|---|---|---|
| analysis_runs.repository_connection_id | repository_connections.id | 1:N, 분석 대상 연결 |
| analysis_runs.pr_id | pull_requests.id | 1:N, PR 하나의 commit·규칙·재분석별 실행들 |
| analysis_runs.config_version_id | rule_config_versions.id | 1:N, 실행 시 고정한 설정; 같은 저장소 소속 |
| analysis_runs.requested_by | users.id | 선택 1:N, USER일 때만 필수 |
| analysis_file_results.analysis_id | analysis_runs.id | 1:N, 분석의 파일별 처리 결과 |
| findings.analysis_id | analysis_runs.id | 1:N, 분석이 발견한 항목들 |
| review_runs.analysis_id | analysis_runs.id | 1:N, 모델·Prompt·정책 버전별 AI 요청들 |
| review_runs.requested_by | users.id | 1:N, AI 요청 사용자 |

이 네 테이블의 **workspace_id는 모두 workspaces.id를 참조**한다. 모든 부모가 같은 팀인지 확인한다. AI 결과는 review_runs.result에 검증된 JSON으로 보관한다.

analysis_file_results와 findings는 둘 다 Analysis의 자식이다. Finding에 file_result_id는 없으며 경로·side와 분석 ID로 파일 맥락을 대응시킨다. 정적 Finding과 AI 설명은 별도 행이므로 AI 실패가 기존 Finding을 삭제하거나 판정을 바꾸지 않는다.

## Job·Webhook 관계

| 참조하는 컬럼·조건 | 참조 대상 | 관계·설명 |
|---|---|---|
| jobs.workspace_id | workspaces.id | 선택 1:N; 전역 설치 이벤트 처리만 NULL |
| jobs.aggregate_id, kind=SYNC_PULL_REQUESTS | pull_request_sync_runs.id | 해당 동기화의 Job 하나 |
| jobs.aggregate_id, kind=ANALYZE_PR | analysis_runs.id | 해당 분석의 Job 하나 |
| jobs.aggregate_id, kind=EXPLAIN_FINDINGS | review_runs.id | 해당 AI 요청의 Job 하나 |
| jobs.aggregate_id, kind=PROCESS_WEBHOOK | webhook_deliveries.id | 해당 Delivery의 Job 하나 |
| webhook_deliveries.workspace_id | workspaces.id | PR 이벤트에서는 필수, 전역 설치 이벤트는 NULL |
| webhook_deliveries.repository_connection_id | repository_connections.id | 1:N, PR 이벤트의 수신 당시 연결; 전역 설치 이벤트는 NULL |

Job은 kind에 따라 다른 테이블을 참조한다. 같은 `(kind,aggregate_id)`에 Job 하나만 두고 재시도는 그 행의 attempts/history로 남긴다. 완료 Job은 보관 기간 차이로 대상 업무 행이 먼저 지워질 수 있지만, 대기·실행 중 Job은 부모가 존재해야 한다.

GitHub 이벤트 하나에서 PR 갱신과 분석 접수가 이어질 수 있다. 그 업무 흐름은 서비스가 연결하며 Delivery에 analysis_id를 저장하는 직접 관계는 없다.

## 외부 ID와 내부 참조를 구별하기

| 값 | 의미 |
|---|---|
| github_user_id / target_github_user_id / author_github_user_id | GitHub 사용자 번호. 초대 대상·PR 작성자가 우리 users에 반드시 가입되어 있는 것은 아님 |
| github_repository_id / installation_id / github_pr_id | GitHub 저장소·App 설치·PR 번호표. 동일 이름의 내부 테이블 참조가 아님 |
| pr_number | 특정 저장소 안의 PR 번호. pull_requests.id와 다름 |
| head_sha / base_sha / source_sha | commit 또는 blob 식별값. 별도 commits 테이블 참조가 아님 |
| connection_generation / policy_version / version | 세대·버전 비교 값. ID 참조 컬럼과 함께 의미를 해석 |
| affected_repository_ids | 설치 이벤트에 포함된 GitHub 저장소 번호 목록. 내부 repository_connections.id 배열이 아님 |

## 관계를 따라 읽는 예

사용자가 팀의 PR 분석 결과를 보는 경우: 사용자 인증 → workspace_members에서 소속/권한 확인 → pull_requests에서 팀·저장소 확인 → analysis_runs 선택 → findings와 analysis_file_results 조회 → 필요하면 review_runs 결과 조회.

예를 들어 `findings.analysis_id=A`이면 analysis_runs.id=A의 결과다. 그러나 A라는 ID를 안다는 것만으로 조회 권한이 생기지 않는다. API는 현재 사용자에게 해당 Workspace 접근 권한이 있는지 확인하고, 조회에도 workspace_id 조건을 함께 적용한다.

부모 확인·잠금·삭제 순서·고아 데이터 점검의 실행 기준은 [공통 스키마의 무결성 규칙](README.md)을 따른다. 이 안내는 기존 설계의 설명이며 새로운 관계나 정책을 추가하지 않는다.

## 개인 리뷰 처리 기록 (0007)

review_feedback은 개인별 판단을 저장하며 총 업무 테이블 수는 17개다. workspace_id → workspaces.id, review_id → review_runs.id, user_id → users.id는 논리 참조다. issue_key는 해당 리뷰 결과의 경로·제목 지문이며 독립 FK가 아니다. 한 사용자/회차/지적당 한 기록이다. [전체 컬럼](RESULTS.md#table-review_feedback)을 따른다.
