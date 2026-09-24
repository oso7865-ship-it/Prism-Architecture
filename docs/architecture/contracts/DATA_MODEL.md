# 데이터 소유권과 핵심 관계

> ID: `DATA-MODEL` · 소유: `data-contracts` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 테이블 관계·FK·유일성·조회 스코프를 설계할 때

이 문서는 아키텍처 수준의 논리 모델이다. 최종 DDL/컬럼 길이/모든 인덱스를 작성한 ERD는 아니며 migration 작성 때 소유 도메인의 계약과 함께 구체화한다.

```text
User ──< WorkspaceMember >── Workspace
                               │
                               ├──< RepositoryConnection ──< RuleConfigVersion
                               │                │
                               │                └──< PullRequest ──< AnalysisRun
                               │                                        │
                               │                                        ├──< Finding
                               │                                        └──< ReviewRun ──< FindingExplanation
                               └──< Invitation

기술 실행: Job / WebhookDelivery / PullRequestSyncRun
인증 상태: LoginAttempt / RefreshSession
```

## 소유 테이블과 유일성

| 소유 | 테이블 | 주요 제약 |
|---|---|---|
| user | users | github_user_id UNIQUE |
| auth | login_attempts, refresh_sessions | state_hash/token_hash UNIQUE |
| workspace | workspaces, workspace_members, invitations | member(workspace_id,user_id) UNIQUE; active OWNER 최대 1 |
| repository | repository_connections, rule_config_versions | 활성 github_repository_id UNIQUE; config(repo_id,version) UNIQUE |
| pull_request | pull_requests, pull_request_sync_runs | (repository_connection_id,pr_number) UNIQUE |
| analysis | analysis_runs, findings, analysis_file_results | execution_key UNIQUE; finding(analysis_id,fingerprint) UNIQUE |
| review | review_runs, finding_explanations | review_key UNIQUE; explanation(review_run_id,finding_id) UNIQUE |
| webhook | webhook_deliveries | (provider,delivery_id) UNIQUE |
| shared/jobs | jobs | dedupe_key UNIQUE |

OWNER가 정확히 한 명인지는 service transaction과 테스트도 필요하다. partial UNIQUE만으로 '최소 한 명'까지 보장했다고 하지 않는다.

## 관계 무결성

도메인별 ORM은 해당 도메인에 둔다. cross-domain 관계는 FK/ID로 연결하되 ORM lazy relationship으로 다른 업무 상태를 마음대로 변경하지 않는다. 다른 도메인 읽기는 공개 계약을 사용한다. DB-level FK는 금지하지 않는다.

workspace_id를 하위 리소스에 중복 저장할 경우 `(id, workspace_id)` UNIQUE와 복합 FK 또는 동등한 강한 제약으로 부모와의 일치를 검증한다. 단순한 중복 컬럼만 추가하고 인가가 보장된다고 하지 않는다. Query에도 workspace 스코프를 적용한다.

AnalysisRun/ReviewRun은 불변 입력 버전과 별도의 실행 상태를 가진다. code source, diff, AST, 전체 Prompt, GitHub OAuth token, private key는 테이블에 넣지 않는다. Finding 위치/경로·PR 제목·설명도 팀의 비공개 데이터다.

## 실행과 보관

Job aggregate_id는 기술 참조이고 처리 의미는 handler가 정한다. 도메인/Job 상태 갱신을 같은 트랜잭션으로 묶는 규칙은 [Jobs](../shared/jobs/README.md)를 따른다. 조회용 결과에 Job lease 내부 필드를 그대로 노출하지 않는다.

보관 기간과 연결 해제/삭제 순서는 [보안·보관](../operations/SECURITY_PRIVACY.md)이 유일한 기준이다. 정리 작업은 lease 중인 Job을 먼저 막고, 자식 설명/결과→실행→부모 메타데이터 순서로 안전하게 삭제한다. 무조건 CASCADE로 모든 분석 이력을 제거하는 정책을 몰래 넣지 않는다.

핵심 인덱스 후보: member(user_id,status), repository(workspace_id,status), PR(repo_id,updated_at,id), analysis(workspace_id,pr_id,created_at), finding(analysis_id,severity,id), jobs(state,available_at). 실제 query plan/데이터 분포로 검증한다.
