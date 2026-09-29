# EC2 배포 전 실행 안내

아직 배포하지 않았다. 이 안내는 운영 값이 확정된 뒤 실행할 순서다. 코드 저장소의 실행 설정과 정확한 CI 통과 커밋을 함께 사용한다. 리전/인스턴스/OS·호스트 HTTPS 프록시·실제 DB·이미지 registry·비밀 전달 방식은 결정 전이며 임의로 자원을 만들지 않는다.

## 필요한 값과 경계

- `PRISM_IMAGE`: 배포할 registry 이미지의 `@sha256:` digest. 이전 배포 digest도 별도로 보관한다.
- `PRISM_ENV_FILE`: 서버의 비공개 환경 파일 절대 경로. 예시는 backend `config/production.example`. 소유자만 쓰고 읽도록 호스트 권한을 설정한다. Compose raw 형식을 지원하는 버전이 필요하며 `scripts/check_ec2.py`로 확인한다.
- `PRISM_DB_CA_FILE`: DB 발급기관의 신뢰할 CA 파일 절대 경로. 컨테이너 `/run/prism/postgres-ca.pem`으로 읽기 전용 마운트하고 `PGSSLROOTCERT`를 사용한다. DB URL은 verify-full을 유지한다.
- raw 환경 파일은 값을 따옴표로 감싸지 않는다. PEM은 한 줄의 문자 `\n`으로 구분한다(현재 GitHub adapter가 실제 줄바꿈으로 변환). `$`를 Compose 변수로 치환하지 않는다. 파일/Compose 확장 결과를 로그·Git·화면에 출력하지 않는다.
- 공개 앱/API origin은 동일한 프론트 HTTPS 주소. Vercel rewrite 목적지만 EC2 HTTPS 주소다. OAuth/App callback은 프론트, Webhook은 EC2 직접 주소로 등록한다. 개발 키 재사용을 끝내고 운영 키를 별도로 주입한다.
- 전체 기능 검증 시에만 sync/analysis worker와 AI를 켠다. 최초 설정 기본값은 OFF다. 팀30회/일과 요청당 최대2회는 유지한다.

## 실행 순서

1. 정확한 코드 커밋 CI 통과와 공개 Git 비밀 검사를 확인하고 해당 이미지 digest를 결정한다.
2. EC2 호스트의 Docker/Compose·프록시·TLS·보안그룹을 준비한다. 8000 포트는 외부에 열지 않는다. 컨테이너 1GiB와 별도로 호스트 메모리/디스크 여유를 확보한다.
3. 세 `PRISM_*` 경로/이미지 변수를 지정하고 `docker compose -f deployment/compose.ec2.yaml config --quiet`로 검사한다. 원문이 출력되는 `config` 사용은 피한다.
4. `docker compose -f deployment/compose.ec2.yaml run --rm --no-deps api python -m app.shared.config.preflight --image "$PRISM_IMAGE"` 실행. 하나라도 FAIL이면 중단한다. CA 내용/키/DB의 실제 유효성은 다음 단계에서 검증한다.
5. 운영 DB의 복원 가능한 백업과 별도 복구 DB를 준비한다. 사전 복원 검증 없이 스키마 변경을 시작하지 않는다. 운영 DB에서 pytest를 실행하지 않는다.
6. 단일 배포 작업자만 `docker compose -f deployment/compose.ec2.yaml run --rm --no-deps api alembic upgrade head`를 실행한다. 실패 시 컨테이너 교체 중단.
7. `docker compose -f deployment/compose.ec2.yaml up -d --no-deps api` 후 `/health/live`와 `/health/ready`를 확인한다. 기본 이미지 변경만으로 DB downgrade를 하지 않는다.
8. 프론트 저장소에서 `PRISM_API_ORIGIN` 환경 변수에 실제 EC2 HTTPS origin을 지정한 뒤 `npm run configure:deployment`로 Vercel 설정을 생성한다. 이미 존재하는 `vercel.json`은 덮어쓰지 않으며 재설정은 별도로 검토한다. 이 명령은 배포하지 않는다.
9. 실제 주소에서 OAuth 왕복/쿠키 refresh·두 계정 격리·Webhook 서명·동기화·분석·AI 요청/근거·Job lease 복구를 확인한다. 장애 알림, 로그 보관, DB/디스크 사용량, 비용 알림의 수신자까지 점검한다.

## 복구

- 앱 오류: migration과 호환되는 이전 이미지 digest로 교체하고 준비 상태/핵심 기능을 재확인한다. 자동 DB downgrade 금지.
- 데이터 오류: 백업을 별도 DB에 복원해 데이터·인덱스·마이그레이션 버전을 확인하고 전환한다. 운영 DB를 바로 덮어쓰지 않는다.
- 워커 중단: 재시작 후 만료된 lease 회수와 중복 처리 방지를 확인한다. AI 전송 여부가 불명확한 호출을 임의로 재전송하지 않는다.
- 현재 로컬 증거: 테스트 DB 합성 스키마의2행/2인덱스/한글 데이터 바이트 일치 복원, Linux 자원 제한 컨테이너의 파서/헬스체크. 운영 백업·AWS 부하·프록시 실제 동작을 대신하지 않는다.
