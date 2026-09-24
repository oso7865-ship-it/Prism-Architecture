# 구현 저장소와 현재 단계

> ID: `IMPLEMENTATION` · 소유: `architecture` · 기준: `2026-09-25`
> 읽는 때: 구현 진행 상태 확인·다른 PC에서 작업 재개 시

- [Prism-Backend](https://github.com/oso7865-ship-it/Prism-Backend): Python 3.12, uv lock, FastAPI health, 설정, DB 세션·트랜잭션, 빈 Alembic 기준선, PostgreSQL 17 Compose, 테스트·CI.
- [Prism-Frontend](https://github.com/oso7865-ship-it/Prism-Frontend): Node 24, npm lock, Vue·Vite·TypeScript·Router, 개발 준비 화면, readiness 확인·테스트·CI.

각 저장소 루트의 AGENTS.md와 PROJECT_HARNESS를 읽는다. 사용자 HARNESS의 0b7dcf9d567eaaa0c883eaee73620aa07cf60019를 각 구현 저장소에 부착했다. 상위 로컬 폴더는 Git 저장소가 아니며 다른 PC에 필요하지 않다. 하네스는 작업 절차, 이 저장소는 제품 계약의 원본이다.

논리 경로 backend/app/...는 Prism-Backend의 app/...로, frontend/src/...는 Prism-Frontend의 src/...로 매핑한다. 기존 context_select.py에는 논리 경로를 전달한다. architecture.json이 각 구현 저장소의 설계 기준 커밋을 고정한다. 설계 변경 후 소비 저장소의 기준 커밋을 명시적으로 갱신한다.

현재 업무 도메인·로그인·PR·분석·AI는 미구현이다. 실제 서비스 배포는 하지 않았다. 기본 앱 테스트·빌드와 실제 PostgreSQL 검증은 구분하며 최신 명령·결과·CI 링크는 구현 저장소의 README와 최신 프로젝트 Report를 따른다. 로컬 Docker는 아직 사용할 수 없어 Compose 실행 검증이 남아 있다.

다음 구현은 TESTING의 단계에 따라 로그인·User·Workspace 흐름으로 진행한다. 실제 GitHub 등록·DeepSeek 모델/예산·도메인·운영 DB 호스팅·백업은 미정이다.

검증 증거: [백엔드 CI](https://github.com/oso7865-ship-it/Prism-Backend/actions/runs/36039579708)는 PostgreSQL 17 마이그레이션 왕복과 테스트 5개 통과, [프론트 CI](https://github.com/oso7865-ship-it/Prism-Frontend/actions/runs/36039823516)는 빌드·타입 검사와 제품 테스트 3개 통과다. 실제 제품 배포는 아니다.
