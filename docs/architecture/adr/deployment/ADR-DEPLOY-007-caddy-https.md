# ADR-DEPLOY-007: EC2 Caddy HTTPS 진입점

> ID: `ADR-DEPLOY-007` · 소유: `DEPLOY` · 기준: `2026-09-30`
> 읽는 때: EC2 인증서·HTTPS 프록시·갱신 설정을 변경할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-30`
- 근거: 사용자가 보안 그룹 개방을 담당하고 EC2 HTTPS 설정을 에이전트에게 위임했다.
- 대체하는 ADR: 없음. DEPLOY-005/006의 호스트 HTTPS 진입점을 구체화한다.
- 대체한 ADR: 없음.

## 배경

EC2와 API 도메인을 준비했지만 HTTPS 프록시와 인증서가 없었다. 첫 앱 배포 전에 신뢰 가능한 HTTPS 진입점과 갱신 방식을 설정한다.

## 결정

Ubuntu 호스트에 Caddy 공식 stable 서명 패키지를 설치하고 systemd 서비스로 실행한다. API 도메인 `api-prismquest.p-e.kr`의 A 레코드는 EC2 탄력적 IP `52.79.50.98`을 가리킨다. 공개 TCP 80/443은 Caddy가 받고 Docker API의 `127.0.0.1:8000`으로 전달한다. 관리 API는 `127.0.0.1:2019`로 한정한다. HTTP는 HTTPS로 전환하며 공인 ACME 인증서 발급·갱신을 Caddy가 관리한다.

설정은 `/etc/caddy/Caddyfile`의 root 소유 파일이고 서비스는 caddy 사용자로 실행한다. 인증서 상태는 `/var/lib/caddy/.local/share/caddy`에 유지한다. 디렉터리 700, 개인 키 600을 확인하고 Git·이미지·로그에 키를 넣지 않는다. 요청 access log는 활성화하지 않으며 기본 오류 로그에서도 request 필드를 제외해 요청 URI·헤더를 기록하지 않는다. 오류 상태와 원인 메시지는 남긴다.

설정 변경은 validate 후 reload한다. 앱 이미지 배포와 Caddy 설정/패키지 업데이트는 별개다. Vercel의 같은 출처 프록시·인증 쿠키·CSRF, RDS verify-full, private GHCR/OIDC/SSM과 초기 배포 Gate는 유지한다.

## 대안

Nginx와 별도 인증서 갱신 도구를 조합하는 대신 Caddy 한 서비스로 초기 운영 절차를 줄인다. ALB를 추가하지 않고 기존 단일 EC2를 사용한다.

## 영향과 한계

단일 EC2는 다중 인스턴스 가용성을 제공하지 않는다. Caddy가 실행되고 DNS·ACME 통신·인증서 저장소가 유지돼야 갱신할 수 있다. 자동 갱신 설정은 미래의 갱신 성공을 보장하는 실측 결과가 아니다.

## 소유 문서와 검증

실제 Caddy 2.11.4 설치, 설정 검증, active/enabled, Let's Encrypt 발급, 외부 TLS 1.3의 신뢰/호스트명 검증 및 HTTP 308을 확인했다. 백엔드 앱 미기동으로 HTTPS ready는 502이며 앱 배포 성공으로 처리하지 않는다. 현재 상태는 [DEPLOYMENT](../../operations/DEPLOYMENT.md), 설정·검증·복구는 [HTTPS 작업 기록](../../../../records/2026-09-30_ec2-https.md)에 둔다.
