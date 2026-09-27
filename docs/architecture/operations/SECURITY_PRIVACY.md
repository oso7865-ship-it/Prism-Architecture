# 보안 경계와 데이터 보관

> ID: `PRIVACY` · 소유: `cross-cutting-security` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 소스 처리·외부 반출·보관·삭제·테넌트 방어를 변경할 때

## 제품의 보안 주장 범위

AI OFF라도 hosted backend는 분석을 위해 소스를 읽는다. 'LLM에 코드를 안 보낸다'와 '회사 코드가 외부로 나가지 않는다'는 다르다. private 저장소 연결 전에 처리 위치·저장 항목·외부 Provider를 고지한다. Secret scanner가 모든 민감정보를 찾아내거나 기업 보안 심사를 대체한다고 말하지 않는다.

## 데이터 정책

| 데이터 | 처리/보관 기본값 — 설계 제안 |
|---|---|
| 소스·Diff·AST·PR 본문·사람 리뷰 원문 | bounded memory/임시 작업만, DB·로그 보존 금지 |
| PR metadata·경로·Finding·검증된 AI 설명 | 활성 Workspace의 비공개 데이터, 생성/최근 갱신 후 90일 |
| Job·WebhookDelivery·SyncRun 기술 기록 | terminal 후 30일 |
| 실행 중 Job·그 부모 데이터 | terminal 처리 전 cleanup 제외 |
| OAuth code/token·LLM key·App private key | code/token은 목적 수행 후 폐기, 서버 키는 비밀 설정만 |
| 만료 LoginAttempt/초대/RefreshSession | domain 만료 후 정리; 감사용 최소 철회 metadata만 30일 |
| 운영 로그 | 운영자가 설정 가능한 범위에서 14일을 목표, Provider 정책 별도 확인 |

위 기간은 법적 보존 의무의 판단이 아니라 MVP 운영 기본값이다. 상용 공개 전 서비스/Provider의 실제 저장·백업·삭제 정책을 검토해야 한다. DB backup에는 삭제 전 데이터가 남을 수 있으므로 '즉시 모든 사본 삭제'라고 약속하지 않는다.

## 연결 해제와 삭제

저장소 해제는 즉시 DISCONNECTED, 새 취득/분석 금지, 대기 Job 취소, 실행 중 Job의 다음 접근/저장 차단으로 처리한다. 기존 보고서는 팀 권한 안에서 보관 기간까지 유지한다. '연결 해제'를 '모든 데이터 즉시 삭제'라고 표시하지 않는다.

MVP는 Workspace/회원 영구 삭제 자동화를 제공하지 않는다. 외부 공개 이전에는 운영자의 안전한 삭제 절차와 retention cleanup을 구현하고 검증해야 한다. 이를 완료하지 않은 시연은 테스트/허가된 저장소로 한정한다.

## 입력·실행 방어

Webhook body, GitHub 파일, 파서 프로세스 출력, PR comment, LLM 입력/출력에 각각 크기 제한을 둔다. Webhook body 초기 상한은 2 MiB로 제안하며 초과는 413과 운영 진단으로 남긴다. 처리 못 한 큰 이벤트는 재동기화로 보완하며 수신 완료로 위장하지 않는다.

사용자 코드를 exec/eval/import하지 않는다. Maven/npm/pip·Git hook·user plugin을 실행하지 않는다. 원격 설정 파일의 명령/URL/무제한 정규식을 신뢰하지 않는다. 프롬프트 인젝션을 막으려는 문구만으로 안전하다고 간주하지 않고 LLM 도구 권한 자체를 제거한다.

Secret Finding은 raw match를 저장·전송하지 않는다. 코드/PR/로그를 통해 들어온 테스트 canary가 DB·HTTP·관측·AI 네트워크로 새지 않는지 검사한다. AI 정책의 구체적 범위는 [Review](../domain/review/README.md)를 따른다.

선택적 로컬 리랭커도 안전한 소스 후보만 메모리에서 처리한다. 모델 데이터는 설치 시 공식 revision/해시로 고정하고 요청 중 다운로드·원격 Python 실행을 하지 않는다. 원문 로그/질의 저장/외부 tracing을 끄고 별도 CPU 컨테이너·loopback 포트·입출력/자원/동시성 한도를 적용한다. loopback 공개 범위와 컨테이너 외부 통신 차단은 다른 통제이며, 별도 egress 차단을 검증하지 않았다면 네트워크 격리를 보장한다고 말하지 않는다. 점수는 사실성·코드 보안 검증이 아니다.

## 테넌트와 남는 위험

UI·API·Job·cache/dedupe key에 Workspace 경계를 적용한다. Worker도 권한/설치 상태를 다시 확인한다. 팀 결과 공유는 GitHub 개인 권한과 별개 정책임을 고지한다.

HMAC이 유효해도 replay/업무 권한 검사를 생략하지 않는다. delivery_id와 업무 실행 키로 중복을 제어하되 보관 기간 밖의 영구 replay 차단을 주장하지 않는다. 무료 공용 컨테이너의 Parser subprocess를 기업용 보안 sandbox라고 소개하지 않는다.

## 검증과 운영

secret 유출, 소스 오보관, cross-tenant 접근이 발견되면 관련 기능/외부 호출을 먼저 차단하고 접근 키/로그/저장 자료의 영향 범위를 조사한다. 사용자를 안심시키기 위한 근거 없는 '유출 없음' 선언을 하지 않는다. 감사 기록은 최소 식별자와 변경 종류만 남긴다.

현재 AI 전송 예산/두 단계 검증은 [ADR-REVIEW-010](../adr/review/ADR-REVIEW-010-evidence-first-verified-review.md)을 따른다. 최대16KiB/파일·48KiB 코드 JSON과 검증용 초안 최대24,000byte를 전송할 수 있다. 각 호출 직전 동의된 리뷰 권한·연결 세대·취소·lease를 확인하고 예약한다. 원문/초안/검증 응답을 로그/DB에 보관하지 않는다. 검증도 같은 외부 제공자를 사용하며 화면 동의·사용 한도에 두 번의 전송을 명시한다.
