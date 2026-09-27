# 아키텍처 연결

제품 설계의 원본은 [Prism-Architecture](https://github.com/oso7865-ship-it/Prism-Architecture)다. architecture.json의 revision이 이 저장소의 기준 커밋이며 최신 main을 자동으로 적용하지 않는다.

독립 clone에서도 이 문서와 README로 실행·검증할 수 있다. 제품 계약을 수정할 때 원본 저장소의 해당 커밋을 별도 폴더에 clone/checkout하고 AGENTS.md → CORE → 작업별 소유 문서를 읽는다. context_select.py의 경로는 architecture.json의 logical_path_prefix와 현재 저장소 상대 경로를 합쳐 사용한다.

공통 실행 규칙은 원본 HARNESS에서 가져온 GENERAL_HARNESS 사본이다. PROJECT_HARNESS는 제품 문서와 작업 경로를 연결한다. 하네스 변경은 원본 커밋과 localChanges를 비교해 수동 반입하며 다른 제품 사본에서 복사하지 않는다. 제품 ADR은 아키텍처 저장소에서 새 영역 번호로 작성한 후 양쪽 참조 커밋을 갱신한다.

아키텍처 필수 경계: 업무는 domain/feature 소유, shared는 기술 공통 기능, 원문 코드 실행·설치 금지, AI 기본 OFF, 인증·Workspace·GitHub 권한 분리. 현재 업무 기능은 미구현이며 README가 실제 구현 현황의 진입점이다.

2026-09-26 게시 갱신: 아키텍처 main cac51a07516cd2e36b3bf4cc45c9a17fad050002를 푸시했고 architecture.json을 해당 SHA로 연결했다. 위의 초기 구현 설명/미게시 메모는 당시 이력이며, 현재 구현·검증은 reports/_LATEST.md를 따른다. 과거 DB snapshot은 작성 당시 기준 SHA를 보존한다.

2026-09-27 개발 변경: 원본 main working-tree에 ADR-REVIEW-005 및 static-1.1.0 범위 문서를 추가했다. 아직 미커밋이므로 architecture.json은 마지막 게시 SHA를 유지한다. 새 계약의 설계와 검증은 이번 프로젝트 Report에 기록하며 다음 게시 때 원본을 먼저 게시하고 revision을 연결해야 한다.

2026-09-27 배포 전 게시: 원본 main c9275e62bb0efba3e42910e3dbcfe3b77f21409b를 푸시했고 architecture.json을 연결했다. ADR-REVIEW-005·ADR-DEPLOY-002와29규칙 계약을 포함한다. 위 미게시 메모는 당시 이력이다.
