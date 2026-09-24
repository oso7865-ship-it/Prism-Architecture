# Config: 환경과 시작 검증

> ID: `CONFIG` · 소유: `backend/app/shared/config` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 환경 변수·앱 설정·시작 검증을 변경할 때

```text
shared/config/
├─ settings.py        Pydantic Settings·환경 변수 구조
└─ validation.py      필수 설정·조합 유효성 검사
```

Config는 환경을 읽는 기술 기반이다. Repository별 Rule threshold·WorkspaceRole·AI 전송 동의는 DB의 도메인 설정이지 환경 변수로 대신하지 않는다.

핵심 환경 변수: `APP_ENV`, `PUBLIC_APP_ORIGIN`, `PUBLIC_API_ORIGIN`, `DATABASE_URL`, `JWT_SIGNING_KEY`, `GITHUB_OAUTH_CLIENT_ID/SECRET`, `GITHUB_APP_ID/PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_API_VERSION`, `JOB_RUNNER_MODE`, `AI_ENABLED`.

`AI_ENABLED=false`가 기본이다. true일 때만 Provider/model/API key/외부 전송 예산이 모두 있어야 시작 또는 해당 기능 활성화를 허용한다. `JOB_RUNNER_MODE=embedded|external|disabled`를 검증한다. DB URL·private key·token에는 SecretStr 등 비밀 표시 타입을 사용하고 settings 전체를 repr/log로 출력하지 않는다.

`.env.example`에는 이름·형식·안전한 placeholder만 둔다. 실제 값은 Render의 비밀 설정으로 관리한다. 프론트 `VITE_*`에는 공개 API 경로 같은 값만 넣고 서버 Secret을 전달하지 않는다. 개발 편의 기본 비밀번호/키를 운영에서 허용하지 않는다.

미정 Provider/API version을 코드에서 임의 추정하지 않는다. GitHub API version은 구현 때 검증한 값을 명시하고 adapter contract test와 함께 올린다.

필수 검증: 비밀 누락·잘못된 URL/환경 조합·AI ON인데 예산 미설정·허용하지 않은 origin·설정 repr 마스킹. 실제 값 없이 단위 테스트 가능하게 환경 로더와 검증 함수를 분리한다.

구현 저장소의 안전한 설정 예시는 `config/development.example`이다. 부착 HARNESS가 `.env.*` 추적을 금지하므로 이 파일을 로컬 `.env`로 복사한다. 예시에는 로컬 개발용 값만 두며 실제 `.env`는 Git에 올리지 않는다.
