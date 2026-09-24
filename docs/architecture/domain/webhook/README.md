# Webhook: 검증·수신 보존·이벤트 처리

> ID: `WEBHOOK` · 소유: `backend/app/domain/webhook` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: Webhook 수신·서명·이벤트 handler를 변경할 때

## 책임과 구조

```text
webhook/
├─ router.py                원문 bytes 수신·상한 확인
├─ verifier.py              GitHub HMAC 검증
├─ service.py               검증된 최소 이벤트의 원자적 접수
├─ repository.py
├─ models.py                WebhookDelivery
├─ jobs/process_delivery.py 영속 처리 handler
├─ handler/
│  ├─ pull_request.py
│  └─ installation.py
├─ dto.py
├─ exceptions.py
└─ schema/github_event.py
```

HMAC은 여러 도메인이 쓰지 않고 GitHub Webhook의 특정 프로토콜에 속하므로 이 도메인에 둔다. 공통 constant-time 비교/비밀 키 로딩만 shared security를 사용한다.

## 수신 순서

`POST /webhooks/github`에서 크기 제한을 적용한 **원문 bytes**를 읽고 `X-Hub-Signature-256`의 HMAC-SHA256을 검증한다. JSON 재직렬화 후 서명을 계산하지 않는다. `hmac.compare_digest`로 비교하고 헤더 누락/형식 오류/서명 불일치는 거부한다. 그 뒤 JSON을 검증한다. [S-GH-HMAC](../../reference/SOURCES.md#s-gh-hmac)

서명은 공유 Secret을 가진 발신자와 본문 무결성을 확인하는 수단이다. 특정 Workspace에 대한 권한까지 증명하지 않는다. 설치/저장소 ID를 등록된 연결에 매핑하고 현재 연결 상태를 확인한다. 요청 Body의 workspace_id는 신뢰하지 않는다.

트랜잭션에서 `(provider, delivery_id)` UNIQUE로 WebhookDelivery를 insert하고 최소 식별자만 든 Job을 함께 insert한다. 커밋 후 `202`로 응답한다. 이미 저장한 중복은 `200`으로 수신만 확인한다. DB 저장 실패에는 성공 응답을 보내지 않는다. 정상 검증을 통과한 미지원 이벤트는 `204`로 무시한다.

GitHub는 10초 이내 2xx 응답을 요구하므로 응답 전에 GitHub 재조회·분석·LLM 호출을 하지 않는다. 내부 응답 목표는 2초 이하이지만 무료 배포의 cold start는 이 목표를 보장하지 못한다. [S-GH-WEBHOOK](../../reference/SOURCES.md#s-gh-webhook)

## 데이터·멱등성

Delivery에는 delivery_id·event/action·installation/repository/PR 식별자·본문 SHA256·수신/처리 시각·상태·공개 error_code만 저장한다. 원문 payload·PR body·token·diff는 저장하지 않는다. 본문 해시는 무결성 보조 기록이며 raw body 보관 대체다.

단순 `exists()` 후 insert는 경쟁에 취약하므로 DB UNIQUE와 충돌 처리를 사용한다. 접수 성공 후 handler 실패는 **내부 Job 재시도**로 처리한다. 중복 delivery 응답이 내부 실패를 처리 완료로 바꾸지 않는다. 같은 PR snapshot이 다른 delivery_id로 들어오는 경우는 analysis의 실행 키로 한 번 더 중복을 막는다.

GitHub 재전송은 원래 delivery_id를 재사용한다. 실패 이벤트는 자동으로 다시 온다고 가정하지 않는다. 운영자가 GitHub에서 재전송하거나 앱이 재동기화해야 한다. [S-GH-WEBHOOK](../../reference/SOURCES.md#s-gh-webhook), [S-GH-RETRY](../../reference/SOURCES.md#s-gh-retry)

## 처리와 실패

PR handler는 pull_request 공개 계약으로 현재 메타데이터를 갱신한 다음 [이벤트 정책](../pull_request/SYNC_POLICY.md)에 따라 analysis 공개 계약을 호출한다. installation handler는 repository 공개 계약으로 연결을 제한한다. 타 도메인 테이블을 직접 수정하지 않는다.

Job 시작과 마지막 결과 저장 전에 설치·연결 상태를 다시 확인한다. 연결이 해제되면 CANCELED/IGNORED 처리하고 후속 분석을 만들지 않는다. 민감 데이터는 로그·실패 메시지에도 남기지 않는다.

## 검증

본문 한 바이트 변조, 원문 공백 차이, 서명 누락, body 상한, 중복 동시 수신, DB commit 실패, 재전송, 역순 이벤트, 위조 설치 ID, 내부 실패 뒤 재시도를 통합 테스트한다.
