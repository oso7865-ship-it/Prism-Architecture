# 남은 결정과 안전한 기본 동작

> ID: `OPEN-ITEMS` · 소유: `architecture-decisions` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 외부 서비스 선택·공개 전 준비 상태를 확인할 때

설계를 시작할 수 없는 상태는 아니다. 아래 외부 선택을 임의로 확정하지 않고, 미정 기능은 안전하게 비활성화한 채 독립 영역을 구현한다.

| ID | 아직 정하지 않은 것 | 그전의 동작 | 결정 시점 |
|---|---|---|---|
| OPEN-01 | 장기 PostgreSQL 호스팅/리전/백업 | 로컬 PostgreSQL + fixture; 무료 Render DB의 30일 제한을 장기 보존으로 오인하지 않음 | 최초 지속 배포 전 |
| OPEN-02 | 공개 운영 금액 예산/알림 | 로컬 deepseek-flash 실제 검증 완료. 팀 UTC 일5회·호출1회·출력2000token 제한; 금액 상한은 미보장 | 외부 공개 전 |
| OPEN-03 | 해결: 로컬 GitHub OAuth/App 등록 및 개인·조직 저장소 연결 | 실제 로그인·PR 동기화 확인. 공개 Webhook 실전송은 OPEN-04 이후 별도 | 2026-09-26 로컬 검증 |
| OPEN-04 | 공개 도메인·Vercel rewrite·Callback 구성 | 로컬 개발 origin만 allowlist | 로그인 배포 테스트 전 |
| OPEN-05 | Rule별 실제 정확도·문법 버전·Render 피크 자원 | 정의는 후보, fixture 통과 전 해당 Rule 비활성 | 기능 완료 선언 전 |
| OPEN-06 | 외부 공개 시점·상용화 여부·기업 코드 처리 계약·영구 삭제 운영 | 본인 Organization과 개인 프로젝트에서 먼저 사용 | 외부 사용자를 받기 전 |
| OPEN-07 | 해결: 정식 프로젝트명 PRism(프리즘), 폴더명 prism | 명칭 확정 | 2026-09-25 결정 |

LLM Provider는 사용자 선택에 따라 DeepSeek로 확정했다. 로컬 모델은 deepseek-flash로 확인했고 ADR-REVIEW-003의 호출/출력 한도를 적용했다. 공개 운영 금액 예산은 미정이다. 실제 GitHub OAuth/App 연동과 실제 주소를 사용하는 배포를 계획하되 로컬 등록·권한 설정은 완료했고 공개 도메인 선택 및 배포 연동 검증은 남아 있다. 분석 품질·문법 버전·자원 한도는 구현 후 검증하여 결정한다. 다른 사용자도 가입하고 저장소를 연결할 수 있는 구조로 개발하며, 초기 사용은 본인 Organization과 개인 프로젝트로 한정하고 즉시 공개 출시하지 않는다. 유료 외부 서비스·결제·계정 연결·실제 배포를 이 문서 생성 요청의 일부로 실행하지 않는다.

## 범위 잠금

MVP: 로그인/팀 권한, GitHub 연결/PR 이력, 영속 Job, 네 언어 정적 분석, 선택적 AI 설명, 결과 화면, 무료 데모 배포의 한계 표시.

확장 후보: 상시 worker/강한 sandbox, RAG 팀 규칙 검색, 전체 저장소 dependency graph, GitHub Checks/리뷰 게시, Vue SFC 추출, 세밀한 저장소별 권한, rule suppression UI.

제외 범위: Go, 자동 코드 실행/빌드/설치, 자동 머지/자동 수정, 회사 보안 인증·완전한 취약점 탐지 보장, 모든 과거 PR commit의 완전 복원, 처음부터 MSA/Kafka/Kubernetes.
