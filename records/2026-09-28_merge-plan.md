# 전체 병합·문서 저장소 분리 계획

- 요청: 현재 전체 작업을 병합하며 문서는 프론트/백엔드 저장소에 올리지 않는다.
- 규모 L. architecture main, backend/frontend dev→main. 원격 fetch 결과 세 저장소 모두 upstream과 동일함을 확인했다.
- 적용: git-workflow/terminal-ops/verification-loop, 문서·Security·코드 Gate. 사용자 최신 요청이 이전 개별 저장소 문서 부착 방식을 대체한다. 임의 force push/이력 재작성/사용자 파일 삭제는 하지 않는다.
- 문서 범위: README/AGENTS/CLAUDE, docs/reports, 개발 GENERAL_HARNESS/PROJECT_HARNESS, 그 밖의 Markdown 문서. 원래 경로와 내용을 records/backend·frontend에 보존하고 SHA-256 manifest로 검증한다. 기존 로컬 사본은 남기고 Git index에서만 제외한다.
- 제품이 로드하는 AI 지침과 평가 fixture는 실행 리소스다. 내용은 보존하고 .prompt로 변경해 코드 저장소에 유지한다. 실패한 평가 후보는 실험 fixture일 뿐 활성화하지 않는다.
- 소비 저장소에는 문서 위치/pinned revision 및 안전한 로컬 복원 스크립트, CI의 문서 재유입/비밀 검사를 둔다. CI를 삭제된 하네스 경로에서 독립 검사로 전환한다.
- 아키텍처 ADR-ARCH-003과 소유 문서를 작성하고, 과거 아카이브는 원래 상대 경로 기준 기록임을 명시한다. 문서 원문 보존 검사는 manifest, 현재 설계 링크/ID 검사는 validate_docs로 분리한다.
- 검증: 백엔드 Linux PostgreSQL 전체 테스트·migration 왕복/drift·Ruff/mypy·프롬프트 내용 hash·컨테이너, 프론트 전체 테스트/build, 문서/복원/저장소 경계, 비밀 검사. 유료 LLM 추가 호출은 불필요하며 하지 않는다.
- 게시: 아키텍처 main 먼저 commit/push→구현 architecture.json pin→dev commit/push→CI 확인→main 병합/push→원격 CI·파일 목록 확인. 완료 후 구현 checkout은 사용자 상시 작업 지시대로 dev에 둔다.
- 기존 의미 품질 FAIL은 보존하며 출시/품질 성공으로 승격하지 않는다. 병합은 소스 통합이며 배포가 아니다.
- 복구: 중앙 문서/manifest·Git 기존 이력으로 복원 가능. 검증/게시 실패 시 단계와 재개 지점을 기록한다.
