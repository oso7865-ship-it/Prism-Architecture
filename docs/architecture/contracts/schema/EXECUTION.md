# 실행·웹훅 테이블 2개

> ID: `DB-EXECUTION` · 소유: `data-contracts` · 기준: `2026-09-25`
> 읽는 때: 영속 Job·Webhook 수신 컬럼·인덱스를 구현할 때

[공통 타입·관계 규칙](README.md)을 적용하며 공통 id/created_at을 더한다. 업무 의미와 재시도 정책은 [Jobs](../../shared/jobs/README.md), [Webhook](../../domain/webhook/README.md)가 소유한다.

<a id="table-jobs"></a>

## jobs

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id | uuid | Y | 업무 Job에는 필수, 전역 설치 이벤트 처리만 NULL |
| kind | varchar(32) | N | SYNC_PULL_REQUESTS/ANALYZE_PR/EXPLAIN_FINDINGS/PROCESS_WEBHOOK CHECK |
| aggregate_id | uuid | N | 종류별 SyncRun/AnalysisRun/ReviewRun/Delivery ID |
| dedupe_key | H256 | N | kind+대상 ID+Workspace(또는 전역 표식) 정규화 SHA256 |
| state | varchar(16) | N | READY 기본, READY/LEASED/SUCCEEDED/DEAD/CANCELED CHECK |
| attempts | integer | N | 0 기본, >=0 |
| max_attempts | integer | N | >0, enqueue 시 업무 정책 제공 |
| available_at | timestamptz | N | now(), 다음 claim 가능 시각 |
| lease_until | timestamptz | Y | 유효 lease 만료 |
| lease_generation | bigint | N | 0 기본, >=0, claim마다 증가 |
| claimed_by | varchar(128) | Y | worker 인스턴스 ID, 비밀 자격증명 아님 |
| completed_at | timestamptz | Y | 성공·실패 소진·취소의 terminal 시각 |
| error_code | varchar(64) | Y | 마지막 정제된 실패 코드 |
| attempt_history | jsonb | N | [] 기본, array CHECK |
| updated_at | timestamptz | N | now() |

UQ(dedupe_key), UQ(kind,aggregate_id). IDX(available_at,id) WHERE state='READY', IDX(lease_until,id) WHERE state='LEASED', IDX(workspace_id,state,created_at,id), IDX(completed_at) WHERE completed_at IS NOT NULL.

CHECK attempts<=max_attempts. LEASED일 때만 lease_until/claimed_by 둘 다 NOT NULL, terminal일 때만 completed_at NOT NULL. workspace_id IS NULL이면 kind='PROCESS_WEBHOOK'인 CHECK와, 해당 Delivery가 전역 설치 이벤트라는 서비스 검증을 모두 적용한다. 다른 팀의 aggregate를 Job에 붙이지 못하도록 소유 공개 계약에서 확인한다.

범용 payload는 MVP에 두지 않는다. 필요한 식별자·버전은 대상 업무 행에서 읽는다. attempt_history는 {attempt,generation,started_at,finished_at,outcome,error_code}만 저장하는 제한 배열이다. outcome은 SUCCEEDED/RETRY/LEASE_EXPIRED/FAILED/CANCELED; 미종료 attempt는 finished_at/outcome=NULL. 최대 max_attempts개이며 직렬화 16 KiB 이하, raw 예외·source·token 금지. 현재 시도 시작 및 종료를 fence 조건부 UPDATE에 포함한다.

claim은 attempts와 generation을 함께 증가시키고 commit한다. 뒤따르는 짧은 업무 시작 transaction에서 권한·세대·Job fence 확인 후 domain RUNNING을 기록한다. 그 사이 프로세스가 죽으면 domain은 PENDING일 수 있으며, API는 실행 확정을 과장하지 않는다. reclaim/최종 저장은 domain 상태와 Job 상태를 원자적으로 맞춘다. 이전 generation의 history 덮어쓰기도 금지한다.

<a id="table-webhook_deliveries"></a>

## webhook_deliveries

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| provider | varchar(16) | N | GITHUB CHECK |
| delivery_id | varchar(128) | N | 공급자 전달 ID |
| event | varchar(64) | N | 구독한 event allowlist |
| action | varchar(64) | Y | 해당 event에 action이 없을 경우 NULL |
| installation_id | bigint | N | 외부 양수 ID |
| github_repository_id | bigint | Y | PR/단일 저장소 이벤트의 외부 ID |
| pr_number | integer | Y | PR 이벤트의 양수 번호 |
| workspace_id / repository_connection_id | uuid | Y | 수신 시 매핑한 PR 이벤트 논리 참조 |
| connection_generation | integer | Y | 매핑된 연결 세대, >0 |
| affected_repository_ids | jsonb | N | [] 기본, 설치 권한 변경의 외부 숫자 ID 배열 |
| body_digest | H256 | N | 검증한 원문 body SHA256, 원문 아님 |
| status | varchar(16) | N | PENDING 기본, PENDING/PROCESSING/PROCESSED/FAILED/CANCELED/IGNORED CHECK |
| received_at | timestamptz | N | now() |
| processed_at | timestamptz | Y | terminal 시각 |
| error_code | varchar(64) | Y | 공개 실패 코드 |
| updated_at | timestamptz | N | now() |

UQ(provider,delivery_id). IDX(workspace_id,received_at DESC,id DESC), IDX(installation_id,received_at DESC,id DESC), IDX(processed_at) WHERE processed_at IS NOT NULL.

CHECK workspace/연결/generation 세 필드 모두 NULL 또는 모두 NOT NULL. PR 이벤트는 매핑 세 필드와 github_repository_id/pr_number를 모두 요구하며 service validation으로 허용 event/action 조합을 검사한다. 설치 전체 이벤트는 세 필드 NULL이며 설치 ID에서 연결을 찾는다. affected_repository_ids는 array·양수 정수·중복 없음·최대 10,000개·직렬화 256 KiB 이하로 검증한다. 상한 초과는 저장 성공으로 위장하지 않고 재동기화 대상으로 기록한다. 원문 payload는 보존하지 않는다.

PROCESSED/FAILED/CANCELED/IGNORED일 때만 processed_at NOT NULL CHECK. 설치 권한 제거 이벤트는 affected ID를 등록된 연결과 비교해 Workspace별 잠금·차단을 적용한다. 이미 적용한 팀에 재시도해도 결과가 같도록 한다. 새 설치/재연결의 현재 권한을 과거 이벤트만으로 복원하지 않고 검증한다.

PR 이벤트는 수신 당시의 연결 ID/세대를 고정하므로 대기 중 재연결되어도 새 세대 작업으로 잘못 전달하지 않는다. 중복 delivery의 body_digest가 다르면 기존 수신 기록을 변경하지 않고 불일치를 진단한다. HMAC 검증 실패/미지원 이벤트에는 업무 Delivery·Job을 만들지 않는다.
