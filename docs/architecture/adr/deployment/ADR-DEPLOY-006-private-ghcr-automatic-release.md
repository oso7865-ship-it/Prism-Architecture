# ADR-DEPLOY-006: 비공개 GHCR와 GitHub Actions 자동 배포

> ID: `ADR-DEPLOY-006` · 소유: `DEPLOY` · 기준: `2026-09-30`
> 읽는 때: main 배포·이미지 공개 범위·AWS 배포 권한·실패 복구를 변경할 때

- 상태: `SUPERSEDED`
- 기록일: `2026-09-30`
- 근거: 사용자가 자동 배포와 비공개 GHCR 이미지·읽기 토큰 방식을 선택했다.
- 대체하는 ADR: [ADR-DEPLOY-004](ADR-DEPLOY-004-ec2-runtime.md).
- 대체한 ADR: [ADR-DEPLOY-008](ADR-DEPLOY-008-frontend-on-ec2.md). Vercel 관련 결정만 변경하며 백엔드 private GHCR/OIDC/SSM 계약은 유지한다.

## 배경과 결정 범위

EC2와 RDS를 준비한 후 매번 SSH로 배포하는 대신 main 병합 후 자동 배포를 요청했다. DEPLOY-004의 자동 배포 기본 OFF를 최초 환경 준비 후 자동 실행으로 변경한다. EC2 Docker/FastAPI·단일 worker·embedded dispatcher, Vue/Vercel과 같은 origin 프록시, Secure 쿠키·CSRF·API no-store, PostgreSQL TLS, 비루트 제한 컨테이너, 개발/운영 비밀 분리, 원문 비저장 계약은 유지한다. AI 활성화는 별도 운영 설정이며 CI/CD 선택으로 켜지지 않는다. RDS와 초기 자원·앱 DB 계정은 [DEPLOY-005](ADR-DEPLOY-005-rds-initial-runtime.md)를 유지한다.

## 결정

백엔드는 기존 CI 통과 커밋을 main 전용 publish job에서 이미지로 만들고 그 결과물에 컨테이너 검증을 실행한 뒤 같은 이미지를 private GHCR에 게시한다. 공개 소스 저장소의 Actions artifact로 이미지 tar를 전달하지 않는다. 태그는 commit SHA, 배포 식별자는 sha256 digest다. 게시 전후 패키지 공개 범위를 검사하고 EC2에서도 OCI source/revision label을 대조한다. EC2는 read:packages 전용 classic PAT로 이미지를 받고 토큰을 root 전용 Docker 설정에 보관한다. GitHub Actions는 해당 저장소 GITHUB_TOKEN으로 게시하며 EC2 다운로드 토큰을 받지 않는다.

Actions→AWS는 장기 AWS 키 대신 OIDC를 사용한다. 실제 OIDC aud/sub를 먼저 확인해 특정 repository production 환경만 허용한다. 해당 GitHub Environment의 배포 브랜치는 main으로 제한한다. AWS 권한은 지정 EC2와 PrismDeployBackend SSM 문서의 SendCommand, 결과 조회로 한정한다. 문서 버전1과 ENV_VAR 입력 전달, digest/SHA/번호 패턴 검사로 임의 shell 인자를 차단한다.

운영 작업은 main push 또는 main의 수동 재실행에서만 수행한다. CI 통과와 최신 main SHA 확인, Actions concurrency 및 호스트 flock, 단조 증가 실행 번호로 역순 배포를 제한한다. EC2는 root 소유 `/opt/prism-deploy`의 도구/Compose와 `/etc/prism/deploy.json`을 사용한다. 활성화되지 않은 설정, `.pending` 환경 파일, 잘못된 권한은 실패한다. 호스트 도구의 변경은 별도 초기 설치/업데이트 단계이며 이미지 배포가 root 도구를 교체하지 않는다.

배포 순서는 pull/provenance → preflight → DB revision → migration → 컨테이너 교체 → 내부 및 공개 HTTPS ready 검사다. SSM 명령 접수만으로 성공 처리하지 않고 실제 종료 상태를 기다린다. DB 변경은 backup_restore_verified_at와 upgrade 정책을 요구한다. migration 실패 시 교체를 중단하며 DB downgrade는 없다. 새 버전 실패 시 현재 DB revision이 배포 전과 같고 이전 이미지가 그 revision을 목표로 할 때만 이전 이미지로 복구한다. 복구 성공도 해당 배포는 실패로 표시한다.

프론트는 별도 저장소 CI 통과 후 Vercel CLI의 production 설정/build와 prebuilt 배포를 사용한다. Vercel 기본 Git 자동 배포는 중복 활성화하지 않는다. 공개 로그인 HTML과 API proxy ready를 확인한다. 프론트 검사 실패는 배포 실패로 표시하며 이 버전에는 Vercel 자동 rollback을 포함하지 않는다.

## 대안과 손실

ECR 대신 사용자 선택인 GHCR를 사용한다. private pull 토큰의 만료/회수 대응은 남는다. SSH 배포 대신 SSM으로 Actions에 SSH 키를 저장하지 않지만 IAM/OIDC·SSM 에이전트 초기 준비가 필요하다. EC2 빌드 대신 CI에서 검증한 release 이미지를 배포하므로 작은 EC2의 빌드 부담을 피한다. 공개 artifact를 통한 우회 다운로드를 막기 위해 CI와 publish에서 빌드/컨테이너 검증을 각각 수행하므로 시간이 추가된다. 단일 컨테이너 교체는 무중단을 보장하지 않으며 schema 변경 후 실패는 운영자 대응이 필요하다. 이미지/디스크 용량을 관측해야 한다.

## 영향과 한계

운영 main 변경은 초기 설정 완료 후 자동 실행된다. 따라서 main 보호와 CI 통과가 배포 경계다. read 토큰 만료, 단일 EC2 장애, 실제 부하, backup 복원 결과는 이 구현의 단위 테스트만으로 보장하지 않는다. migration으로 revision이 달라진 경우에는 자동 이미지 복구를 보수적으로 차단한다.

## 소유 문서와 검증

로컬 Linux에서 배포 성공·실패·복구·입력 거부·실제 프로세스 잠금과 SSM 응답·GHCR 공개 범위를 검사했다. Actions 문법, 프론트 빌드/준비 상태 검사와 문서 무결성을 별도로 검증한다. 이는 실제 AWS/Vercel 배포 성공을 대신하지 않는다. 외부 권한·비밀·DNS/TLS·운영 GitHub 앱·백업 복원과 main 최초 실배포는 초기 설정 Gate다. Vercel의 Prism은 조회 시 팀(`prism-2139`)이며 프로젝트는 아직 없다.

현재 계약은 [배포 설계](../../operations/DEPLOYMENT.md), 상세 절차·결과는 [자동 배포 기록](../../../../records/2026-09-30_automatic-deployment.md)에 둔다.
