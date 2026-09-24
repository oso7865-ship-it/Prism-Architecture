# ADR-REVIEW-001: 정적 Finding과 선택적 AI 설명 분리

> ID: `ADR-REVIEW-001` · 소유: `REVIEW` · 기준: `2026-09-25`
> 읽는 때: 이 영역의 결정 배경이나 대체 여부를 검토할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: D-007, C-007
- 대체하는 ADR: 없음
- 대체한 ADR: 없음

## 배경

사용자의 명시적 선택 또는 기존 결정 기록을 이관한다. 아래 대안은 기존 기록과의 대비이며 실제 벤치마크나 당시의 상세 논의를 재구성한 것이 아니다.

## 결정

LangChain으로 정적 Finding의 선택적 설명을 제공한다. AI가 Finding·Severity를 변경하거나 자동 수정하지 않는다. 현재 단일 소비자인 review가 provider factory를 소유한다.

## 대안

AI를 규칙 판정자로 쓰거나 소비 도메인 없이 shared/llm을 만드는 방식은 채택하지 않는다.

## 영향과 한계

정적 분석과 AI 상태를 분리한다. FINDINGS_ONLY·기본 OFF·호출 한도는 기존 설계 기본값이며 실행 검증은 남아 있다.

## 소유 문서와 검증

- [소유 문서: domain/review/README.md](../../domain/review/README.md)
- [소유 문서: operations/SECURITY_PRIVACY.md](../../operations/SECURITY_PRIVACY.md)

문서 이관의 링크·ID·영역 매핑을 검증한다. 애플리케이션 구현·연동·성능 검증은 각 소유 문서의 테스트 기준을 적용하며 이 ADR 작성으로 완료 처리하지 않는다.
