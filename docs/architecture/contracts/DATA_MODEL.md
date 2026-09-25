# 데이터 소유권과 핵심 관계

> ID: `DATA-MODEL` · 소유: `data-contracts` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 테이블 관계·FK·유일성·조회 스코프를 설계할 때

이 문서는 17개 테이블의 논리 관계와 소유권 지도다. 컬럼·타입·NULL·기본값·PK/UNIQUE/CHECK·조회 인덱스는 [물리 스키마 설계](schema/README.md)를 따른다. **물리 FK는 사용하지 않는다.** 인증·팀 6개 ORM/migration·로컬 DB 적용은 완료했으며 나머지 11개는 후속 구현 대상이다.

각 테이블의 목적과 참조 컬럼별 대상은 [테이블 설명·관계표](schema/RELATIONS.md)에 정리되어 있다.

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
| repository | repository_connections, rule_config_versions | ACTIVE/SUSPENDED github_repository_id UNIQUE; config(repo_id,version) UNIQUE |
| pull_request | pull_requests, pull_request_sync_runs | (repository_connection_id,pr_number) UNIQUE |
| analysis | analysis_runs, findings, analysis_file_results | execution_key UNIQUE; finding(analysis_id,fingerprint) UNIQUE |
| review | review_runs, finding_explanations | review_key UNIQUE; explanation(review_run_id,finding_id) UNIQUE |
| webhook | webhook_deliveries | (provider,delivery_id) UNIQUE |
| shared/jobs | jobs | dedupe_key UNIQUE |

OWNER가 정확히 한 명인지는 service transaction과 테스트도 필요하다. partial UNIQUE만으로 '최소 한 명'까지 보장했다고 하지 않는다.

## 관계 무결성

도메인별 ORM은 해당 도메인에 둔다. cross-domain 관계는 논리 ID로 연결하고 물리 FK·참조 트리거·자동 CASCADE를 만들지 않는다. ORM lazy relationship으로 다른 업무 상태를 변경하지 않으며 다른 도메인 읽기·관계 검증은 공개 계약을 사용한다. [ADR-DATA-003](../adr/data/ADR-DATA-003-logical-relations-schema.md)

하위 리소스의 workspace_id는 서버가 검증한 부모에서 채운다. 부모 존재·Workspace 일치·현재 권한·연결 세대를 같은 트랜잭션에서 검사한다. 쓰기·삭제·권한 변경은 [Workspace 잠금 프로토콜](schema/README.md)을 함께 따른다. Query에도 workspace 스코프를 적용한다. 애플리케이션을 우회한 SQL까지 DB가 관계를 강제한다고 표현하지 않는다.

AnalysisRun/ReviewRun은 불변 입력 버전과 별도의 실행 상태를 가진다. code source, diff, AST, 전체 Prompt, GitHub OAuth token, private key는 테이블에 넣지 않는다. Finding 위치/경로·PR 제목·설명도 팀의 비공개 데이터다.

## 실행과 보관

Job aggregate_id는 기술 참조이고 처리 의미는 handler가 정한다. 도메인/Job 상태 갱신을 같은 트랜잭션으로 묶는 규칙은 [Jobs](../shared/jobs/README.md)를 따른다. 조회용 결과에 Job lease 내부 필드를 그대로 노출하지 않는다.

보관 기간과 연결 해제/삭제 순서는 [보안·보관](../operations/SECURITY_PRIVACY.md)이 유일한 기준이다. 정리 작업은 lease 중인 Job을 먼저 막고, 자식 설명/결과→실행→부모 메타데이터 순서로 안전하게 삭제한다. 무조건 CASCADE로 모든 분석 이력을 제거하는 정책을 몰래 넣지 않는다.

테이블별 인덱스 정의는 물리 스키마의 [인증·팀](schema/IDENTITY.md), [GitHub·PR](schema/GITHUB.md), [분석·AI](schema/RESULTS.md), [실행·웹훅](schema/EXECUTION.md)에 있다. 실제 query plan/데이터 분포 검증은 구현 단계에 수행한다. 위 관계선은 논리 관계이며 DB FK가 아니다.
