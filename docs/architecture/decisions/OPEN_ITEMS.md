# 남은 결정과 안전한 기본 동작

> ID: `OPEN-ITEMS` · 소유: `architecture-decisions` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 외부 서비스 선택·공개 전 준비 상태를 확인할 때

설계를 시작할 수 없는 상태는 아니다. 아래 외부 선택을 임의로 확정하지 않고, 미정 기능은 안전하게 비활성화한 채 독립 영역을 구현한다.

| ID | 아직 정하지 않은 것 | 그전의 동작 | 결정 시점 |
|---|---|---|---|
| OPEN-01 | RDS PostgreSQL 17.11/서울·전용 DB·migration 0009 완료; 빈 DB 및 테이블 20개 백업 복원 PASS. 정기 백업/별도 보관·재해 복구 정책은 미확정 | root 전용 논리 백업 보관, 새 migration은 unchanged 정책으로 차단 | 데이터 운영 확대 전 |
| OPEN-02 | 공개 운영 금액 예산/알림 | 로컬 deepseek-flash 실제 검증 완료. 팀 UTC 일30회·호출1회·출력2000token 제한; 금액 상한은 미보장 | 외부 공개 전 |
| OPEN-03 | 해결: 로컬 GitHub OAuth/App 등록 및 개인·조직 저장소 연결 | 실제 로그인·PR 동기화 확인. 공개 Webhook 실전송은 OPEN-04 이후 별도 | 2026-09-26 로컬 검증 |
| OPEN-04 | 프론트/API DNS·Caddy HTTPS·두 ready=200·실제 OAuth 로그인·GitHub ping=204 완료; 운영 PR 전체 흐름·두 계정 격리 E2E는 후속 | 로컬 기록을 운영으로 자동 이관하지 않는다. 운영 값은 DEPLOYMENT 참조 | 운영 사용 흐름 검증 시 |
| OPEN-05 | Rule별 실제 정확도·문법 버전·AWS 실행 환경 피크 자원 | 정의는 후보, fixture 통과 전 해당 Rule 비활성 | 기능 완료 선언 전 |
| OPEN-06 | 외부 공개 시점·상용화 여부·기업 코드 처리 계약·영구 삭제 운영 | 본인 Organization과 개인 프로젝트에서 먼저 사용 | 외부 사용자를 받기 전 |
| OPEN-07 | 해결: 정식 프로젝트명 PRism(프리즘), 폴더명 prism | 명칭 확정 | 2026-09-25 결정 |
| OPEN-08 | 프론트·백엔드 공개 GHCR/OIDC/SSM main 자동배포 실제 성공; 운영 알림/예산·상한 부하·호스트 재시작/유실 복구는 미완료 | Vercel/PAT 없이 운영. 새 스키마 이행과 root 배포 도구 업데이트는 별도 준비 | 운영 안정화 단계 |

LLM Provider는 사용자 선택에 따라 DeepSeek로 확정했다. 운영 모델은 deepseek-flash이며 팀 일30회 제한을 적용했다. 금액 예산은 미정이고 이번 배포 검증에서 유료 추론은 실행하지 않았다. 사용자 승인으로 두 도메인 배포·운영 OAuth·ping 웹훅·자동배포를 완료했다. 분석 품질·문법 버전·AWS 자원 한도와 운영 PR 전체 흐름은 별도 증거로 판단한다. 초기 사용은 본인 Organization과 개인 프로젝트로 한정한다. 인프라 배포 성공을 일반 사용자 대상의 전체 품질 보장으로 확대하지 않는다.

## 범위 잠금

MVP: 로그인/팀 권한, GitHub 연결/PR 이력, 영속 Job, 네 언어 정적 분석, 선택적 AI 설명, 결과 화면, 선택한 배포 구성의 한계 표시.

확장 후보: 상시 worker/강한 sandbox, RAG 팀 규칙 검색, 전체 저장소 dependency graph, GitHub Checks/리뷰 게시, Vue SFC 추출, 세밀한 저장소별 권한, rule suppression UI.

제외 범위: Go, 자동 코드 실행/빌드/설치, 자동 머지/자동 수정, 회사 보안 인증·완전한 취약점 탐지 보장, 모든 과거 PR commit의 완전 복원, 처음부터 MSA/Kafka/Kubernetes.
