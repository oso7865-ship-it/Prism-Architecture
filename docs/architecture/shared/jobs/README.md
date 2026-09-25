# Jobs: PostgreSQL 영속 큐와 복구

> ID: `JOBS` · 소유: `backend/app/shared/jobs` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 비동기 실행·재시도·lease·복구를 변경할 때

## 왜 Shared인가

분석·PR 동기화·Webhook 처리·AI 설명 모두 쓰는 기술 실행 기반이다. **작업 종류의 업무 의미는 각 domain이 소유**한다. Runner는 handler registry를 주입받고 analysis/pull_request/review를 import하지 않는다.

```text
shared/jobs/
├─ contracts.py      JobEnvelope·JobHandler protocol·Claim
├─ models.py         Job ORM
├─ store.py          enqueue/claim/lease/fence 조건부 갱신
├─ runner.py         실행 loop
├─ retry.py          중립 backoff 계산
└─ registry.py       주입받은 handler lookup
```

## 영속 접수

Job에는 `id, workspace_id, kind, aggregate_id, dedupe_key, state, attempts, max_attempts, available_at, lease_until, lease_generation, claimed_by, created_at, completed_at, error_code`를 둔다. payload가 필요하면 검증된 식별자·설정 버전만 포함한다. token/source/ORM 객체/Session을 저장하지 않는다.

MVP 물리 모델은 범용 payload 없이 aggregate에서 입력을 조회한다. 제한된 attempt_history와 claim 인덱스·상태 CHECK는 [실행 스키마](../../contracts/schema/EXECUTION.md)를 따른다. 전역 설치 이벤트 처리만 workspace_id NULL을 허용하고, 실제 업무 변경은 등록된 연결에서 팀을 찾아 검증한다.

업무 레코드와 Job을 같은 PostgreSQL transaction에서 생성하고 commit 후 접수를 응답한다. 현재 구조에는 외부 Redis/Kafka가 없으므로 DB와 broker 이중 기록을 만들지 않는다.

## Claim·lease·fencing

Worker는 READY이고 실행 시각이 지난 Job을 `SELECT ... FOR UPDATE SKIP LOCKED`로 하나 claim한 뒤 lease 정보를 기록하고 즉시 commit한다. SKIP LOCKED는 queue 소비 같은 용도에 사용할 수 있으며 일반적인 일관된 조회를 대신하지 않는다. [S-PG-QUEUE](../../reference/SOURCES.md#s-pg-queue)

MVP 기본값: 전체 동시 Job 1개, claim loop 2초, lease 60초, heartbeat 15초. 하나의 embedded runner만 실행한다. 분석 CPU 작업은 subprocess에 두어 heartbeat와 HTTP loop를 막지 않는다. SQLAlchemy Session은 단계마다 새로 만든다.

claim마다 lease_generation을 증가시킨다. 결과 저장 시 job_id + 현재 generation + lease 소유/만료 조건을 다시 확인한다. 만료된 이전 worker가 돌아와도 결과를 덮어쓰지 못한다. 이 확인과 domain 결과 저장·Job 완료 표시를 같은 DB transaction에서 처리한다.

claim transaction은 Job만 잠그고 종료한다. domain RUNNING 전환은 다음 짧은 transaction에서 Workspace→업무 행→Job 순서로 재검증한다. 이 사이의 PENDING/LEASED 조합은 복구 가능한 시작 구간이다. 결과 저장·reclaim·cleanup은 [공통 무결성 프로토콜](../../contracts/schema/README.md)을 따른다. Job 잠금을 유지한 채 반대 순서로 Workspace를 잠그지 않는다.

## 상태와 재시도

Job state는 `READY / LEASED / SUCCEEDED / DEAD / CANCELED`. 업무 상태는 domain이 따로 유지한다. 예를 들어 Analysis PENDING↔Job READY, RUNNING↔LEASED지만 모든 Job을 AnalysisStatus로 표현하지 않는다.

분석/PR/Webhook 작업은 총 3회 시도를 설계 기본값으로 둔다. 재시도 간격은 5초→30초, 약간의 jitter를 허용한다. rate limit이 알려주는 대기 시각이 더 늦으면 그것을 사용한다. Review의 총 호출 한도는 [Review 문서](../../domain/review/README.md)가 우선한다.

재시도 가능한 원인은 일시 네트워크·Provider 5xx·회복 가능한 rate limit이다. invalid signature·권한 없음·잘못된 입력·지원 불가 Snapshot은 반복하지 않는다. parser crash/시간 초과는 파일 실패로 기록하고 무한 재시도하지 않는다.

시작 시 및 loop 중 만료된 LEASED를 회수한다. 남은 횟수가 있으면 READY로, 없으면 DEAD로 이동한다. 주입된 domain 실패 callback으로 Analysis/SyncRun 등도 같은 transaction에서 갱신한다. domain 상태를 RUNNING에 영구 방치하지 않는다.

## 보장 범위

실행은 중복될 수 있다. UNIQUE dedupe_key·결과 upsert·lease fence로 DB 결과를 멱등하게 만든다. 외부 API/LLM의 부수 효과나 과금이 정확히 한 번 발생한다는 보장은 없다.

FastAPI BackgroundTasks는 응답 후 작업을 실행할 수 있지만 영속 큐가 아니다. 여기서는 그것만으로 핵심 Job을 보관하지 않는다. [S-FASTAPI-BG](../../reference/SOURCES.md#s-fastapi-bg)

Render 무료 서비스가 잠들면 embedded runner도 진행을 보장하지 못한다. DB에 남은 작업은 다음 기동 때 복구하지만 24시간 실행을 보장하지 않는다. [배포 계약](../../operations/RENDER.md)을 반드시 함께 적용한다.

## 필수 테스트

동시 claim·commit 직후 강제 종료·lease 만료·stale worker 완료·중복 enqueue·재시도 횟수 소진·도메인 상태 동기화·Job cancel·secret-free payload·사용자/설치 권한 재검증이 필요하다.
