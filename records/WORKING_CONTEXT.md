# 현재 개발 상태

최신 배포 작업은 [자동 배포 구현·초기 설정 기록](2026-09-30_automatic-deployment.md)을 참조한다. private GHCR→OIDC/SSM→EC2 및 Vercel CI/CD 코드를 준비했으며 최초 외부 권한/비밀 연결과 실제 main 배포는 미완료다. Vercel Prism은 팀 이름(prism-2139)이고 프로젝트 생성은 아직 안 되어 있다. 현재 정책은 ADR-DEPLOY-006이며 AI 활성화 정책은 별도다.

2026-09-30 인프라 준비 상태는 [EC2 직접 접속 기록](2026-09-30_ec2-access-report.md)을 참조한다. 애플리케이션 검증 기준은 [배포 전 완성도 Gate](2026-09-29_predeployment-hardening.md)와 [EC2 실행 안내](2026-09-29_ec2-release-runbook.md)다. 이전 실제 문서/PR 검증은 [최종 검증 보고서](2026-09-29_final-validation-report.md)에 보존한다. 설계는 ADR-REVIEW-012~014를 따른다.

- architecture main, backend/frontend dev. 문서는 architecture에만, 코드/테스트/평가 도구는 구현 저장소에 둔다. 최종 Git/CI 상태는 최신 보고서의 Git 완료 절을 참조한다.
- 2026-09-30 사용자 생성 EC2는 서울/t3.small/Ubuntu 24.04.4, RDS는 PostgreSQL 17.11/db.t4g.micro다. 사용자가 초기화 SQL을 실행한 뒤 에이전트가 prism_app→prism DB 로그인을 직접 확인했다. verify-full/TLS 1.3, schema CREATE 허용, 관리자 역할 속성·PUBLIC CONNECT 해제, 앱 테이블 0개 확인. 별도 테스트 PostgreSQL 17의 권한/비밀번호/기존 객체 보호 검사도 통과했다. 운영 migration은 아직 하지 않았다.
- Docker Engine 29.8.1/Compose 5.5.1 설치·hello-world 실행, EC2 Compose 합성 설정 검사 통과. CI 통과 backend26646ff를 `/opt/prism/releases/26646ff080c165f041a7805f077b7cae8e9299e0`에 준비했다. `/home/ubuntu/.config/prism/`의 database.env와 runtime.env.pending은 700/600 권한으로 비밀값을 서버에만 보관한다. 실제 앱 실행은 아직 하지 않았다. ADR-DEPLOY-005와 소유 문서에 RDS/초기 자원·비밀 주입 결정을 기록했다.
- 사용자 확인: 운영 GitHub OAuth/App 미설정. EC2 탄력적 IP 52.79.50.98 연결 완료; 기존 SSH 호스트 키를 대조해 새 주소 로그인과 private IP 172.31.3.188을 확인했다. RDS 주소 3.35.150.103은 EC2로 재할당하지 않는다. 현재 로컬 DNS 조회에서는 프론트/API 도메인 모두 이름 없음이다. 다음은 DNS/HTTPS, 운영 키, registry/digest, 백업 복원 후 migration/API 실행이다. 전용 SSH 키 사본은 매 호출 후 정리하며 키/DB 비밀번호를 채팅이나 Git으로 전달하지 않는다. 원본 키 경로는 사용자의 Downloads/prism-key.pem이며 Windows의 넓은 ACL 때문에 임시 사본의 권한 제한이 필요하다.
- 2026-09-29 프론트 `https://prismquest.p-e.kr`, 백엔드 `https://api-prismquest.p-e.kr` 확정. 두 주소의 DNS/Vercel/TLS/운영 앱 등록은 아직 미수행/미검증이며 로컬 실행 설정은 유지한다. 주소 지정은 기존 동일 출처 정책의 구현 값이므로 별도 ADR을 만들지 않았고, 이후 DB 배치·EC2 초기 사양은 ADR-DEPLOY-005로 구체화했다.
- 코드 리뷰/취약점/팀 규칙 분리, 업로드 문서 버전/권한/검색/인용, 결정적 규칙 구현. DB0009·업무19테이블·물리FK0. 이번 DDL 변경 없음.
- 실제 챱챱 코드 컨벤션 버전1을 팀 비공개 공간에 등록했다. 원문14,387바이트/19섹션 일치. 실제 검색8섹션/제외11,백엔드 구조와 역할·기본 작성 규칙 포함. 자동 검사 규칙은 아직 설정하지 않았다.
- 실제 PR #49 고정562e528에서 CODE/SECURITY/STANDARDS 모두 완료. 제안/질문은 각각0/0,0/0,0/1. 문서 버전/원문·사이트 내 코드 보기·검증용 개인 메모 저장 확인. 원본 문서/조직 코드/화면/리뷰 본문은 공개Git에 넣지 않았다.
- V5/ADR014: invalid 초안 독립 재검토, 새 발견, 제한 문맥 보충, 좁은 정적 계산·단언 불일치 서버 설명, 수정안 반례 표시/차단. 실제 코드를 실행하지 않는다. 서버 설명을 AI 의미 정답으로 집계하지 않는다.
- H4 하네스 rh1-ee9b9e100eba9cad: 경로 수정안의 정상 경계 보존·중첩 복사 구분·불필요한 질문 독립 재검토 보강. 86평가/78고유사례 형식86/86·정상오탐0·대표줄불일치3·근거줄누락0. 집중12응답 의미 검수; 3건은 올바른 쓰기 줄과 복사 근거를 제시했다. 원 지표 보존. 독립holdout/범용 미탐0/전체 설명 정확도 PASS를 주장하지 않는다.
- 리뷰 이력의 이전 코드 선택, 인용 지연 응답 혼합, 문서 편집 후 섹션 연결 오류, Markdown 중첩 fence 오인을 수정했다. 새 버전 저장에 적용하며 기존 문서 버전은 재색인하지 않았다.
- Linux backend474테스트, frontend136테스트/타입/빌드, backend mypy140·Ruff/format184 통과. Windows pytest 미사용. 5화면×5너비 및 실제 OAuth 보호 경로 복귀 확인.
- 이번 보수516호출(전부 합성), 캠페인3,464/5,000·잔여1,536. 과거1,563 포함5,027/6,563. 공통 usage.json이 원장. 평가 종료.
- EC2 Compose·설정 preflight·실행/복구 안내 추가. 제한 컨테이너/합성 백업 복구 검증 통과. 운영 주소/TLS/DB/키/백업·알림·실배포 Gate D3는 BLOCKED이며 실제 배포하지 않았다.
- Flash·ChatDeepSeek·추론OFF·2,000토큰/회·최대2회/요청·팀30회/일·동시1개 유지. Pro 교체 보류. OSV는 어댑터만 있고 자동 전송 없음.
- 다음: 독립적인 실제 PR 정답 라벨, 큰 PR/호출 경로/수정안의 기존 동작 보존, 팀 문서 경로·필수 섹션 설정. EC2 운영 주소/TLS/키/DB·백업/모니터링·실배포는 별도. 사용자 원본 하네스 동기화도 미진행.
