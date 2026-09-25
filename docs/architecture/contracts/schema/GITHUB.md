# GitHub 연결·PR 테이블 4개

> ID: `DB-GITHUB` · 소유: `data-contracts` · 기준: `2026-09-25`
> 읽는 때: 저장소·설정·PR·동기화 컬럼을 구현할 때

[공통 타입·관계 규칙](README.md)을 적용하며 각 테이블에 공통 id/created_at을 더한다. 업무 정책은 [Repository](../../domain/repository/README.md), [PR](../../domain/pull_request/README.md), [Sync](../../domain/pull_request/SYNC_POLICY.md)가 소유한다.

<a id="table-repository_connections"></a>

## repository_connections

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id | uuid | N | workspaces 논리 참조 |
| github_repository_id / installation_id | bigint | N | 외부 양수 ID |
| owner_login / repository_name | varchar(255) | N | 표시용 최신 이름 |
| is_private | boolean | N | 외부 확인 결과, 기본값 없음 |
| default_branch | varchar(1024) | Y | 외부 정보 없으면 NULL |
| status | varchar(16) | N | ACTIVE/SUSPENDED/DISCONNECTED CHECK |
| connection_generation | integer | N | 1 기본, > 0 |
| current_config_version_id | uuid | N | rule_config_versions 논리 참조 |
| auto_analysis_enabled | boolean | N | false 기본, 현재 자동 분석 동의 |
| ai_mode | varchar(24) | N | OFF 기본, OFF/FINDINGS_ONLY CHECK |
| ai_policy_version | integer | N | 1 기본, > 0 |
| ai_policy_changed_by | uuid | Y | 정책 변경 users 논리 참조 |
| connected_by | uuid | N | 연결한 users 논리 참조 |
| connected_at | timestamptz | N | now(), 현재 세대 시작 |
| disconnected_at | timestamptz | Y | 해제 시각 |
| last_sync_success_at | timestamptz | Y | PR 동기화 최종 성공 |
| updated_at | timestamptz | N | now() |

UQ(workspace_id,github_repository_id). UQ(github_repository_id) WHERE status IN ('ACTIVE','SUSPENDED'). **SUSPENDED도 기존 팀의 배정을 유지**하고 DISCONNECTED에서만 다른 팀 배정을 허용한다. IDX(workspace_id,status,id), IDX(installation_id,status,id), IDX(current_config_version_id). DISCONNECTED일 때만 disconnected_at NOT NULL CHECK.

초기 연결과 설정 v1을 한 트랜잭션에 생성한다(두 UUID를 먼저 생성해 순환 논리 참조를 채움). 같은 Workspace 재연결은 같은 연결 행의 generation을 증가시키고 새 권한 확인·현재 설정을 기록한다. 다른 Workspace 연결은 새 행이며 과거 결과를 옮기지 않는다. Workspace 동시 연결 경쟁은 전역 partial UQ로 처리한다.

현재 정책 컬럼은 매 실행 직전 차단 판단용이다. 설정 버전에도 당시 정책을 snapshot으로 남기며 같은 트랜잭션에 맞춘다. 예전 config의 허용 값으로 현재 철회를 무시하지 않는다. AI 정책 변경은 OWNER만 가능하고 ai_policy_version을 증가시킨다. private key·installation token은 저장하지 않는다.

<a id="table-rule_config_versions"></a>

## rule_config_versions

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / repository_connection_id | uuid | N | 부모 연결과 동일 Workspace |
| version | integer | N | > 0, 연결 내 단조 증가 |
| schema_version | integer | N | 1 기본, JSON 계약 버전 |
| rules / layer_mappings | jsonb | N | 각각 {} 기본, object CHECK |
| ignored_paths | jsonb | N | [] 기본, array CHECK |
| auto_analysis_enabled | boolean | N | false 기본, 당시 정책 snapshot |
| ai_mode | varchar(24) | N | OFF 기본, OFF/FINDINGS_ONLY CHECK |
| config_digest | H256 | N | 정규화된 설정 전체 SHA256 |
| created_by | uuid | N | 변경한 users 논리 참조 |

UQ(repository_connection_id,version). IDX(workspace_id,repository_connection_id,version DESC). 불변 행이라 updated_at 없음. rules는 rule_id별 enabled/severity/threshold allowlist, layer_mappings는 glob→계층 이름, ignored_paths는 glob 문자열 목록이다. 저장 총 크기 64 KiB 이하를 CHECK(pg_column_size(...))로 제한하는 대신 애플리케이션의 정규화 UTF-8 JSON 크기로 검증해 압축/내부 표현과 혼동하지 않는다.

Workspace/연결 잠금 아래 다음 version을 배정하고 새 행 insert와 current_config_version_id 갱신을 함께 수행한다. 최대 version 조회만으로 경쟁을 막지 않는다. config_digest는 감사용이며 같은 내용으로 돌아온 새 version을 막는 UNIQUE가 아니다. config ID·workspace·repository의 일치는 서비스가 검사한다.

<a id="table-pull_requests"></a>

## pull_requests

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / repository_connection_id | uuid | N | 부모 연결 논리 참조 |
| github_pr_id | bigint | N | 외부 양수 PR ID |
| pr_number | integer | N | 저장소 내 양수 번호 |
| title | text | N | 비공개 표시 데이터, PR 본문 아님 |
| author_github_user_id | bigint | Y | 삭제된 작성자 등 알 수 없으면 NULL |
| author_login | varchar(255) | Y | 외부 작성자, 내부 users 관계 아님 |
| state | varchar(16) | N | OPEN/CLOSED CHECK |
| merge_status | varchar(16) | N | UNKNOWN 기본, UNKNOWN/NOT_MERGED/MERGED CHECK |
| is_draft | boolean | N | GitHub 확인 결과 |
| base_ref / head_ref | varchar(1024) | Y | 외부 정보 없으면 NULL |
| base_sha / head_sha | GitSHA | Y | 미확인 snapshot은 분석 접수 불가 |
| changed_files_count / commits_count | integer | Y | 확인된 경우 >= 0 |
| github_created_at / github_updated_at | timestamptz | N | 외부 생성/갱신 시각 |
| closed_at / merged_at | timestamptz | Y | 외부 정보, 상세 응답 누락은 NULL |
| synced_at | timestamptz | N | 마지막 성공 반영 시각 |
| synced_connection_generation | integer | N | >0, 이 metadata를 확인한 연결 세대 |
| updated_at | timestamptz | N | now(), 내부 갱신 시각 |

UQ(repository_connection_id,pr_number), UQ(repository_connection_id,github_pr_id). IDX(workspace_id,repository_connection_id,github_updated_at DESC,id DESC). 제목은 애플리케이션에서 4,096자 이하로 제한하며 임의 URL/HTML로 실행하지 않는다. GitHub 제목이 아닌 PR body/comments/diff는 컬럼으로 두지 않는다.

외부 github_updated_at으로 역순 덮어쓰기를 막는다. 같은 외부 시각의 SHA 충돌은 재조회하며 내부 updated_at과 비교하지 않는다. 재연결 뒤 PR 행은 유지할 수 있지만 현재 연결에서 재취득하고 synced_connection_generation이 현재 generation과 같은 snapshot만 새 분석에 제공한다. merge_status와 closed state의 논리 검증은 외부 필드 누락을 고려해 어댑터에서 수행한다.

<a id="table-pull_request_sync_runs"></a>

## pull_request_sync_runs

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / repository_connection_id | uuid | N | 부모 논리 참조 |
| connection_generation | integer | N | > 0, 접수 당시 세대 |
| actor_type | varchar(16) | N | USER/SYSTEM CHECK |
| requested_by | uuid | Y | USER일 때 users ID, SYSTEM이면 NULL |
| mode | varchar(16) | N | RECENT/PAGE/SINGLE CHECK |
| requested_pr_number | integer | Y | SINGLE일 때만 양수 |
| request_cursor | varchar(1024) | Y | PAGE 요청의 검증된 opaque cursor |
| next_cursor | varchar(1024) | Y | 다음 페이지 식별자, 임의 외부 URL 저장 금지 |
| etag | varchar(512) | Y | 이 요청 범위에 한정된 캐시 검증값 |
| status | varchar(16) | N | PENDING 기본, PENDING/RUNNING/COMPLETED/FAILED/CANCELED CHECK |
| fetched_count | integer | N | 0 기본, >= 0 |
| started_at / finished_at | timestamptz | Y | 실행·terminal 시각 |
| last_success_at | timestamptz | Y | 이 run의 성공 시각 |
| error_code | varchar(64) | Y | 정제된 실패 코드 |
| updated_at | timestamptz | N | now() |

UQ(repository_connection_id) WHERE status IN ('PENDING','RUNNING'). IDX(workspace_id,repository_connection_id,created_at DESC,id DESC), IDX(finished_at) WHERE finished_at IS NOT NULL. actor와 요청 모드별 NULL 조건은 CHECK, terminal 상태와 finished_at 동치 CHECK.

같은 연결의 **같은 모드·대상·cursor·세대** 요청만 기존 활성 run으로 합친다. 다른 범위 요청은 409 SYNC_IN_PROGRESS로 재시도를 안내해 조용히 누락시키지 않는다. run+Job을 같은 transaction에 생성한다. 성공 시 연결의 last_sync_success_at도 함께 갱신하고 실패 시 이전 성공 시각·PR 목록을 유지한다.
