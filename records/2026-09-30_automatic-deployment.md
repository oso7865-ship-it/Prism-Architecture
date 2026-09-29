# GitHub Actions 자동 배포 구현 기록

> 작업 브랜치: backend/frontend dev, architecture main
> 상태: 로컬 구현·검증 및 EC2 도구 설치 완료; 외부 인증 연결·main 최초 배포 미완료
> 적용 스킬: terminal-ops
> 범위: L / 실행 환경·배포 권한·DB 변경 순서

## 0. 작업 계약

사용자 요청은 main 병합 후 수동 서버 접속 없이 자동 배포다. GHCR 이미지는 비공개다. 사용자가 Vercel 프로젝트 이름을 Prism이라고 알려줬으나 실제 콘솔 확인 결과 Prism은 팀(prism-2139)이며 프로젝트 목록은 비어 있다. 변경은 구현 저장소의 CI·배포 실행 코드·검증 코드와 아키텍처 저장소의 설계·기록이다. 실제 운영 DB 테스트, 개발용 키 복사, 이미지 공개 전환, 앱 기능/스키마 변경은 범위에서 제외한다.

확인한 기준: CORE, PACKAGE-RULES, CONVENTIONS, DEPLOYMENT, ADR-GUIDE, ADR-DEPLOY-004/005, GENERAL_HARNESS Quick Ref/GateGuard/Security Gate/DB Gate/Terminal Ops. 기존 문서는 구현 저장소에 추가 게시하지 않는다. Windows 네이티브 pytest를 실행하지 않고 배포 코드의 Linux 테스트와 프론트 Node 검증을 사용한다.

## 1. 구현 전 설계

1. push/pull_request의 기존 CI는 유지한다. 운영 배포는 push main의 같은 실행에서 검증을 통과한 커밋만 대상으로 한다. PR은 AWS 자격 증명·Vercel 토큰·이미지 게시 권한을 받지 않는다.
2. 백엔드는 CI 통과 커밋의 release 이미지를 main 전용 publish job에서 만들고 해당 이미지의 컨테이너 검증 후 같은 이미지를 private GHCR에 게시한다. 공개 소스 저장소의 artifact로 이미지 tar를 우회 다운로드할 수 없도록 artifact 전달은 사용하지 않는다. 소스/revision label과 sha256 digest를 확인해 EC2에 전달한다. latest 배포와 EC2 빌드는 하지 않는다.
3. Actions→AWS는 저장소 production 환경에 한정한 OIDC 역할, SSM은 지정한 prism 인스턴스와 배포 문서에만 한정한다. EC2에는 root 관리 배포 도구/Compose/설정과 비공개 GHCR read:packages 토큰을 준비한다. 사용자 runtime.env의 비밀과 GHCR 토큰은 SSM 명령/Actions 로그에 포함하지 않는다.
4. 호스트 배포는 잠금→설정/입력 검사→image pull/label 대조→운영 preflight→DB revision 확인→단일 migration→컨테이너 교체→내부/공개 준비 상태 검사다. root 관리 활성화 설정과 백업 복원 확인 없이는 처음 운영 DB를 변경하지 않는다.
5. DB migration 실패 시 교체를 중단한다. 새 이미지 상태 검사 실패 시 DB revision이 변경되지 않은 경우에만 이전 이미지로 자동 복구한다. DB downgrade는 하지 않는다. 배포 실패/복구 결과는 Actions의 성공으로 위장하지 않는다.
6. 프론트는 CI 이후 Vercel CLI로 production 환경을 준비하고 기존 rewrite 생성기를 사용한다. 테스트·타입 검사 이후 Vercel build --prod 결과물을 --prebuilt --prod로 게시한다. Git 자동 배포와 중복 활성화하지 않는다.
7. 운영 배포 job은 production concurrency/cancel-in-progress=false를 사용한다. 실제 서버에도 배타 잠금을 적용하며 이전 커밋이 늦게 배포되는 것을 방지한다. 최초 AWS/Vercel/GHCR 인증·HTTPS 준비 후 자동 배포를 활성화한다.

## 2. 사전 검수

Security Gate 설계 PASS: digest/commit/인스턴스 입력 제한, PR 배포 차단, OIDC trust/SSM 대상 최소 범위, 비밀의 서버 보관, 원격 출력 마스킹, 타임아웃·실패 중단을 구현 대상으로 고정했다. 실제 권한 연결은 아직 검증하지 않았다.

DB Gate 범위: 앱 스키마 변경은 없다. 배포 시 기존 Alembic migration만 실행하며 운영 백업/복원 준비 확인을 활성화 조건에 포함한다. 합성 테스트와 운영 DB를 분리한다. 첫 운영 migration과 공개 출시는 아직 실행하지 않는다.

## 3. 완료 체크리스트

- [x] 기존 CI·서버 구성·사용자 공개 범위 확인
- [x] 구현 전 설계·실패/복구 계약 작성
- [x] 배포 ADR·현재 소유 문서·결정 맵 동기화
- [x] backend CI→private GHCR→SSM workflow 구현
- [x] EC2 배포 실행기·설정·SSM/IAM 템플릿 구현
- [x] frontend CI→Vercel production workflow 구현
- [x] 성공/입력 거부/동시 배포/실패/복구 Linux 검증
- [x] EC2 root 전용 도구 설치·비활성 실행 차단 확인
- [x] GitHub production 환경과 main 전용 배포 제한 설정
- [x] 최종 workflow·프론트 배포 설정·문서 무결성 검사
- [ ] AWS 역할·GHCR 읽기 토큰·Vercel 식별자/토큰 연결
- [ ] HTTPS·운영 앱 키·백업 복원 준비 완료
- [ ] main의 실제 자동 배포 및 원격 상태 검사

## 4. 확인된 외부 준비 상태

GitHub 두 저장소의 production 환경을 생성하고 custom branch policy를 main 브랜치만 허용하도록 설정했다. required reviewer는 추가하지 않았다. backend production에 EC2_INSTANCE_ID를 등록했다. 나머지 AWS 역할/Vercel 식별자·토큰은 미등록이다. 로컬 AWS CLI 설정 파일은 없으며 EC2 SSM 에이전트는 active, 버전3.3.4121.0이다. ENV_VAR 지원 하한3.3.2746.0보다 높다. 이것만으로 SSM 관리 노드 등록/IAM 접근을 확인한 것은 아니다. Vercel 팀 Prism 안에는 프로젝트가 없다.

EC2 `/opt/prism-deploy` root:755에 deploy_ec2.py와 compose.ec2.yaml(root:644), `/etc/prism/deploy.json` root:600, 상태 폴더 `/var/lib/prism-deploy` root:700을 설치했다. 전송 파일 SHA256 대조와 Python 컴파일 검증, 유효한 합성 image/SHA 입력의 DEPLOYMENT_NOT_ACTIVATED 거부를 확인했다. 설정은 enabled=false, migration_policy=unchanged다. 앱/DB 작업은 수행하지 않았다. 첫 설치 시 Windows CRLF 문제로 잘못 생성된 빈 폴더2개와 예시 파일1개는 정확한 경로·빈 폴더·SHA256 확인 후 정리하고 줄바꿈 변환으로 재설치했다. 기존 runtime.env.pending과 RDS 데이터는 건드리지 않았다.

## 5. 결과와 남은 작업

배포/SSM/GHCR Linux unittest **20개**, 프론트 공개 상태 검사3개 및 기존 저장소 도구2개, 백엔드 저장소 도구2개, 프론트 타입/production build를 통과했다. actionlint 1.7.12 공식 SHA256 확인 후 두 CI 및 OIDC 진단 workflow 문법을 최종 검사했다. Ruff/format 배포 Python5개, 문서119개/ID87개/링크540개/ADR35개 무결성과 과거 기록490개·원본 평가7개 해시 보존을 통과했다. 문서 길이 경고5개는 기존 문서에 대한 안내로 실패가 아니다. 기존 Git 추적 파일의 비밀/문서 혼입 검사도 통과했다. 새 파일의 입력 제한·출력·시크릿 전달 경로를 별도로 검수했다.

이 변경은 앱 기능·DB 스키마 변경이 아니므로 대규모 AI 재평가나 유료 모델 호출을 하지 않았다. Git 원격 반영·main 병합·이미지 게시·실제 앱 배포는 아직 실행하지 않았다. 실제 GHCR GITHUB_TOKEN 권한, AWS OIDC trust claim, SSM 실행 결과, Vercel 프로젝트 환경, 실제 HTTPS/cookie/login은 로컬 테스트로 대체할 수 없다.

## 6. 최초 연결 순서

| 위치 | 필요한 설정 | 현재 상태 |
|---|---|---|
| 두 GitHub 저장소 production | main 브랜치만 허용, 수동 reviewer 없음 | 설정 완료 |
| backend production Variable | EC2_INSTANCE_ID | 설정 완료 |
| backend production Variable | AWS_DEPLOY_ROLE_ARN | IAM 역할 생성 후 입력 |
| EC2 instance profile | AmazonSSMManagedInstanceCore가 연결된 EC2 역할 | 연결/관리 노드 등록 확인 필요 |
| AWS IAM/SSM | GitHub OIDC provider, 제한된 deploy role, PrismDeployBackend 문서 버전1 | JSON 템플릿 준비 |
| EC2 root Docker 설정 | GHCR classic PAT, read:packages만 사용 | 사용자 발급 필요, 토큰을 채팅/Git/SSM 인자에 넣지 않음 |
| Vercel 팀 Prism | 프론트 프로젝트 생성, 도메인 연결, Git 자동 배포 비활성화 | 프로젝트 생성 필요 |
| frontend production Variables | VERCEL_ORG_ID, VERCEL_PROJECT_ID | 실제 Vercel ID로 입력 |
| frontend production Secret | VERCEL_TOKEN | 사용자 발급·GitHub Secret 직접 입력 필요 |
| DNS·EC2 운영 설정 | API A→52.79.50.98, HTTPS, runtime.env, 운영 GitHub 앱, 백업 복원 | 초기 출시 Gate 미완료 |

1. dev 변경 검토·Git 반영 후 main에서 deployment-identity workflow를 실행한다. 출력은 aud/sub뿐이며 JWT를 출력하지 않는다. production 환경은 main만 허용한다. 실제 sub와 deployment/aws-github-trust.json을 대조한다. 템플릿은 저장소/소유자 immutable ID 형식이며 legacy 형식으로 발급되면 **실제 확인한 정확한 값**으로 바꾼다. wildcard trust를 추가하지 않는다.
2. AWS에 OIDC provider `https://token.actions.githubusercontent.com`, audience `sts.amazonaws.com`을 준비하고 deployment/aws-github-trust.json으로 `PrismGitHubDeploy` 역할을 만든다. deployment/aws-deploy-policy.json을 연결한다. 역할은 특정 인스턴스+문서 SendCommand와 GetCommandInvocation만 허용한다. 별도 EC2 역할은 deployment/aws-ec2-trust.json + AmazonSSMManagedInstanceCore로 연결한다. 기존 instance profile이 있으면 교체 전 필요한 정책을 확인한다. SSM 관리 노드 Online을 확인한다.
3. deployment/ssm-deploy.json을 **PrismDeployBackend, Command, JSON, 버전1**로 만든다. 기존 문서가 있으면 덮어쓰지 않고 버전/내용을 먼저 대조한다. 역할 ARN을 backend production AWS_DEPLOY_ROLE_ARN에 입력한다.
4. EC2에서 root Docker 로그인에 다운로드 전용 토큰을 password-stdin으로 전달한다. 터미널의 숨김 입력을 사용하고 셸 기록/채팅/로그에 토큰을 쓰지 않는다. `/root/.docker` 700, config.json 600을 확인한다. 토큰 만료 전 교체한다.
5. Vercel 팀 Prism에서 프로젝트를 만들고 실제 Project ID/Team ID를 GitHub Variables에 등록한다. Vercel 토큰은 frontend production Secret에만 등록한다. Vercel의 별도 Git 배포는 비활성화하고 `PRISM_API_ORIGIN`은 workflow에 고정된 백엔드 HTTPS 주소를 사용한다. 도메인은 프로젝트 Domains에서 제공한 실제 DNS 안내를 따른다.
6. API DNS/HTTPS, 운영 OAuth/GitHub App·AI 키·동의/한도 설정을 완성하고 runtime.env.pending을 검증한 실제 runtime.env로 전환한다. 별도 DB 복원 검증 완료 시각을 `/etc/prism/deploy.json`에 기록하고 migration_policy=upgrade, enabled=true로 최초 활성화한다. 시각만 채워 실제 복원 검증을 대신하지 않는다.
7. 최신 main을 backend→frontend 순서로 최초 배포한다. CI/이미지 검증→private GHCR→SSM 완료→공개 ready, 프론트 login/API proxy 검사와 실제 OAuth/PR/Job 흐름을 확인한다. 이후 각 저장소 main push가 자동 실행된다. 단계6 이전 main 실행은 missing configuration으로 실패하며 출시 성공으로 간주하지 않는다.

## 7. 실패와 복구

Actions의 실패 상태와 SSM command ID로 조사한다. 원격 stdout 전체를 Actions로 복사하지 않는다. EC2 `/var/lib/prism-deploy/attempt.json`에 commit/digest/stage/status/schema/복구 결과를 보관한다. 설정은 root만 수정한다. DB가 변경되지 않은 조건에서만 이전 이미지로 복구하며, DB가 변경됐거나 복구가 실패하면 운영자 조치를 요구한다. 자동 DB downgrade는 없다.

프론트 검사가 실패한 경우 이 버전은 자동 rollback을 하지 않는다. Vercel의 이전 정상 배포로 수동 복구한다. 단일 EC2 컨테이너 교체에 잠깐의 중단이 있을 수 있다. 오래된 GHCR 이미지/EC2 이미지 정리는 정상·직전 복구 digest를 보존하는 별도 운영 작업이다. 현재 토큰 만료·디스크·실패 알림/예산 설정도 출시 전에 확인한다.

## 8. 참고

- [GitHub GHCR 인증/공개 범위](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub artifact 다운로드 권한](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts?tool=webui): 공개 저장소의 이미지 전달 artifact를 사용하지 않은 근거.
- [GitHub AWS OIDC](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [AWS SSM parameter 처리](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-troubleshooting.html)
- [Vercel GitHub Actions 안내](https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel)

## 9. Git 반영 작업

사용자가 2026-09-30 “커밋·푸시와 CI 확인까지 진행”을 승인했다. 이번 EC2 준비·자동 배포 변경을 architecture main, backend/frontend dev에 커밋하고 각 원격 CI까지 확인한다. 적용 스킬은 git-workflow와 기존 terminal-ops다. fetch 후 세 브랜치 모두 upstream과 차이0을 확인했다. 변경 파일을 명시해 stage하며 프론트/백엔드에는 문서를 올리지 않는다. 먼저 아키텍처 결정을 커밋한 뒤 양쪽 architecture.json을 해당 SHA로 고정한다. 코드 main 병합·최초 운영 배포는 이번 Git 작업의 실행 범위에 포함하지 않는다. 최종 커밋/원격 CI 결과는 완료 후 이 절에 기록한다.
