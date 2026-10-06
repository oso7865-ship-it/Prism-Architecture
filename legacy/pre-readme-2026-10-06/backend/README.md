# PRism Backend

Python 3.12 / FastAPI / SQLAlchemy / PostgreSQL 개발 기반입니다. 인증·팀·저장소·PR·Job·Webhook·분석 15개 테이블과 마이그레이션을 구현했습니다. GitHub 로그인·프로필·세션 갱신·로그아웃 API를 로컬 구현했습니다. 실제 GitHub 기본 로그인 흐름은 사용자 확인 완료이며 Workspace·저장소 연결·PR sync Job을 추가 구현했고 실제 GitHub App 연결과 PR 조회를 확인했습니다. 고정 커밋 정적 분석과 결과 API를 구현했습니다. 수동 DeepSeek 리뷰도 구현했습니다. 운영 모드는 비활성화했으며 현 단계는 로컬 개발용입니다.

최신 검증: [계약 복원·누락 진단 보고서](reports/2026-09-28_recall-repair_report.md). 2026-09-28 계약 복원·진단·동일 조건 비교를 완료했다. Linux359 tests PASS. 최종 후보는 핵심 결함 위치6/6이지만 설명·개선안 정확도3/6으로 채택 FAIL, 신규 사례24/24·기존 회귀45/46이다. 실패 후보는 evals/recall-repair에 보존하고 제품 지침은 rh1-d634ca5b77229914로 복원했다. V4 16/48KiB·리뷰당2회·팀 하루30·리랭커 OFF 유지. 유료 누적1352/3000·잔여1648, 자동 실행 없음. 기존 v1 잠정11/18은 축약 계약 오류가 있어 실제 PR recall로 사용하지 않는다. 독립 사람 검수와 값·분기·예외 추론 오류 해결이 남았다.

## 실행

Git, uv 0.12.18, Python 3.12가 필요합니다. uv는 필요한 Python을 다운로드할 수 있습니다.

```bash
git clone https://github.com/oso7865-ship-it/Prism-Backend.git prism-backend
cd prism-backend
uv sync --locked
uv run uvicorn app.main:create_app --factory --loop app.shared.database.event_loop:loop_factory --reload --no-access-log
```

DB 설정이 없어도 `/health/live`는 200입니다. `/health/ready`는 DB에 연결할 수 없으면 503이며 내부 오류·접속 문자열을 공개하지 않습니다. 로그인 및 설정된 GitHub App 연동 시 외부 API를 호출합니다. AI_ENABLED=true는 인증·DB·GitHub App·DeepSeek 키가 설정되어야 시작됩니다. SYNC_RUNNER_ENABLED는 PR sync 전용 영속 runner 옵션입니다.

## 로컬 PostgreSQL

개발 기준 이미지: PostgreSQL 17. 운영 호스팅 선택과는 별개입니다. Docker Desktop 또는 Docker Engine + Compose를 준비한 다음 `config/development.example`을 `.env`로 복사하고 로컬 비밀번호와 DATABASE_URL을 맞춥니다. 예시 비밀번호는 로컬 개발 전용입니다.

```bash
docker compose up -d --wait
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --loop app.shared.database.event_loop:loop_factory --reload --no-access-log
```

HeidiSQL: PostgreSQL TCP/IP / 127.0.0.1 / 5432 / 사용자 prism / DB prism / .env의 비밀번호. 포트는 루프백에만 바인딩합니다. named volume에 데이터가 유지되며 `docker compose down -v`는 데이터를 삭제하므로 평소에는 `docker compose down`만 사용합니다.

마이그레이션은 빈 기준선 0001 다음 0002에서 users, login_attempts, refresh_sessions, workspaces, workspace_members, invitations를 생성합니다. 0003은 저장소·설정·PR·동기화·Job 5개를 추가합니다. 물리 FK는 없으며 서비스에서 논리 관계와 팀 권한을 검증합니다. API startup에서 migration이나 create_all을 실행하지 않습니다. [컬럼 명세](docs/database/IDENTITY_SCHEMA.md)와 [로컬 DB·HeidiSQL·별도 테스트 DB 안내](docs/database/LOCAL_POSTGRES.md)를 참고하세요.

## 검증

```bash
uv run ruff check app tests migrations
uv run ruff format --check app tests migrations
uv run mypy app
uv run pytest -q -m "not integration"
```

실제 DB 검사는 `_test`로 끝나는 별도 DB에 TEST_DATABASE_URL을 설정한 후 `uv run pytest -q -m integration`으로 실행합니다. 임시 스키마에서 제약조건·동시 쓰기·ORM 저장·트랜잭션 rollback을 검증합니다. CI에는 PostgreSQL 17 migration 왕복과 `alembic check`, 전체 테스트를 구성했습니다. 테스트 DB가 없어 skip된 경우 DB 검증 통과로 처리하지 않습니다.

구조: app/main.py는 조립, app/shared/config는 설정, database는 세션·트랜잭션, observability는 health를 소유합니다. 업무 도메인은 실제 기능 추가 시 app/domain 아래에 만듭니다.

현재 로컬에서는 GitHub OAuth/App 연결, PR 동기화, 정적 분석 및 DeepSeek 수동 리뷰를 확인했습니다. 최신 범위·한계는 [진행 현황](docs/PROJECT_STATUS.md)과 [최신 Report](reports/_LATEST.md)를 따릅니다.

## 하네스와 다른 PC에서 재개

이 저장소 루트의 CLAUDE.md → PROJECT_HARNESS/00.PROJECT_CONTEXT.md → 작업별 문서 순서로 읽습니다. 공통 하네스는 [HARNESS](https://github.com/oso7865-ship-it/HARNESS)의 `0b7dcf9d567eaaa0c883eaee73620aa07cf60019` 사본입니다. 상위 폴더가 없어도 사용할 수 있습니다. 원본 유지보수 보고서는 출처 이력이며 현재 제품 상태는 CLAUDE_HARNESS/05.WORKING_CONTEXT.md와 부착 프로젝트 최신 Report를 따릅니다.

[아키텍처 연결](docs/ARCHITECTURE.md)과 architecture.json으로 설계의 원본·기준 커밋을 추적합니다. 아키텍처를 바꾸면 원본 저장소에 ADR과 소유 문서를 갱신합니다. 각 저장소의 main이 통합 기준이며 이후 기능 작업은 별도 브랜치·PR·CI로 검증합니다. 초기 빈 저장소의 첫 커밋은 main으로 게시합니다. 브랜치 보호 설정 자체는 아직 적용하지 않았습니다.

작업 시작: git status로 로컬 변경 확인 → 깨끗한 상태에서 git pull --ff-only → 의존성 잠금 기준 설치 → 최신 Report의 미해결 항목 확인. 작업 종료: 검증 → Report/Working Context 갱신 → 커밋·푸시. 비밀 값과 가상환경·node_modules는 Git에 올리지 않습니다.

하네스 연결 검사: `node CLAUDE_HARNESS/scripts/validate-project-adapter.mjs --project-root . --require-adapter --strict --json`.

## 확인된 검증 기록

[초기 구현 CI](https://github.com/oso7865-ship-it/Prism-Backend/actions/runs/36039579708)는 이전 5개 테스트 기준 기록입니다. 이번 DB 단계는 로컬 Docker PostgreSQL 17에서 migration 왕복·drift 검사, 테스트 28개 및 실제 Uvicorn readiness 200을 확인했습니다. [이번 구현 커밋의 원격 CI](https://github.com/oso7865-ship-it/Prism-Backend/actions/runs/36127425357)도 통과했습니다. 현재 게시 상태는 [최신 Report](reports/_LATEST.md)를 따릅니다. [작업 계획·체크리스트](docs/work-plans/2026-09-25_identity-database.md), [검증·트러블슈팅 리포트](reports/2026-09-25_identity-database_report.md)를 참조하세요.

## GitHub 로그인 수동 테스트

[실행 방법·설정·수동 체크리스트](docs/GITHUB_LOGIN.md). 프론트는 http://localhost:5173 을 사용합니다. 로컬 OAuth 설정은 `.env`에만 있으며 Git에 포함하지 않습니다. 최신 구현·검증 상태는 [Report](reports/2026-09-25_github-login_report.md)를 따릅니다.

## 팀·저장소 연결 (2026-09-26)

구현은 dev에서 진행한다. 팀/초대/권한·GitHub App 연결·PR 동기화 화면과 API를 추가했다. 실제 App 등록·실계정 연결 확인은 별도이며 최신 결과는 reports/_LATEST.md를 따른다. 로그인용 OAuth App과 저장소용 GitHub App은 서로 다른 설정이다.

실행과 App 등록: [팀·저장소 안내](docs/TEAM_REPOSITORIES.md).

## Webhook 단계

Webhook 자동 PR 동기화와 설치 철회 차단을 구현했다. 설정·현재 지원 이벤트·실제 수신 주소 준비와 검증 범위는 [Webhook 안내](docs/WEBHOOK.md), 결과는 [최신 리포트](reports/_LATEST.md)를 따른다. GitHub에서 직접 전송하는 공개 Webhook 검증은 후속 작업이다. 정적 분석·AI 수동 리뷰는 아래 구현 안내를 따른다.

## PR 정적 분석 (2026-09-26)

0005 migration 적용 후 `.env`에서 `ANALYSIS_RUNNER_ENABLED=true`로 수동 분석 runner를 켭니다. Java/Python/JavaScript/TypeScript의 fixture 검증을 마친 29개 규칙을 지원합니다. [실행·API·제한](docs/STATIC_ANALYSIS.md), [작업 계획](docs/work-plans/2026-09-26_static-analysis.md), [검증 기록](reports/2026-09-26_static-analysis_report.md)을 참조하세요. AI의 기본 설정은 OFF이며 아래 안내에 따라 로컬에서 수동 활성화합니다. 공개 Webhook 자동 분석 검증은 별도입니다.

## 수동 AI 리뷰

0006 migration 적용 후 서버 전용 `.env`에서 AI_ENABLED=true, DEEPSEEK_MODEL=deepseek-flash, DEEPSEEK_API_KEY를 설정하고 API를 재시작합니다. 팀 소유자가 완료된 정적 분석 아래 AI 코드 리뷰에서 매번 전송 동의 후 요청합니다. LangChain ChatDeepSeek를 사용하며 최대8파일/입력24KiB/출력2000토큰, 팀당 UTC 하루30회 접수·동시1개·자동재시도0입니다. 원문 prompt/diff를 저장하지 않고 검증된 결과·사용량·이력을 저장합니다. 이미 호출된 요청은 취소해도 과금될 수 있습니다.

[설계·체크리스트](docs/work-plans/2026-09-26_ai-review.md)

DeepSeek가 읽는 리뷰 지침·버전·오프라인 평가 방법은 [리뷰 하네스](docs/REVIEW_HARNESS.md)를 따른다. 개발 에이전트용 CLAUDE_HARNESS와 분리한다.

최신 [품질 안정화 기록](reports/2026-09-27_ai-quality-stabilization_report.md)은 응답 거절 원인, import 문맥 누락 수정, 반복·별도 사례의 품질과 남는 한계를 구분한다. [합성 평가 재현](evals/quality-stabilization/README.md)과 [유료 호출 승인·집계](docs/PAID_EVALUATION_AUTHORIZATION.md)를 확인한 후에만 유료 평가를 실행한다.

새 리뷰의 메서드·참조 문맥 수집은 BOUNDED_CODE_V3이다. 선택적 리랭커는 실제 비교에서 기본 활성화 기준을 통과하지 못해 OFF를 유지한다. [문맥 수집·설치·재현·한계](docs/CONTEXT_RETRIEVAL.md), [동일 후보·24회 유료 비교](reports/2026-09-27_context-reranking_report.md)를 참고한다.

## 배포 직전 준비

[배포 설정·운영 절차](docs/PREDEPLOYMENT.md)를 확인하세요. production HTTPS·Secure cookie·프록시 설정과 Docker 이미지를 준비했으며 실제 공개 배포는 수행하지 않았습니다. 검증 결과와 남은 사용자 결정은 [최신 Report](reports/_LATEST.md)를 따릅니다.
