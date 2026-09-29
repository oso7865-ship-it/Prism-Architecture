# EC2 백엔드 출시와 전체 자동배포 연결

## 최종 결과 — 2026-09-30 05:14 KST

프론트·백엔드 운영 배포와 main 자동배포가 모두 성공했다. 공개 주소는 [PRism](https://prismquest.p-e.kr), 직접 API는 [API 준비 상태](https://api-prismquest.p-e.kr/health/ready)다. 실제 GitHub 로그인으로 운영 /app 진입과 세션 생성을 확인했다. 운영 DB는 새로 시작했으며 로컬 팀·저장소·리뷰 이력을 이관하지 않았다.

| Gate | 결과 | 실제 근거와 한계 |
|---|---|---|
| 백엔드 코드/이미지/배포 | PASS | [Actions 36623153663](https://github.com/oso7865-ship-it/Prism-Backend/actions/runs/36623153663), validate/publish/deploy 모두 success |
| 프론트 코드/이미지/배포 | PASS | [Actions 36623167334](https://github.com/oso7865-ship-it/Prism-Frontend/actions/runs/36623167334), validate/publish/deploy 모두 success |
| EC2 배포 권한 | PASS | 사용자 승인 후 OIDC provider와 두 전용 IAM 역할, 고정 SSM 문서 생성. 두 실제 Actions 실행으로 역할 인수와 SSM 완료 확인 |
| 이미지 다운로드 | PASS | 정확한 공개 manifest digest를 익명 검증. EC2 root Docker GHCR 인증 제거 확인 |
| DB/migration | PASS | head 0009, 컨테이너 healthy, 두 도메인 ready=200 |
| 논리 백업·복원 | PASS | 빈 DB 및 migration 이후 테이블 20개를 각각 별도 임시 PostgreSQL 17에 복원. 호스트 유실 복구 시험은 아님 |
| 운영 OAuth | PASS | GitHub App의 동일 출처 로그인 callback 누락을 추가 후 실제 /app 로그인 성공 |
| 실제 GitHub 웹훅 | PASS | 기존 ping만 재전송해 204 수신. 서명·TLS 검사 유지. 실제 PR 이벤트 분석 완료 증거는 아님 |
| 공개 HTTP 경계 | PASS | TLS/ready/SPA/자원 해시/캐시/비공개 파일/CSRF/쿠키/비활성 API 문서/HTTP 전환 22개 검사 |
| 운영 PR·AI 전체 흐름 | 미수행 | 이번 배포 작업에서 실제 운영 PR 동기화→분석→유료 리뷰까지 실행하지 않음 |
| 운영 부하·복구·비용 | 후속 | 상한 입력/두 계정 운영 E2E/재부팅·lease 복구/정기 백업·별도 보관/알림·예산은 별도 |

### 최종 배포 식별자

- backend revision: 7209c42d5d9c7b98d0eb9ac05e3e18ca3c38035c, sequence 28.
- backend image: ghcr.io/oso7865-ship-it/prism-backend@sha256:e4666aaf4d3b8916f5f12be4e010f995e87623e34cc25087cdb4fade2f1a65be.
- frontend revision: d88cb69d2ce68b8697079c461e1607589d6bb707, sequence 22.
- frontend image: ghcr.io/oso7865-ship-it/prism-frontend@sha256:ca613a05d3d072eb5b72ea465d5e0c6f1c93a0674be71f75d544577b02732b41.
- backend/frontend dev와 main에 검증 변경을 반영했다. 두 코드 작업 트리는 깨끗하며 보고 문서는 이 아키텍처 저장소에만 추가한다.

### 실제 연결과 수정

사용자가 제한된 자동배포 권한 연결을 승인했다. AWS 계정 152025328159의 OIDC provider는 token.actions.githubusercontent.com, audience는 sts.amazonaws.com이다. prism-backend-deploy/prism-frontend-deploy 역할은 각각 다음 실제 subject만 신뢰한다.

```text
repo:oso7865-ship-it@269069314/Prism-Backend@1386116890:environment:production
repo:oso7865-ship-it@269069314/Prism-Frontend@1386116977:environment:production
```

GitHub의 각 production 환경은 main만 허용한다. 역할은 EC2 i-02d892cf8019b2d7a와 해당 PrismDeployBackend/PrismDeployFrontend 문서만 SendCommand할 수 있다. GetCommandInvocation은 결과 조회에 사용하며 임의 shell 명령 인자를 받지 않는다. EC2 기존 prism-ec2-role은 유지했다. Actions 변수 AWS_DEPLOY_ROLE_ARN/EC2_INSTANCE_ID를 연결했고 장기 AWS 키는 추가하지 않았다.

배포 설정 유무 검사에서 `test A && test B`는 첫 명령 실패가 set -e의 중단으로 이어지지 않을 수 있어 각각 독립된 test 줄로 수정했다. 최종 두 커밋은 이 수정까지 포함한다. backend root 배포 설정은 enabled=true, migration_policy=unchanged다. 새로운 DB migration은 별도 백업/복원·이행 승인 없이는 자동 실행하지 않는다. root 배포 도구와 Caddy 설정 자체는 별도 호스트 설치 단계로 관리한다.

GitHub App PRismRequest의 homepage를 운영 주소로 변경하고 https://prismquest.p-e.kr/api/v1/auth/github/callback을 추가했다. 기존 github-app/callback과 로컬 callback은 유지하며 wildcard를 켜지 않았다. Webhook Active를 활성화하고 기존 URL https://api-prismquest.p-e.kr/webhooks/github, 기존 secret, SSL verification을 유지했다. 배포 전 ping은 502였고 같은 ping의 재전송은 2026-09-29T20:11:21.605Z에 204였다. GitHub REST 및 화면의 성공 표시를 모두 확인했다. PR/설치 이벤트를 재실행하지 않았다.

### 백업과 공개 검증

초기 migration 후 백업은 /var/lib/prism-backups/after-first-migration-20260929T200503Z.dump다. SHA256 d542cb3b29df6ea4d1037d7e11d6e57a73767f4052e1279f757cf4c74b5e317b, 복원 검증 시각 2026-09-29T20:05:08.857612+00:00, 원본과 복원 public 테이블 수는 모두 20이다. 격리 임시 DB에 pg_restore --exit-on-error를 적용했고 운영 DB를 복원으로 덮어쓰지 않았다. 백업은 root600/디렉터리700이며 현재 EC2 내부 보관이다. RDS 정기 백업 보존·오프호스트 사본·목표 복구 시간은 이번 확인 범위 밖이다.

최종 공개 검증은 2026-09-29T20:13:32.692982+00:00에 PASS였다. 최초 해시 검사는 이전 로컬 dist와 CI 산출물이 달라 실패했다. 비교 대상을 실제 현재 CI 이미지에서 추출해 배포한 파일 manifest로 바로잡고 모든 공개 파일의 SHA256을 재확인했다. 이 차이만으로 배포 파일 변조를 주장하지 않는다. CI 배포 도구도 전환 직후 공개 자원 해시와 API를 검증했다.

인증 시작은 정확한 GitHub/운영 callback으로 이동하며 binding 쿠키는 Secure/HttpOnly/SameSite=Lax/host-only다. refresh는 CSRF 없는 요청 403, 허용 Origin/헤더지만 인증 쿠키 없는 요청 401이다. /.env, /.git/config, 소스맵, 없는 자원은 404이며 API 오류가 SPA 200으로 숨겨지지 않는다. 직접 API의 /docs,/redoc,/openapi.json은 404다. 두 TLS 인증서 신뢰 검증과 HTTP→HTTPS 308을 통과했다. 쿠키·OAuth state·토큰·비밀값은 증거 파일에 저장하지 않았다.

작업 로컬 증거는 저장소 밖 audit-artifacts/ec2-bootstrap-20260930의 production-verification.json, production-host-verification.json, production-login-success.png, webhook-success.png, aws-roles-ready.png다. Windows 네이티브 pytest는 실행하지 않았으며 Python 배포 테스트는 Linux 환경과 원격 CI에서 수행했다. 이번 배포 작업의 유료 모델 추론 호출은 0회다. 기존 PAT는 EC2에서 제거했으나 GitHub 자체의 토큰 폐기를 수행했다고 주장하지 않는다.

문서 무결성 검사 PASS: Markdown 126개, ID 90개, 링크 570개, ADR 38개. 기존 보존 기록 490개와 평가 결과 원본 7개의 해시 검사도 PASS다. 길이 안내 7개는 비차단이며 이번 최종 이력 보고서 1개가 포함된다. 문서 검사 성공을 제품 기능·성능 검증으로 해석하지 않는다. 명령과 Git 작업은 각 저장소 cwd를 지정해 실행했고 최종 코드 원격 CI·실제 배포 결과를 각각 확인했다. 삭제·강제 push·운영 DB 자동 downgrade는 수행하지 않았다.

문서 선택 helper가 프론트 ADR 읽기 목록의 다른 영역(DEPLOY) ADR 직접 포함을 거부했다. 영역별 읽기 경계를 유지하도록 두 배포 ADR을 adr-deploy 작업에만 두고, 프론트 소유 문서의 링크로 연결했다. validator를 느슨하게 변경하지 않고 같은 helper 검사를 재실행해 92개 task/mode 조합·ADR 경로 38개·잘못된 경로 4개 검사가 PASS였다.

이하 내용은 최초 설계와 진행 이력이다. 현재 공개 이미지와 완료 상태는 위 최종 결과를 따른다.

## 작업 계약

사용자는 프론트 초기 배포 후 백엔드 앱 배포·로그인 확인·자동배포 연결을 모두 진행하도록 승인했다. 기존 Git 반영/병합/자동배포 요청을 이어서 구현 코드와 필요한 설정을 검증 후 main에 반영한다. 문서는 아키텍처 저장소에만 둔다. Terminal Ops/Git Workflow/Security Gate/DB Gate와 CORE/DEPLOYMENT/FRONTEND/ADR-DEPLOY-008을 적용한다. Windows 네이티브 pytest는 실행하지 않는다.

## 구현 전 설계

1. 백엔드 dev의 검증된 변경을 원격 main에 fast-forward하여 private GHCR 이미지를 게시한다. 정확한 digest를 배포한다. 기존 main이 dev의 조상임을 확인했으며 강제 push는 하지 않는다.
2. 사용자 생성 read:packages 전용 classic PAT를 EC2 root Docker 인증에만 입력한다. 광범위한 로컬 gh 인증을 EC2에 복사하지 않는다. 토큰은 명령 인자·로그·Git에 넣지 않는다.
3. 현재 RDS는 빈 앱 DB다. 초기 migration 전에 PostgreSQL 17 도구로 논리 백업을 만들고 격리된 임시 PostgreSQL에 복원하여 스키마/테이블 상태를 확인한다. 운영 DB에서 테스트 데이터를 생성하지 않는다. 백업과 검증 기록은 root 전용 경로에 보관한다. 실패 시 migration/앱 교체를 중단하고 DB 자동 downgrade는 하지 않는다.
4. 백엔드 preflight·migration·앱 시작·내부 및 두 도메인의 API health를 확인한다. 로그인은 실제 공개 프론트 origin과 GitHub callback을 통해 확인하며 사용자 로그인/동의가 필요한 지점은 맡긴다.
5. 프론트는 CI가 빌드한 dist만 담은 실행하지 않는 scratch OCI 이미지를 private GHCR에 게시한다. digest/source/revision을 검증한 서버 도구가 정적 파일만 추출하고 버전 디렉터리/current 링크를 전환한다. API/HTML 검사가 실패하면 이전 링크로 복구하고 배포 자체는 실패로 기록한다. 상시 Node/프론트 컨테이너는 추가하지 않는다.
6. 두 Actions 저장소는 각각의 production 환경·실측 OIDC sub를 신뢰하는 최소 IAM 역할을 쓴다. 지정 EC2와 고정 SSM 문서만 실행한다. EC2는 SSM 관리 노드 역할이 필요하다. 프론트와 백엔드 호스트 잠금/배포 번호를 각각 유지한다. 신규 IAM 권한은 적용 대상을 구체화한 뒤 확인한다.
7. GitHub production 환경 main 제한, 실제 CI/게시/SSM 완료, public page/API, 토큰·설정 누출 방지를 확인한다. 전체 완료 여부는 각각의 실제 결과로 판단한다.

## 시작 상태

- backend dev cbad2af / 원격 main a7b9792, dev가 main의 후속이다. frontend dev e6fdbd0은 원격 main의 후속이다.
- EC2 Caddy/프론트/TLS 완료, 백엔드 컨테이너 없음, /etc/prism/deploy.json enabled=false, GHCR 인증 없음.
- AWS CLI 로컬/서버 준비 없음, SSM agent active이며 관리 노드 등록/역할 연결은 확인 전이다.
- 사용자에게 GHCR 전용 토큰 생성과 로컬 파일 저장을 요청했다. 토큰 생성 화면은 열었고 최종 생성은 사용자가 수행한다.

## 진행 결과

### 최신 결정

사용자는 공개 저장소의 포트폴리오 목적을 설명하고 GHCR도 공개로 진행하도록 명시 승인했다. 아래 비공개 전환 시도는 당시 선택에 따른 중간 이력이며 폐기했다. ADR-DEPLOY-009가 현행 기준이다. EC2 root Docker의 GHCR 자격증명은 logout으로 제거했다. 사용자 PAT를 다른 곳에 복사하지 않았으며 더 이상 다운로드에 쓰지 않는다. 기존 공개 이미지는 삭제하지 않는다.

- backend c7f90e5 / frontend b44dbb8을 dev와 main에 반영했다. 프론트 정적 OCI는 dist만 빌드 context로 사용하며 컨테이너는 실행하지 않는다.
- backend 배포·공개 manifest 검사 21개, frontend 배포·복구·경로 안전성·공개 검사 18개 Linux 테스트 통과. 프론트 타입/빌드/136개 기능 테스트, Node 배포/저장소 5개 테스트, actionlint 통과. 새로운 런타임 문서는 구현 저장소에 넣지 않았다.
- PostgreSQL 17 이미지(digest 고정) 도구로 빈 RDS prism을 백업하고 격리된 임시 PostgreSQL 17에 pg_restore를 실행했다. public 테이블 0개가 동일함을 확인했다. 운영 DB 쓰기는 없으며 향후 데이터가 생긴 뒤의 전체 재해 복구 검증을 대신하지 않는다. 실제 이미지 태그는 postgres:17이고 서버 버전의 상세 문자열은 이번 출력에 기록하지 않았다.
- 백업 /var/lib/prism-backups/before-first-migration-20260929T195056Z.dump, SHA256 4414950e17d1cce4fcd456c52008d59056ec67d3448e668013d90b66daa0dc6a, 복원 검증 2026-09-29T19:51:09.722181+00:00.
- frontend OIDC 실제 sub도 repo:oso7865-ship-it@269069314/Prism-Frontend@1386116977:environment:production으로 확인했다. 두 IAM 역할·SSM 문서의 구체적 정책을 준비했다. 브라우저로 신규 보안 권한을 부여하기 직전 확인을 요청한다.

### 중간 확인 이력

- 사용자 제공 classic PAT의 계정과 read:packages 단독 권한을 검증하고 EC2 /root/.docker/config.json(root600)에 등록했다. 비밀값은 표준입력으로만 전달했고 기록에는 넣지 않았다.
- backend main cbad2af 원격 CI의 validate는 성공했으나 publish 후 비공개 검사에서 실패했다. 실제 Packages API에서 기존 prism-backend의 visibility=public, 익명 registry 접근 200을 확인했다. 이 이미지는 운영 배포에 사용하지 않는다. 공개 전환 주체/시점은 확인하지 않았으며 추정하지 않는다.
- GitHub는 공개 패키지의 비공개 전환을 허용하지 않는다. 새 prism-backend-production 저장소를 사용하고, REST의 404 예외가 공개 이미지를 통과시키지 않도록 게시 전 익명 registry 접근도 차단한다. 기존 공개 패키지는 삭제하지 않았고 별도 확인이 필요하다. CI 이미지에는 운영 env가 입력되지 않는 구조다.
- 배포·SSM·비공개 검사 Linux 회귀 테스트 23개 PASS, Ruff PASS. 저장소 검사 명령의 최초 CWD 오류는 올바른 저장소에서 다시 실행한다.
- backend OIDC 실제 sub는 repo:oso7865-ship-it@269069314/Prism-Backend@1386116890:environment:production이다. AWS EC2는 기존 prism-ec2-role을 사용하고 SSM Online임을 확인했다. OIDC provider는 아직 없다.
- 프론트 자동배포와 운영 DB 백업/복원, 앱 실행, 로그인 검증, 새 IAM 역할은 진행 중이다.
