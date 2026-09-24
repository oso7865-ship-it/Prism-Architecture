# ADR-INTEGRATION-001: 실제 GitHub 연동과 PR 동기화

> ID: `ADR-INTEGRATION-001` · 소유: `INTEGRATION` · 기준: `2026-09-25`
> 읽는 때: 이 영역의 결정 배경이나 대체 여부를 검토할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: D-004, C-003, D-010
- 대체하는 ADR: 없음
- 대체한 ADR: 없음

## 배경

사용자의 명시적 선택 또는 기존 결정 기록을 이관한다. 아래 대안은 기존 기록과의 대비이며 실제 벤치마크나 당시의 상세 논의를 재구성한 것이 아니다.

## 결정

실제 OAuth/GitHub App 연동을 계획한다. 기존 PR은 조회·선택 분석하고 새 PR 이벤트는 정책에 따라 접수한다. GitHub 실패 Webhook 자동 재전송을 전제하지 않는다.

## 대안

과거 전체 PR 자동 분석과 모든 누락 이벤트의 완전 재생은 MVP에서 제외한다.

## 영향과 한계

등록·설치 권한 설정은 미완료다. OAuth/App 분리와 최근 갱신 PR 30개는 기존 설계 기준이며 내부 retry와 수동 재동기화를 구분한다.

## 소유 문서와 검증

- [소유 문서: domain/auth/README.md](../../domain/auth/README.md)
- [소유 문서: domain/pull_request/SYNC_POLICY.md](../../domain/pull_request/SYNC_POLICY.md)
- [소유 문서: domain/webhook/README.md](../../domain/webhook/README.md)

문서 이관의 링크·ID·영역 매핑을 검증한다. 애플리케이션 구현·연동·성능 검증은 각 소유 문서의 테스트 기준을 적용하며 이 ADR 작성으로 완료 처리하지 않는다.
