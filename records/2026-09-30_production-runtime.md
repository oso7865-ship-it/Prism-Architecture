# 운영 환경값 반영 결과 — 2026-09-30

이 기록은 환경값 준비 단계의 결과다. 이후 앱 실행·운영 로그인·웹훅·자동배포 완료는 [전체 출시 결과](2026-09-30_full-ec2-release.md)를 따른다.

## 범위

사용자가 EC2 운영 환경값 입력을 요청하고 운영 GitHub 정보가 백엔드 `.env`에 있다고 확인했다. CORE/CONFIG/DEPLOYMENT와 실제 Settings·preflight·Compose를 기준으로 terminal-ops와 보안 Gate를 적용했다. 운영 DB·JWT·웹훅 비밀은 서버의 기존 값을 보존하며 지정한 `.env`에서 GitHub OAuth/App·DeepSeek 항목만 읽었다. 소스 파일은 수정하지 않았다.

## 결과

`/home/ubuntu/.config/prism/runtime.env`를 ubuntu 소유 600, 상위 디렉터리 700으로 생성했다. `.pending` 원본은 보존했다. 키는 로컬 프로세스 메모리→호스트 키가 고정된 SSH 표준입력으로 전송했으며 명령 인자·채팅·검증 결과·Git에 출력하지 않았다. DB 비밀번호를 로컬로 가져오지 않았다.

| 설정 | 적용 결과 |
|---|---|
| APP_ENV | production |
| PUBLIC_APP_ORIGIN / PUBLIC_API_ORIGIN | 모두 https://prismquest.p-e.kr, Vercel 동일 출처 프록시 계약 유지 |
| DATABASE_URL | 기존 RDS prism/prism_app 및 verify-full 보존 |
| JWT_SIGNING_KEY / GITHUB_WEBHOOK_SECRET | 기존 서버 값 보존 |
| GitHub OAuth/App | 사용자가 지정한 로컬 .env의 값 반영 |
| GITHUB_APP_SLUG | 인증된 GitHub App 응답의 현재 이름으로 교정 |
| DEEPSEEK_API_KEY / DEEPSEEK_MODEL | 키 반영, 기존 deepseek-flash 유지 |
| AUTH / SYNC / ANALYSIS / AI | 운영 파일에서 true로 구성 |
| AI_DAILY_LIMIT | 팀별 하루30회 |

작업 시각은 2026-09-29 18:53:54 UTC(한국 9월30일 03:53)다. 실제 앱 시작과 DB migration은 수행하지 않았다. `/etc/prism/deploy.json`의 초기 활성화 Gate는 이 작업으로 변경하지 않는다. 운영 파일의 활성화 플래그는 다음 배포 시 적용되며 현재 worker/AI가 실행된다는 뜻이 아니다.

## 검증과 수정

- PEM RSA 개인 키 형식·서명 검증 통과. GitHub GET /app의 JWT 인증 성공과 App ID·Client ID 일치를 확인했다. contents/pull_requests/metadata 읽기 권한도 확인했다.
- 최초 검증은 로컬 App slug와 GitHub 현재 slug가 달라 운영 파일 생성 전에 중단했다. ID/Client ID/개인 키로 동일 앱임을 검증한 뒤 GitHub가 반환한 현재 slug를 사용해 재실행했다. 로컬 .env를 덮어쓰지 않았다.
- DeepSeek GET /models 인증 성공과 설정 모델의 조회 가능 여부를 확인했다. 코드 전송·유료 추론 호출은 0회다.
- EC2 psql에서 RDS CA·호스트명 verify-full, 전용 사용자/DB 및 SSL 세션을 읽기 전용 SELECT로 확인했다.
- Docker Compose의 raw 환경 파일 파싱을 config --quiet로 검증했다. 이미지 자리에는 문법 검증용 합성 digest를 전달했으며 이미지 다운로드·배포는 하지 않았다. 실제 release image를 사용한 전체 preflight는 첫 배포 단계에 남아 있다.
- 최종 파일을 다시 읽어 입력값 일치·필수 항목 존재·권한을 확인했다. 중간 전달물과 검증 stdout에는 비밀값을 남기지 않았다. 보안 Gate는 이번 설정 전달·보관 범위에서 PASS다.

## 남은 검증

OAuth Client Secret과 GitHub App Client Secret의 실제 code 교환, 운영 callback 등록 일치, Vercel 프록시·쿠키, Webhook HMAC 실전송, 앱 시작 및 ready=200은 아직 확인하지 않았다. GitHub App 개인 키 인증 성공만으로 로그인 성공을 주장하지 않는다. GHCR 읽기 토큰, AWS OIDC/SSM, Vercel 프로젝트/토큰, 백업 복원 및 최초 main 배포 준비도 별도다.

서버 `/home/ubuntu/.config/prism/runtime-configuration-status.json`에는 값 대신 검사 결과만 보관한다. 문서는 아키텍처 저장소에만 추가했으며 이번 환경값 변경은 Git 커밋·푸시하지 않았다.
