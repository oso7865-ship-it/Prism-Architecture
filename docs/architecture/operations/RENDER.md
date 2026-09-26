# Render 배포와 무료 환경의 한계

> ID: `RENDER` · 소유: `deployment` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: Render·Docker·CI/CD·DB 호스팅을 변경할 때

## 배포 기본 구성

```text
브라우저 → Vercel(Vue + /api reverse proxy)
                   ↓
             Render FastAPI
             ├─ API process + embedded Job dispatcher
             └─ 제한된 Parser subprocess
                   ↓
             외부 PostgreSQL

GitHub Webhook → Render 직접 HTTPS endpoint
```

Python 모듈형 모놀리스 한 개로 시작한다. Redis/Kafka/Kubernetes/MSA는 요구하지 않는다. Parser가 있는 Docker 이미지를 제안하며 앱 entrypoint는 `uvicorn app.main:create_app --factory --host 0.0.0.0 --port "$PORT" --workers 1`이다. 구현 저장소의 Dockerfile과 deployment/render.example.yaml을 사용하며 실배포 여부는 최신 구현 Report로 확인한다.

## 외부 서비스 사실 — 2026-09-25 확인

Render 무료 Web Service는 15분간 들어오는 트래픽이 없으면 멈출 수 있고 다음 요청의 기동에 지연이 있다. 재배포/재시작/중지 때 로컬 파일은 사라진다. 무료 서비스 종류에는 제약이 있으며 상시 Background Worker를 무료라고 전제하지 않는다. 무료 Render PostgreSQL은 생성 30일 후 만료된다. [S-RENDER-FREE](../reference/SOURCES.md#s-render-free)

따라서 로컬 SQLite·파일을 영속 Job DB로 쓰지 않는다. 외부 PostgreSQL provider는 아직 미정이다. 단기 시연용 30일 DB와 장기 보관 가능한 배포를 구분한다.

## 무료 MVP 보장 수준

Job을 DB에 접수하므로 앱 재기동 후 복구할 수 있게 설계한다. 그러나 잠든 동안 작업이 실행된다는 보장은 없다. GitHub Webhook 자동 분석 역시 best-effort다. 기동 지연으로 delivery가 실패할 수 있고 GitHub는 자동 재전송하지 않으므로 수동 재동기화/운영 재전송이 필요하다. [S-GH-RETRY](../reference/SOURCES.md#s-gh-retry)

사용자가 결과 화면을 닫으면 반드시 즉시 완료된다고 약속하지 않는다. UI에는 대기·마지막 처리 시각·재시도 버튼을 제공한다. 유휴 제한을 회피하려는 가짜 지속 트래픽을 만들지 않는다.

외부 DB/GitHub/LLM 통신도 무료 한도와 비용을 소비할 수 있으므로 사용량을 측정한다. 무료 정책은 배포 직전 다시 확인한다. 지속적인 자동 분석·기업 비공개 코드 처리가 목표가 되면 상시 Web/Worker와 격리를 갖춘 유료/자가 호스팅 배치로 바꾼다. 지금 당장 결제나 이전을 요구하는 결정은 아니다.

## CI/CD 제안

PR: docs validate → lint/type → unit → PostgreSQL integration → Docker build. 보호 branch merge: 같은 검증 통과 → 단일 migration → Render deploy → health/auth/Job smoke test. 테스트 전에 deploy hook을 호출하지 않는다. CI token과 Render deploy secret은 저장소 secret으로 관리한다.

운영 DB에 PR 테스트를 실행하지 않는다. 재배포 때 expired lease 회수와 정상 결과 조회를 확인한다. migration 실패 시 앱 rollout을 멈추고 복구 절차를 기록한다.

## 배포 완료 판정

네 언어 fixture와 100파일 상한 입력의 실제 피크 메모리, Parser timeout kill, 동시 HTTP 응답, 강제 재시작 Job 복구, HMAC Webhook, OAuth Cookie 프록시, DB 지속성을 측정/검증한다. 로컬/CI 결과와 실제 공개 환경 검증을 구분한다.

## 배포 전 production 계약

[ADR-DEPLOY-002](../adr/deployment/ADR-DEPLOY-002-production-boundary.md)에 따라 production은 동일한 HTTPS frontend origin을 PUBLIC_APP_ORIGIN과 PUBLIC_API_ORIGIN에 사용한다. DB는 sslmode=verify-full, 앱 쿠키는 Secure·HttpOnly, API 응답은 CDN을 포함한 no-store를 적용한다. 운영 키는 로컬 개발 키와 분리한다. 비밀값을 이미지·Git·프론트 변수에 포함하지 않는다.

Docker는 비root·단일 worker·접근로그 OFF·PORT·health를 지원한다. migration은 별도 단계이며 실패하면 rollout 중지, schema 호환성이 확인된 이전 이미지로만 복귀한다. 백업은 별도 DB에 복원해 검증한 뒤 전환한다. 실제 주소/플랜/DB/CA 확정과 최초 배포는 사용자 후속 결정이다.

설정 근거: [Render Blueprint](https://render.com/docs/blueprint-spec), [Vercel rewrites](https://vercel.com/docs/routing/rewrites), [Vercel cache headers](https://vercel.com/docs/caching/cache-control-headers). 2026-09-27 문서 확인; 클라우드에서의 실행 검증은 별도다.
