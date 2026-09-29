# EC2 직접 접속과 RDS 준비 상태

## 작업 계약

- 요청: 사용자가 직접 접속한 EC2에 에이전트도 접속할 수 있는지 확인한다.
- 범위: 로컬 SSH 키 경로 확인, SSH 인증, 서버의 운영체제·도구·인증서 파일 읽기. 서버 패키지 설치·DB 생성·배포는 이번 접속 확인에서 실행하지 않는다.
- 기준: CORE, DEPLOYMENT, 기존 EC2 실행 안내, terminal-ops. 아키텍처 main에만 기록하고 구현 저장소는 변경하지 않는다.
- 완료 기준: 사용자가 보여준 EC2와 일치하는 호스트에서 `ubuntu` 계정으로 읽기 전용 명령이 성공한다.

## 확인 결과

- 직접 SSH 인증 성공. 원격 사용자 `ubuntu`, 호스트 `ip-172-31-3-188`로 사용자 브라우저 터미널과 일치했다.
- Ubuntu 24.04.4 LTS. PostgreSQL 클라이언트 16.15, Git 실행 파일 확인. 현재 PATH에서 Docker 실행 파일은 발견되지 않았다.
- `/etc/prism/certs/rds-global-bundle.pem` 파일 존재: 165,408바이트, 권한 644. 이 파일 확인만으로 인증서의 유효성이나 DB 접속을 다시 검증한 것은 아니다.
- 사용자 화면 증거: RDS PostgreSQL 17.11, db.t4g.micro, 20GiB gp2, 저장 암호화 활성화. EC2의 psql에서 `verify-full`을 지정한 DB 로그인과 TLS 1.3 연결이 성공했다.
- 사용자 화면의 일반 DB 목록은 `postgres`, `rdsadmin` 두 개였다. 아직 `prism` DB는 확인되지 않았다. 브라우저 psql의 DB 인증은 별도 SSH 세션으로 공유되지 않는다.

## 접속 실패와 해결

1. 제한된 로컬 실행 환경에서 SSH 네트워크 접근이 거부됐다. 사용자 요청 범위의 승인된 실행 환경에서 재시도했다.
2. 서버까지 연결됐지만 원본 PEM에 다른 로컬 그룹의 접근 권한이 있어 OpenSSH가 키 사용을 거부했다.
3. 현재 Windows 사용자만 접근할 수 있는 임시 폴더에 키 사본을 만들고 재시도해 SSH 인증에 성공했다. 원본 키 내용과 권한은 변경하지 않았다.
4. 최초 수신 호스트 키를 로컬 작업 파일에 저장했고 후속 접속에는 StrictHostKeyChecking=yes를 적용했다. AWS 외부 경로를 통한 호스트 키 지문 대조는 별도로 수행하지 않았다.

키 내용·DB 비밀번호는 출력하거나 Git 문서에 저장하지 않았다. 서버 조회 명령은 종료 코드 0으로 완료했다. 접속 확인 후 이번 작업에서 만든 임시 키 사본과 빈 임시 폴더를 정리했다. 다음 접속 때도 제한된 권한의 사본을 준비해야 한다.

## 다음 단계와 검증 한계

- 전용 DB/서비스 계정 준비, 해당 계정의 실제 로그인, Docker/Compose 설치, 운영 환경 설정, migration과 배포가 남아 있다.
- 현재 애플리케이션과 Alembic은 같은 DATABASE_URL 설정을 읽는다. DB 권한 설정 시 migration에 필요한 schema 생성 권한도 고려한다.
- DNS·HTTPS·Vercel·운영 OAuth/Webhook·백업 복원·비용/장애 알림은 아직 확인되지 않았다. SSH 성공을 배포 완료로 집계하지 않는다.
- 이번에는 애플리케이션 코드를 변경하지 않았고 유료 AI 호출도 하지 않았다.
- 문서 검증 PASS: 116개 Markdown/85개 문서 ID/520개 링크, 기존 보존 기록 490개와 원 평가 파일 7개의 바이트 해시 일치. 기존 긴 문서 안내 경고는 유지한다. 커밋·푸시는 이번 요청에서 실행하지 않았다.

## 후속: DB 인증 전달 없이 초기화 파일 준비

사용자는 직접 접속 후 무엇이 필요한지 물었다. 이미 인증된 브라우저 psql에서 초기화 파일을 한 번 실행하는 방식으로 안내한다. RDS 관리자 비밀번호를 채팅·로컬 파일로 받지 않는다. 실제 RDS 변경은 아직 실행하지 않았고 아래 파일만 EC2에 준비했다.

- `/home/ubuntu/.config/prism/bootstrap.sql`: 기존 `prism` DB 또는 `prism_app` 역할이 있으면 중단. PostgreSQL 17의 `postgres` DB에 `hoon`으로 접속한 경우에만 새 역할과 DB를 만든다. 새 DB 소유자는 관리자 `hoon`, 서비스 역할에는 CONNECT와 public schema의 USAGE/CREATE만 명시적으로 부여한다. 클러스터 SUPERUSER/CREATEDB/CREATEROLE/REPLICATION/BYPASSRLS는 부여하지 않는다. 이 계정은 현행 단일 DATABASE_URL 계약에 맞춰 생성한 앱 테이블의 소유권과 migration 권한을 갖게 된다.
- `/home/ubuntu/.config/prism/database.env`: EC2에서 생성한 무작위 앱 비밀번호가 포함된 DATABASE_URL. 폴더 700, 두 파일 600으로 ubuntu만 읽는다. SQL에는 SCRAM verifier만 포함되며 평문 비밀번호는 없다. 환경 파일은 실제 전체 운영 설정에 병합할 재료이며 이것만으로 앱 배포가 완료되지는 않는다.
- 비밀번호·verifier 원문은 도구 출력이나 공개 기록에 싣지 않았다. 호스트 키 검사를 유지했고 각 SSH 호출 후 임시 키 사본을 정리했다.
- 로컬의 격리된 PostgreSQL 17 컨테이너에서 실제 SCRAM 로그인, 잘못된 비밀번호 거부, 앱 DDL/인덱스 생성 권한, 클러스터 DB 생성 금지, PUBLIC 접속 차단, 잘못된 관리자 거부, 재실행 시 기존 비밀번호 불변을 확인했다. 테스트 컨테이너와 전용 볼륨은 정리했으며 실제 RDS 호출은 0회다.
- 사전 DB/Security 검토: 기존 운영 데이터 변경·삭제 없음, 새 DB/역할만 생성, 비밀 파일 접근 제한, 같은 이름이 있으면 fail-closed. 테이블 PK/FK 등은 아직 생성하지 않으므로 기존 migration 계약을 유지한다. 서비스 계정의 실제 RDS 로그인과 권한 검증은 파일 실행 후에 한다.
- 초기화는 CREATE DATABASE 특성상 전체가 단일 트랜잭션이 아니다. 중간 실패 시 ON_ERROR_STOP으로 중단하고 객체 상태를 검사한다. 역할만 생긴 상태라면 기존 비밀 파일을 유지한 채 남은 생성 단계를 검토한다. 기존 DB나 역할을 자동 삭제/덮어쓰기하지 않는다. 새 객체에 데이터가 없다면 향후 명시적 정리 범위를 확인한 뒤 제거할 수 있다. 향후 실제 테이블 migration 전에는 운영 백업/복원 준비를 별도로 확인한다.

사용자 실행 명령: 현재 브라우저의 `postgres=>`에서 `\i /home/ubuntu/.config/prism/bootstrap.sql`. 성공 표시는 `PRISM_DB_BOOTSTRAP_COMPLETE`다. 실행 결과를 아직 받지 않았으므로 RDS 초기화 완료로 기록하지 않는다.

## 후속: 초기화 확인과 Docker 실행 환경 준비 완료

사용자가 초기화 명령을 실행했다고 알려 직접 SSH에서 서비스 계정으로 재검증했다. 앞 절의 실행 대기 상태를 다음 결과로 갱신한다.

| 대상 | 직접 확인 결과 |
|---|---|
| RDS 로그인 | prism DB / prism_app 역할 / PostgreSQL 17.11, verify-full 사용, TLS 1.3 |
| DB 권한 | public schema CREATE 허용, SUPERUSER/CREATEDB/CREATEROLE 없음, PUBLIC CONNECT 없음 |
| 앱 테이블 | 0개. 이번 조회는 SELECT만 수행했고 운영 DB에서 테스트나 migration을 실행하지 않음 |
| EC2 메타데이터 | IMDSv2로 t3.small / ap-northeast-2 확인. 자격 증명 endpoint는 조회하지 않음 |
| Docker | 공식 Docker Ubuntu apt 저장소에서 Engine 29.8.1, Compose 5.5.1 설치. 서비스 시작/부팅 활성화. 기존 패키지 삭제나 전체 OS 업그레이드는 하지 않음 |
| 컨테이너 실행 | hello-world를 network none/read-only/64MiB/32 PID로 실행 후 제거. ubuntu를 docker 그룹에 추가하지 않고 sudo를 사용 |
| 백엔드 코드 | `/opt/prism/releases/26646ff080c165f041a7805f077b7cae8e9299e0`에 정확한 커밋으로 checkout. clean 상태 확인 |
| 원격 CI | [backend-ci 36583178069](https://github.com/oso7865-ship-it/Prism-Backend/actions/runs/36583178069)의 동일 head SHA / completed / success 재확인 |
| Compose 검사 | 해당 release의 scripts/check_ec2.py 통과. 합성 값으로 누락 설정 거부·raw env 보존·자원/권한/포트 제한 확인. 실제 서비스 시작 0개 |
| 설정 초안 | `/home/ubuntu/.config/prism/runtime.env.pending` 준비. RDS URL, 프론트 origin 두 개, 새 JWT/Webhook 비밀값을 서버에서만 보관. worker와 AI는 OFF. 운영 GitHub/AI 키는 넣지 않음 |

사용자 확인: GitHub 운영용 OAuth/App는 아직 설정하지 않았고 현재 EC2 IP는 자동 할당 주소다. Elastic IP, 두 도메인 DNS, HTTPS 프록시, 이미지 registry/digest, 운영 GitHub/AI 키, 백업/복원, 실제 migration/API 실행과 최종 사용자 흐름 검증이 남아 있다. 필수 인증을 끄거나 preflight를 우회해 API를 시작하지 않았다. 기존 로컬 개발 키는 서버로 복사하지 않았다.

서버 로그와 준비 상태는 비공개 설정 디렉터리의 docker-install.log/docker-readiness.json/runtime-preparation.log/runtime-readiness.json에 있다. 공개 기록에는 비밀값·SQL verifier를 포함하지 않는다. 이 턴의 각 SSH 호출에서도 키 사본은 작업 후 정리했다. 유료 AI 호출/공개 배포/커밋/푸시는 하지 않았다.

호스팅 선택과 초기 권한/비밀 주입 결정은 [ADR-DEPLOY-005](../docs/architecture/adr/deployment/ADR-DEPLOY-005-rds-initial-runtime.md)에 기록하고 DEPLOYMENT/OPEN-ITEMS/DATABASE/결정 맵/문서 라우팅을 동기화했다. 신규 자원 크기의 부하 적합성, 운영 백업 복원, public endpoint 검증은 아직 미완료다.

최종 문서 검증: 새 ADR의 필수 제목과 기록 상대 링크를 수정한 뒤 PASS(117개 Markdown, 86개 문서 ID, 529개 링크, 34개 ADR). 보존 기록 490개와 원 평가 파일 7개의 바이트 해시도 PASS이며 git diff --check에서 공백 오류는 없었다. 기존 긴 문서 안내 경고는 유지한다.

## 후속: 탄력적 IP 연결과 접속 주소 갱신

수정 범위는 접속 보조 스크립트와 운영 상태 기록이며 CORE/DEPLOYMENT/OPEN-ITEMS를 따른다. 사용자 화면에 처음 보인 3.35.150.103은 RDS 엔드포인트의 실제 DNS 조회 결과와 일치했다. AWS는 RDS 관리 EIP를 사용자가 수정/해제할 수 없다고 명시한다. 이 주소를 EC2에 옮기는 대신 새 EC2용 탄력적 IP를 할당하도록 안내했다. 기존 RDS 연결이나 권한을 변경하지 않았다.

사용자 화면에서 새 EIP 52.79.50.98이 prism 인스턴스 i-02d892cf8019b2d7a / private IP 172.31.3.188에 연결된 것을 확인했다. SSH 접속 대상만 새 EIP로 바꾸고 HostKeyAlias로 기존에 저장한 호스트 키를 대조했다. StrictHostKeyChecking=yes 상태에서 로그인과 hostname -I가 성공했으며 172.31.3.188이 반환됐다. 기존 IP로 재접속하거나 새 호스트 키를 무조건 신뢰하지 않았고 임시 키 사본도 정리했다.

현재 로컬 DNS 조회에서 api-prismquest.p-e.kr과 prismquest.p-e.kr은 모두 이름 없음으로 반환됐다. 이는 해당 조회 시점/리졸버의 결과이며 전체 DNS 전파 상태를 보장하지 않는다. 백엔드 A 레코드는 새 EIP를 가리키도록 안내하고, 프론트는 후속 Vercel 설정값으로 연결한다. 실제 HTTPS·앱 실행은 여전히 대기 중이다.
