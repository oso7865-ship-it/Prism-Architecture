# 구현 저장소와 현재 단계

> ID: `IMPLEMENTATION` · 소유: `architecture` · 기준: `2026-09-25`
> 읽는 때: 구현 진행 상태 확인·다른 PC에서 작업 재개 시

- [Prism-Backend](https://github.com/oso7865-ship-it/Prism-Backend): Python 3.12, uv lock, FastAPI health, 설정, DB 세션·트랜잭션, 빈 Alembic 기준선, PostgreSQL 17 Compose, 테스트·CI.
- [Prism-Frontend](https://github.com/oso7865-ship-it/Prism-Frontend): Node 24, npm lock, Vue·Vite·TypeScript·Router, 개발 준비 화면, readiness 확인·테스트·CI.

각 저장소 루트의 AGENTS.md와 PROJECT_HARNESS를 읽는다. 사용자 HARNESS의 0b7dcf9d567eaaa0c883eaee73620aa07cf60019를 각 구현 저장소에 부착했다. 상위 로컬 폴더는 Git 저장소가 아니며 다른 PC에 필요하지 않다. 하네스는 작업 절차, 이 저장소는 제품 계약의 원본이다.

논리 경로 backend/app/...는 Prism-Backend의 app/...로, frontend/src/...는 Prism-Frontend의 src/...로 매핑한다. 기존 context_select.py에는 논리 경로를 전달한다. architecture.json이 각 구현 저장소의 설계 기준 커밋을 고정한다. 설계 변경 후 소비 저장소의 기준 커밋을 명시적으로 갱신한다.

인증·팀 6개 ORM과 Alembic 0002는 구현했다. 로그인·Workspace 서비스/API·PR·분석·AI는 미구현이다. 실제 서비스 배포는 하지 않았다. 기본 앱 테스트·빌드와 실제 PostgreSQL 검증은 구분하며 최신 명령·결과·CI 링크는 구현 저장소의 README와 최신 프로젝트 Report를 따른다. 로컬 Docker PostgreSQL 17에서 migration 왕복·drift 검사·테스트 28개·실제 API readiness 200을 확인했다.

다음 구현은 TESTING의 단계에 따라 로그인·User·Workspace 흐름으로 진행한다. 실제 GitHub 등록·DeepSeek 모델/예산·도메인·운영 DB 호스팅·백업은 미정이다.

2026-09-25 DB 설계 구체화: [17개 물리 테이블 설계](../contracts/schema/README.md)와 [ADR-DATA-003](../adr/data/ADR-DATA-003-logical-relations-schema.md)에 컬럼·타입·인덱스·물리 FK 미사용·애플리케이션 관계 검증을 기록했다. 로그인·팀 6개 테이블을 백엔드에서 구현·로컬 검증했다. 나머지 11개와 서비스 논리 참조 검증은 후속 단계다. 이 설계를 게시한 커밋으로 백엔드 architecture.json을 연결하며 하네스 동기화는 보류한다.

검증 증거: [백엔드 CI](https://github.com/oso7865-ship-it/Prism-Backend/actions/runs/36039579708)는 PostgreSQL 17 마이그레이션 왕복과 테스트 5개 통과, [프론트 CI](https://github.com/oso7865-ship-it/Prism-Frontend/actions/runs/36039823516)는 빌드·타입 검사와 제품 테스트 3개 통과다. 실제 제품 배포는 아니다.

## 2026-09-26 현재 작업

이전 문단은 기반 단계의 이력이다. GitHub 로그인·프로필·refresh·logout은 구현·게시·CI 및 사용자 기본 흐름 확인을 마쳤다. 구현 저장소는 dev, 이 아키텍처 저장소는 main에서 작업한다.
팀 생성·초대·역할·소유권 이전, GitHub App 연결, PR sync Job·메타데이터·기존 리뷰 상태 조회를 현재 working-tree에서 구현했다. migration 0003은 저장소/설정/PR/sync/jobs 5개를 추가해 업무 테이블은 11개이며 물리 FK는 0개다. 설계 전체 17개 중 분석/Review/Webhook 관련 나머지는 후속 단계다.
실제 GitHub App 설정·연동은 미완료이며 자동 테스트와 구분한다. 연결·리뷰 조회 범위는 ADR-INTEGRATION-002, 최신 실행 증거는 구현 저장소 reports/_LATEST.md를 따른다. 하네스 사본 동기화는 보류한다.

## 2026-09-26 Webhook 후속 구현

GitHub App 등록·실계정 저장소 연결·Draft PR #1 메타데이터 동기화/상세 조회를 확인했다. Webhook 수신·영속 Delivery/Job·SYSTEM PR 단건 동기화·설치 권한 제거 시 SUSPENDED 처리를 구현했다. migration 0004 추가로 업무12테이블/FK0. 전체78 tests 및 migration drift/왕복 검증 완료.
로컬 생성 서명 이벤트로 API202/중복200→Delivery PROCESSED→실제 GitHub SYSTEM sync COMPLETED 1개를 확인했다. GitHub에서 직접 전송된 Webhook은 아직 검증하지 않았다(공개 HTTPS 주소 미정). 정적 분석 실행·규칙·DeepSeek 및 UI 개선은 후속이다. 기존 설계의 Webhook 부분 구현이므로 새 ADR은 추가하지 않았다.

## 2026-09-26 정적 분석 실행·규칙 구현

위 문단은 단계별 이력이며 현재는 backend/frontend dev working-tree에서 분석 접수·조회·이력·파일별 평가·Finding·취소·재분석을 구현했다. 0005는 analysis_runs/analysis_file_results/findings를 추가한다. 업무15테이블/FK0이며 AI review 2테이블은 후속이다. 사용자 코드 실행 없이 Tree-sitter 격리 프로세스를 사용한다. 기존 Analysis 계약의 초기 구현이므로 새 정책 ADR은 추가하지 않는다.

활성 rule set static-1.0.0: COM-001/002/004/009/010, JAVA-004/005/006/007/008, PY-001/002/003/006, JS-001/002/003/004, TS-001/002/003/004/005 (총23개). 나머지 제안 규칙은 미구현/비활성이다. 전체 타입·데이터 흐름·Vue SFC·사용자 규칙 설정은 후속이며 미지원 설정은 거부한다. 언어 중립 비밀 형식 관찰은 원문을 저장하지 않는다.

백엔드 전체134 tests, Ruff/mypy, 0005 왕복·drift, 프론트 build/23 tests를 통과했다. 실제 조직 chapchap-customer-service의 병합 PR #47에서 Java 1파일 FULL_SCOPE, COM-002 1건(46–137줄)을 확인했다. 최초 분석과 재분석 generation1이 완료됐고 모바일375px/필터/완료 후 버튼을 확인했다. Windows Psycopg 관련 기존 네이티브 access violation 진단은 테스트 exit0과 별개로 원인 미해결이다.

계획·검증·트러블슈팅 상세는 각 구현 저장소 reports/2026-09-26_static-analysis_report.md를 따른다. 이번 작업은 미커밋·미푸시이며 consumer architecture revision은 게시 후 갱신한다. 다음은 DeepSeek 설명/Review, 남은 고급 규칙, 공개 HTTPS Webhook 실전송, 배포/운영이며 하네스 동기화는 계속 보류한다.

## 규칙 확장 (static-1.1.0)

기존23개에 COM-003(조건/반복 깊이>4), PY-004/005(내장 eval/exec 직접 호출), PY-008(포괄 except), JS-005/006(eval/Function 동적 코드 생성)을 추가한29개다. 이름 바인딩·동적 변경을 확신할 수 없으면 해당 규칙 NOT_EVALUATED/BINDING_UNRESOLVED, 파일 범위 PARTIAL이다. 파일 안의 다른 이름 사용까지 보수적으로 제외하며 전역 타입/심볼 해석은 하지 않는다. 런타임 monkey patch와 외부 주입은 검증하지 않는다. PY-003과 PY-008 중복은 제외한다. 함수 경계에서 깊이를 초기화하며 else-if/elif는 같은 깊이로 취급한다. 새6규칙은 version1.0.0이고 기존 규칙 버전은 유지한다. 나머지9개 후보는 비활성이다.
