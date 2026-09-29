# 작업 리포트: 개발 서버 시작과 Docker 소켓 복구

> 작성일: 2026-09-28
> 패키징/배포일: 해당 없음
> 작업 브랜치: architecture main; backend/frontend dev
> 커밋/PR: 미커밋
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-28T20:49:44+09:00
> 구현 상태: 앱 코드 변경 없음, 개발 실행 환경 복구
> 로컬 검증 상태: 완료
> 로컬 검증 대상: 기존 main 병합 코드, 로컬 DB·API·Vite
> 로컬 검증 근거: Docker DB Healthy, frontend/API readiness/proxy readiness HTTP200
> 병합 상태: 이번 작업 미수행
> 배포 상태: 미수행
> 실제 연동 상태: 로컬 DB 연결 확인, GitHub 재로그인·새 LLM 요청 미실행
> 작업 범위: M
> 적용 스킬: terminal-ops, troubleshooting-report
> 적용 Gate: 실행 결과·경로·데이터 보존 확인
> 위험도: 환경 변경(비파괴적)
> 위험 작업 여부: 예, 사용자 서버 재기동 요청 범위에서 수행

## 0. 작업 범위 확인

사용자가 PR 리뷰 답변을 화면에서 확인하도록 개발 서버를 모두 켜 달라고 요청했다. Docker Desktop/PostgreSQL·FastAPI·Vite를 시작하고 접속 준비 상태를 검사한다. 앱 코드·키·DB 스키마·기존 데이터는 변경하지 않는다. 문서는 중앙 아키텍처에만 작성한다. AWS 배포와 백엔드 CI 수정은 이번 범위 밖이다.

## 실행 결과

- Vite: localhost:5173, PID11496, HTTP200.
- FastAPI: 127.0.0.1:8000, PID41856. 기존 설정과 Windows SelectorEventLoop를 사용하고 접근 로그를 비활성화했다.
- PostgreSQL: 기존 prism-local-db-1 및 named volume을 그대로 사용. compose up -d --wait 성공/Healthy.
- 직접 /health/ready 및 Vite 경유 /health/ready 모두 HTTP200으로 DB 연결 확인.
- 앱/서버는 숨겨진 백그라운드 프로세스로 실행. 로그는 워크스페이스 audit-artifacts/server-start-20260928-204050 아래에 있다.
- 기존 조직 PR의 AI 탭을 브라우저에 여는 요청을 등록했다(앱 응답 queued, 실제 탭 표시 여부 미확인). 로그인 세션과 저장된 리뷰 내용 자체는 이번에 검수하지 않았다. 새 AI 리뷰를 요청하지 않았다.

## 트러블슈팅: Docker Desktop이 오래된 소켓 때문에 시작하지 못함

- 사건 상태: 임시 우회 후 로컬 복구 검증 완료.
- 원인 상태: 시작을 막은 직접 오류는 확인. Windows 내부 파일 접근 실패의 근본 원인은 미확인.

### 어디서 발생했나

Windows Docker Desktop4.85.0 시작 중, 2026-09-28 20:40~20:49 KST. 호스트 로그의 Inference manager 및 Secrets Engine 초기화 단계. LOCALAPPDATA/Docker/run/dockerInference와 LOCALAPPDATA/docker-secrets-engine/engine.sock.

### 어떤 문제가 있었나

Docker API named pipe가 만들어지지 않고 DB를 켤 수 없었다. 로그에 오래된 AF_UNIX 연결 파일을 제거할 수 없다는 The file cannot be accessed by the system 오류가 있었다. 해당 항목들은 길이0, ReparsePoint였으며 이전 날짜의 생성/수정 시각이 남아 있었다. 프론트만 먼저 실행됐고 DB 복구 전 API 준비 상태는 성공하지 않았다.

### 어떻게 발생했나

꺼진 Docker Desktop 시작 → compose 기동 실패 → 호스트 로그에서 Inference manager 오류 발견 → 임시 run 폴더 보존 후 재시작 → Secrets Engine의 다른 오래된 소켓 오류 발견. 보존 후 한 번 더 시작했을 때도 다른 이전 날짜의 engine.sock이 관찰돼 엔진이 중단됐다. 과거 비정상 종료가 촉발했는지는 확인하지 못했다.

### 왜 발생했나

직접 원인은 Docker 시작 코드가 기존 연결 파일에 접근·제거하지 못해 전체 기동을 중단한 것이다. DB 파일 손상은 관측하지 않았다. 유사한 Docker 공식 이슈 저장소의 사용자 보고가 있지만 Windows 커널/NTFS 원인을 이 장치에서 입증한 것은 아니다.

참고: [Docker desktop-feedback #554](https://github.com/docker/desktop-feedback/issues/554), [#527](https://github.com/docker/desktop-feedback/issues/527). 외부 게시물의 광범위 삭제·초기화 명령은 실행하지 않았다.

### 어떻게 해결했나

| 순서 | 실제 조치 | 결과 |
|---|---|---|
| 1 | Docker Desktop 시작, compose up | 엔진 API 부재·Inference manager 실패 |
| 2 | 설치 경로가 확인된 Docker 프로세스 종료 후 run 폴더 이름 변경 보존 | Inference 단계 통과, Secrets Engine 단계에서 실패 |
| 3 | run 및 docker-secrets-engine 폴더가 0바이트 항목만 담는지 확인하고 이름 변경 보존 | 다른 이전 날짜의 engine.sock 오류가 다시 관찰됨 |
| 4 | Docker 설치 경로의 프로세스를 모두 종료. 정확한 두 런타임 경로·비링크 디렉터리·0바이트 내용 확인 후 다시 보존. 원래 경로가 사라졌는지 검사하고 빈 디렉터리 명시 생성 | 시작 직후 compose는 아직 엔진 부재. 이후 재확인 시 compose 성공/DB Healthy |
| 5 | 기존 Python 가상환경으로 API, 기존 node_modules로 Vite 실행 | frontend200, API readiness200, proxy readiness200 |

보존한 폴더는 LOCALAPPDATA/Docker/run.stale-20260928-204343·204511·204714 및 LOCALAPPDATA/docker-secrets-engine.stale-20260928-204511·204714다. 기존 Docker 데이터·볼륨·설정은 삭제·초기화하지 않았다. PostgreSQL named volume을 기존 그대로 사용했다. 이 작업은 연결 경로 우회이며 Windows/Docker 결함의 영구 수정이 아니다.

### 앞으로 어떻게 대응하나

| 조치 | 담당자 | 실행 조건 | 완료 기준 | 상태 |
|---|---|---|---|---|
| 재시작 실패 시 호스트 로그와 소켓 경로 확인 | 다음 작업자 | 같은 증상 재발 | 직접 실패 지점과 영향 데이터 구분 | 절차 기록 완료 |
| 기존 소켓 보관본 정리 | 미정 | 정상 사용·재기동 확인 후 | 정확한 임시 대상만 별도 확인해 정리 | 미수행 |
| Docker/Windows 근본 원인 및 수정 버전 검토 | 미정 | 반복 재발 시 | 해당 환경에서 정상 종료·재기동 재현 검증 | 후속 |

## 한계와 남은 작업

PR 결과를 볼 수 있는 로컬 서버 준비 상태를 검증했다. 로그인 및 리뷰 내용 확인은 사용자 화면에서 이어간다. 공개 AWS 배포·전체 제품 테스트·AI 품질 평가·CI 실패 수정은 수행하지 않았다. 기존 AWS 결정 미커밋 변경과 문서 보관본은 그대로 보존했다.
