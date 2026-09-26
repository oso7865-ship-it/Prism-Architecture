# PR 동기화 정책

> ID: `PR-SYNC` · 소유: `backend/app/domain/pull_request/sync_service.py` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: PR 동기화·Webhook 이벤트 정책을 변경할 때

## 최초·수동 동기화

저장소 최초 연결은 `state=all, sort=updated, direction=desc, per_page=30`으로 **최근 갱신된 PR 30개**를 가져온다. '최근'은 생성순이 아니라 갱신순이다. 처음에는 메타데이터만 저장하며 자동 분석하지 않는다. 오래된 PR은 다음 페이지 또는 PR 번호 직접 조회로 불러온다. GitHub endpoint의 정렬/상태 옵션과 pagination을 따른다. [S-GH-PR](../../reference/SOURCES.md#s-gh-pr)

동기화는 `PullRequestSyncRun`과 영속 Job을 함께 생성하고 `202`를 반환한다. cursor·last_success_at·error_code를 기록한다. 초기 전체 목록을 매 요청에서 재다운로드하지 않는다.

## 이벤트별 동작

| 이벤트 | PR 갱신 | 자동 분석 |
|---|---|---|
| opened / reopened / synchronize | 실행 | non-draft이고 자동 분석 허용이면 접수 |
| ready_for_review | 실행 | 허용이면 접수 |
| converted_to_draft | 실행 | 새 자동 분석 접수 안 함 |
| closed | 실행, merged 여부도 확인 | 접수 안 함 |
| edited | 실행 | base SHA가 달라졌으면 허용 시 접수 |
| review/comment 관련 이벤트 | MVP 미구독, 상세 화면에서 조회 | 없음 |

일반 push와 pull_request synchronize를 동시에 분석 트리거로 쓰지 않는다. PR 없는 branch 전체 분석은 확장 후보다. 사용자의 명시적 수동 분석은 draft/closed PR도 허용하며 접근과 snapshot 가용성을 검증한다.

## 순서 뒤바뀜과 누락

Webhook 도착 순서를 GitHub 상태 변경 순서로 믿지 않는다. Job은 이벤트의 PR 식별자로 GitHub 현재 상태를 재조회하여 upsert하고 `updated_at`이 더 오래된 데이터로 현재 레코드를 되돌리지 않는다. 같은 updated_at인데 SHA가 다르면 재조회/충돌 기록을 한다. 대기 중 여러 synchronize는 최신 snapshot 한 건으로 합칠 수 있다.

**모든 중간 commit의 분석을 보장하지 않는다.** 수신되지 않은 이벤트나 합쳐진 commit은 이력에 없을 수 있다. 이미 생성한 Analysis 행은 유지하고 새 snapshot은 새 Analysis를 만든다. SHA 문자열의 사전순으로 '최신'을 판단하지 않는다.

GitHub는 실패한 Webhook을 자동 재전송하지 않는다. Render 무료 서비스가 잠든 동안 누락될 수 있으므로 화면의 `동기화` 버튼과 서비스 재기동 후 최근 목록 재조회로 현재 상태를 복구한다. 이 복구도 전 과거 이벤트 재생은 아니다. [S-GH-RETRY](../../reference/SOURCES.md#s-gh-retry), [Render 제약](../../operations/RENDER.md)

## 비용/실패

같은 저장소의 활성 동기화는 한 건으로 합친다. `ETag/If-None-Match`, pagination, rate-limit 응답을 처리한다. Retry-After/한도 복구 시각을 Job available_at에 반영하고 장시간 sleep하지 않는다. 401/403은 무조건 재시도하지 말고 토큰 만료·권한 철회·rate limit을 구별한다. [S-GH-RATE](../../reference/SOURCES.md#s-gh-rate)

합치기는 같은 모드·대상·cursor·연결 세대 요청에 한정한다. 다른 범위를 요청하면 409 SYNC_IN_PROGRESS로 현재 작업 종료 후 재시도를 안내한다. PR metadata는 확인한 연결 세대를 함께 저장하며 재연결 뒤 이전 세대 metadata로 바로 분석을 접수하지 않는다. [물리 저장 계약](../../contracts/schema/GITHUB.md)

동기화 실패가 기존 PR 목록을 지우지 않는다. UI에 마지막 성공 시각과 오래된 데이터 경고를 보여준다. 기존 PR 전체를 자동 LLM 처리하는 기능은 없다.

## 필수 검증

최초 30개 분석 미생성, synchronize 중복 분석 방지, 업데이트 역순, draft 전환, 머지 상태, 304, rate limit, 실패 뒤 기존 데이터 유지, 수동 재동기화, 접근 불가능한 과거 SHA를 확인한다.

현재 구현의 페이지 입력과 cursor 저장 형식은 [ADR-INTEGRATION-002](../../adr/integration/ADR-INTEGRATION-002-verified-app-connection.md)를 따른다. 단건/페이지 scope별 ETag 재사용은 같은 연결 세대의 성공 기록으로만 제한한다.
