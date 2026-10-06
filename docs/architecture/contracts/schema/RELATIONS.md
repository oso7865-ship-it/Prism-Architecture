# 테이블 설명과 관계 참조 안내

> ID: `DB-RELATIONS` · 소유: `data-contracts` · 기준: `2026-10-06`
> 읽는 때: 테이블의 용도·컬럼 설명 위치·테이블 사이의 참조를 확인할 때

현재 설계는 **20개 업무 테이블**(migration 0011)이다. 이 문서는 읽기 위한 지도이며 컬럼의 타입·NULL·제약은 연결한 상세 명세가 기준이다. 새 관계나 정책을 추가하지 않는다. 압축 전 원문: [legacy](../../../../legacy/pre-compression-2026-10-06/schema/RELATIONS.md).

## 표기

- 모든 테이블의 `id`는 서비스가 발급한 UUID PK, `created_at`은 생성 시각이다([공통 명세](README.md)). `workspace_id`는 어느 팀의 데이터인지 나타내며 user_id와 의미가 다르다.
- `자식.컬럼 → 부모.id`는 **논리 참조**다. 물리 FK는 없고 참조 유효성·같은 팀 여부는 애플리케이션이 검사한다. `1:N`은 부모 하나에 자식 여럿, `선택`은 NULL 허용이다.

## 테이블별 용도

| 테이블 | 한 행의 의미 | 주요 컬럼 |
|---|---|---|
| [users](IDENTITY.md#table-users) | 사용자 한 명 | github_user_id, login, status |
| [login_attempts](IDENTITY.md#table-login_attempts) | 로그인·설치의 일회성 시도 | purpose, state_hash, expires_at/consumed_at |
| [refresh_sessions](IDENTITY.md#table-refresh_sessions) | Refresh 토큰 한 개의 서버 기록 | token_hash, family_id, replaced_by_id |
| [workspaces](IDENTITY.md#table-workspaces) | 팀·개인 작업 공간 | name, created_by, status |
| [workspace_members](IDENTITY.md#table-workspace_members) | 사용자의 팀 가입 관계 | role(OWNER·ADMIN·MEMBER), status |
| [invitations](IDENTITY.md#table-invitations) | GitHub 사용자 초대 | target_github_user_id, token_hash, accepted_by |
| [repository_connections](GITHUB.md#table-repository_connections) | 팀에 연결한 저장소 | github_repository_id, installation_id, connection_generation, current_config_version_id |
| [repository_candidate_sets](GITHUB.md#table-repository_candidate_sets) | 연결 전 후보 저장소의 15분 임시 목록 | workspace_id/user_id, expires_at, items |
| [rule_config_versions](GITHUB.md#table-rule_config_versions) | 분석 설정의 불변 버전 | version, rules, config_digest |
| [pull_requests](GITHUB.md#table-pull_requests) | 연결 저장소의 PR 한 개 | pr_number, base_sha/head_sha |
| [pull_request_sync_runs](GITHUB.md#table-pull_request_sync_runs) | PR 동기화 요청 한 번 | mode, status, cursor |
| [standard_documents](../../domain/standards/README.md) | 팀 컨벤션·구조 문서 한 건 | repository_connection_id, current_version, active |
| [standard_versions](../../domain/standards/README.md) | 팀 문서의 불변 버전 | document_id+version, content, sections, digest |
| [analysis_runs](RESULTS.md#table-analysis_runs) | 고정 commit·규칙·설정의 분석 한 번 | execution_key, config_version_id, status, coverage_status |
| [analysis_file_results](RESULTS.md#table-analysis_file_results) | 분석에서 파일 하나의 처리 결과 | file_path, status, rule_outcomes |
| [findings](RESULTS.md#table-findings) | 정적 분석 발견 항목 | rule_id, severity, confidence, fingerprint |
| [review_runs](RESULTS.md#table-review_runs) | 제한된 문맥의 AI 리뷰 한 번 | analysis_id, purpose, mode, model, result |
| [review_feedback](RESULTS.md#table-review_feedback) | 개인별 지적 처리 상태 | review_id, user_id, issue_key, state |
| [jobs](EXECUTION.md#table-jobs) | 백그라운드 작업 한 개 | kind, aggregate_id, state, lease_generation |
| [webhook_deliveries](EXECUTION.md#table-webhook_deliveries) | 검증 후 접수한 GitHub 이벤트 | delivery_id, body_digest, status |

## 관계

**사용자·팀.** login_attempts.user_id/workspace_id → users/workspaces(설치 흐름만 필수). refresh_sessions.user_id → users.id, replaced_by_id → 자기 참조(선택). workspaces.created_by → users.id(현재 OWNER와 다를 수 있음). workspace_members와 invitations는 workspace_id·user_id·invited_by·accepted_by(선택)로 users·workspaces를 참조한다. users와 workspaces는 workspace_members를 사이에 둔 N:M이며 (workspace_id,user_id)는 한 행, 활성 OWNER는 팀당 한 명이다. family_id는 별도 테이블 FK가 아니다.

**저장소·PR.** repository_connections.workspace_id → workspaces.id, connected_by/ai_policy_changed_by(선택) → users.id, current_config_version_id → 자신의 rule_config_versions.id. rule_config_versions·pull_requests·pull_request_sync_runs는 repository_connection_id로 연결을 참조하고 workspace_id는 연결의 팀과 같아야 한다(sync_runs.requested_by는 USER 요청일 때만 필수). PR 번호는 전역 고유가 아니며 `(repository_connection_id, pr_number)`로 구분한다. repository_candidate_sets는 어떤 테이블도 참조하지 않는 임시 목록이다(workspace_id/user_id 단일 행).

**팀 문서.** standard_documents.workspace_id/repository_connection_id/created_by → workspaces/repository_connections/users. standard_versions.document_id → standard_documents.id. review_runs.standard_versions(JSONB)가 실행에 고정한 버전 UUID 목록을 가지며 FK가 아니다.

**분석·AI.** analysis_runs → repository_connections·pull_requests·rule_config_versions(같은 저장소)·requested_by(USER일 때만). analysis_file_results·findings → analysis_runs.id. Finding에 file_result_id는 없으며 경로·side·분석 ID로 대응한다. review_runs → analysis_runs.id·requested_by. review_feedback → review_runs.id·users.id·workspaces.id(issue_key는 결과의 경로·제목 지문이며 FK가 아니다). 정적 Finding과 AI 설명은 별도 행이므로 AI 실패가 Finding을 지우거나 바꾸지 않는다.

**Job·Webhook.** jobs.workspace_id는 선택(전역 설치 이벤트만 NULL). jobs.aggregate_id는 kind별로 다른 테이블을 가리킨다.

| kind | aggregate_id 대상 |
|---|---|
| SYNC_PULL_REQUESTS | pull_request_sync_runs.id |
| ANALYZE_PR | analysis_runs.id |
| EXPLAIN_FINDINGS | review_runs.id |
| PROCESS_WEBHOOK | webhook_deliveries.id |

같은 `(kind,aggregate_id)`에 Job은 하나이며 재시도는 그 행의 attempts로 남긴다. 완료 Job은 대상 행보다 먼저 보관 기간이 끝날 수 있지만 대기·실행 중 Job은 부모가 있어야 한다. webhook_deliveries는 PR 이벤트에서 workspace_id·repository_connection_id가 필수이고 전역 설치 이벤트는 NULL이다. Delivery에 analysis_id를 저장하는 직접 관계는 없다.

## 외부 ID와 내부 참조 구별

| 값 | 의미 |
|---|---|
| github_user_id 계열 | GitHub 사용자 번호. 우리 users에 가입했다는 뜻이 아님 |
| github_repository_id / installation_id / github_pr_id | GitHub 번호표. 같은 이름의 내부 테이블 참조가 아님 |
| pr_number | 저장소 안의 PR 번호. pull_requests.id와 다름 |
| head_sha / base_sha / source_sha | commit·blob 식별값. commits 테이블 없음 |
| connection_generation / policy_version / version | 세대·버전 비교 값 |
| affected_repository_ids | 설치 이벤트의 GitHub 저장소 번호 목록. 내부 ID 배열이 아님 |

## 조회 흐름과 권한

PR 분석 결과 조회는 사용자 인증 → workspace_members로 소속·권한 확인 → pull_requests 팀·저장소 확인 → analysis_runs 선택 → findings·analysis_file_results → 필요 시 review_runs 순서다. ID를 안다는 것만으로 권한이 생기지 않으며 모든 조회에 workspace_id 조건을 적용한다. 부모 확인·잠금·삭제 순서·고아 데이터 점검은 [공통 스키마의 무결성 규칙](README.md)을 따른다.
