# 아키텍처 결정 맵

> ID: `DECISIONS` · 소유: `architecture-decisions` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 영역별 ADR과 이전 결정 번호를 찾을 때

결정 본문은 [ADR 패키지](../adr/README.md)에 분리한다. 현재 계약은 각 소유 문서, 미정 사항은 [OPEN_ITEMS](OPEN_ITEMS.md)가 기준이다. 상태는 구현 완료 여부가 아니다. 외부 기술 사실의 근거는 [SOURCES](../reference/SOURCES.md)를 따른다.

## 영역 맵

| 코드 | 디렉터리 | 책임 | 소유 문서 |
|---|---|---|---|
| ARCH | `adr/architecture/` | 전체 구조·의존성·언어 스택 | [PACKAGE_RULES.md](../PACKAGE_RULES.md) |
| DOCS | `adr/documentation/` | 문서·ADR 관리 | [INDEX.md](../INDEX.md) |
| ANALYSIS | `adr/analysis/` | 지원 언어·파이프라인·규칙 | [domain/analysis/README.md](../domain/analysis/README.md) |
| REVIEW | `adr/review/` | AI 모델·설명·비용 | [domain/review/README.md](../domain/review/README.md) |
| INTEGRATION | `adr/integration/` | GitHub·PR 동기화·Webhook | [domain/pull_request/SYNC_POLICY.md](../domain/pull_request/SYNC_POLICY.md) |
| RUNTIME | `adr/runtime/` | Job·Worker·복구 | [shared/jobs/README.md](../shared/jobs/README.md) |
| DATA | `adr/data/` | DB·스키마·트랜잭션 | [shared/database/README.md](../shared/database/README.md) |
| DEPLOY | `adr/deployment/` | 호스팅·도메인·배포 | [operations/DEPLOYMENT.md](../operations/DEPLOYMENT.md) |
| SECURITY | `adr/security/` | 인증·인가·테넌트·개인정보 | [operations/SECURITY_PRIVACY.md](../operations/SECURITY_PRIVACY.md) |
| FRONTEND | `adr/frontend/` | 화면·클라이언트·프록시 | [frontend/README.md](../frontend/README.md) |
| PRODUCT | `adr/product/` | 이름·제품 범위·공개 대상 | [CORE.md](../CORE.md) |

## ADR 이력

| ADR | 결정 | 상태 | 이전 번호 |
|---|---|---|---|
| [ADR-ARCH-001](../adr/architecture/ADR-ARCH-001-python-domain-boundaries.md) | Python과 업무 소유권 중심 구조 | ACCEPTED | D-001, D-005, C-001, C-006 |
| [ADR-DOCS-001](../adr/documentation/ADR-DOCS-001-selective-reading.md) | 패키지별 선택 읽기 | ACCEPTED | D-006 |
| [ADR-ANALYSIS-001](../adr/analysis/ADR-ANALYSIS-001-static-snapshot-analysis.md) | 네 언어의 고정 Snapshot 정적 분석 | ACCEPTED | D-003, C-004, C-005, D-012 |
| [ADR-REVIEW-001](../adr/review/ADR-REVIEW-001-optional-explanations.md) | 정적 Finding과 선택적 AI 설명 분리 | SUPERSEDED | D-007, C-007 |
| [ADR-REVIEW-002](../adr/review/ADR-REVIEW-002-deepseek-provider.md) | DeepSeek Provider 선택 | ACCEPTED | D-009 |
| [ADR-REVIEW-003](../adr/review/ADR-REVIEW-003-bounded-manual-code-review.md) | 제한된 코드 문맥 수동 AI 리뷰·실행 한도 | SUPERSEDED | REVIEW-001 대체 |
| [ADR-REVIEW-004](../adr/review/ADR-REVIEW-004-versioned-review-harness.md) | DeepSeek 리뷰 하네스·버전·평가 | ACCEPTED | REVIEW-003 확장 |
| [ADR-REVIEW-005](../adr/review/ADR-REVIEW-005-evidence-admission.md) | AI 근거 줄·조건·결과·가정 검증 | SUPERSEDED | REVIEW-004 확장 |
| [ADR-REVIEW-006](../adr/review/ADR-REVIEW-006-review-workflow.md) | 검토 질문·관련 문맥·개인 처리 기록·리뷰 탐색 | SUPERSEDED | REVIEW-003/005 대체 |
| [ADR-REVIEW-007](../adr/review/ADR-REVIEW-007-bounded-context-ranking.md) | 제한된 함수·참조 문맥과 선택적 로컬 재정렬 | SUPERSEDED | REVIEW-006 대체 |
| [ADR-REVIEW-008](../adr/review/ADR-REVIEW-008-team-daily-allowance.md) | 팀별 AI 리뷰 하루30회·일반 모델 표시 | SUPERSEDED | REVIEW-009가 요약 구성만 대체 |
| [ADR-REVIEW-009](../adr/review/ADR-REVIEW-009-derived-review-summary.md) | 검증된 리뷰 항목으로 사용자 요약 구성 | SUPERSEDED | REVIEW-010이 문맥·검증 호출 변경, 요약 유지 |
| [ADR-REVIEW-010](../adr/review/ADR-REVIEW-010-evidence-first-verified-review.md) | 필수 문맥 보존·16/48KiB·두 단계 검증 | SUPERSEDED | REVIEW-011이 빈 초안·코드 열람 변경 |
| [ADR-REVIEW-012](../adr/review/ADR-REVIEW-012-purpose-and-team-standards.md) | 목적별 리뷰·취약점·팀 문서 RAG | ACCEPTED | REVIEW-011의 코드 취득/검증 계약 유지·RAG 범위 추가 |
| [ADR-REVIEW-011](../adr/review/ADR-REVIEW-011-empty-recheck-and-source-view.md) | 빈 초안 파일별 재검토·사이트 내 코드 열람 | SUPERSEDED | REVIEW-010 대체, 최대2회·과거 결과 불변 유지 |
| [ADR-REVIEW-013](../adr/review/ADR-REVIEW-013-recovery-and-evidence-checks.md) | 누락 복구·출력 복구·제한 연산·독립 보안 근거 | SUPERSEDED | REVIEW-011 대체, 코드 열람·한도 유지 |
| [ADR-REVIEW-014](../adr/review/ADR-REVIEW-014-grounded-claims-and-repair-guards.md) | 제한 계산 설명·출력 조건·수정안 반례 차단 | ACCEPTED | REVIEW-013 대체, 호출·권한·원문 비저장 유지 |
| [ADR-INTEGRATION-001](../adr/integration/ADR-INTEGRATION-001-github-pr-sync.md) | 실제 GitHub 연동과 PR 동기화 | ACCEPTED | D-004, C-003, D-010 |
| [ADR-INTEGRATION-002](../adr/integration/ADR-INTEGRATION-002-verified-app-connection.md) | 사용자·App 권한 검증 연결과 단계별 PR 조회 | ACCEPTED | — |
| [ADR-RUNTIME-001](../adr/runtime/ADR-RUNTIME-001-durable-jobs.md) | PostgreSQL 영속 Job과 복구 | BASELINE | C-002 |
| [ADR-DEPLOY-001](../adr/deployment/ADR-DEPLOY-001-render-real-deployment.md) | Render 배포와 실제 주소 사용 | SUPERSEDED | D-002, D-010 → DEPLOY-003 |
| [ADR-DEPLOY-002](../adr/deployment/ADR-DEPLOY-002-production-boundary.md) | Production 설정·배포 전 검증 경계 | SUPERSEDED | DEPLOY-003에 운영 계약 유지 |
| [ADR-DEPLOY-003](../adr/deployment/ADR-DEPLOY-003-aws-backend.md) | AWS 백엔드와 production 계약 유지 | SUPERSEDED | DEPLOY-004가 EC2 실행 서비스 확정 |
| [ADR-DEPLOY-004](../adr/deployment/ADR-DEPLOY-004-ec2-runtime.md) | EC2 백엔드 실행 서비스 | SUPERSEDED | DEPLOY-006이 자동 배포 구체화, EC2 유지 |
| [ADR-DEPLOY-005](../adr/deployment/ADR-DEPLOY-005-rds-initial-runtime.md) | RDS·서울 EC2·전용 DB 계정·초기 비밀 주입 | ACCEPTED | DEPLOY-004 보완, 앱 배포는 미완료 |
| [ADR-DEPLOY-006](../adr/deployment/ADR-DEPLOY-006-private-ghcr-automatic-release.md) | private GHCR·AWS OIDC/SSM·Vercel 자동 배포 | ACCEPTED | DEPLOY-004 대체, 초기 연결 후 main 자동 배포 |
| [ADR-PRODUCT-001](../adr/product/ADR-PRODUCT-001-prism-name.md) | PRism 프로젝트명 | ACCEPTED | D-008 |
| [ADR-PRODUCT-002](../adr/product/ADR-PRODUCT-002-staged-public-access.md) | 초기 내부 사용과 향후 외부 가입 | ACCEPTED | D-011 |
| [ADR-DATA-001](../adr/data/ADR-DATA-001-postgresql.md) | PostgreSQL 사용 | ACCEPTED | — |
| [ADR-FRONTEND-001](../adr/frontend/ADR-FRONTEND-001-vue-vercel.md) | Vue와 Vercel 프론트 구성 | BASELINE | — |
| [ADR-DOCS-002](../adr/documentation/ADR-DOCS-002-area-adrs.md) | 영역별 ADR과 변경 이력 관리 | ACCEPTED | — |
| [ADR-ARCH-002](../adr/architecture/ADR-ARCH-002-independent-repositories.md) | 독립 저장소와 프로젝트별 하네스 | SUPERSEDED | — |
| [ADR-ARCH-003](../adr/architecture/ADR-ARCH-003-central-documentation.md) | 문서 중앙 관리·로컬 복원 | ACCEPTED | ARCH-002 대체 |
| [ADR-DATA-002](../adr/data/ADR-DATA-002-local-postgres-foundation.md) | PostgreSQL 17 로컬 개발 기반 | ACCEPTED | — |
| [ADR-DATA-003](../adr/data/ADR-DATA-003-logical-relations-schema.md) | 물리 FK 없는 17개 테이블·애플리케이션 무결성 | ACCEPTED | — |

D-010은 실제 연동과 배포 두 책임으로 나누어 이관했다. D-001의 LangChain 선택은 REVIEW-001에서 함께 설명한다. SECURITY 영역은 번호만 예약하며 별도 ADR은 아직 없다.

## 이관한 설계 기본값의 범위

모듈형 모놀리스·embedded runner·초대/세션/보관 기간·API 경로·자원 상한·Rule 38개·FINDINGS_ONLY/AI OFF·동일 출처 프록시는 실행 검증 전 설계 기본값이다. 이번 이관으로 사용자 승인을 새로 부여하지 않는다. 세부 수치는 소유 문서에 유지하며 이후 변경 시 해당 영역 ADR을 만든다.
