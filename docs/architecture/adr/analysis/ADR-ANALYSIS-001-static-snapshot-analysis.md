# ADR-ANALYSIS-001: 네 언어의 고정 Snapshot 정적 분석

> ID: `ADR-ANALYSIS-001` · 소유: `ANALYSIS` · 기준: `2026-09-25`
> 읽는 때: 이 영역의 결정 배경이나 대체 여부를 검토할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: D-003, C-004, C-005, D-012
- 대체하는 ADR: 없음
- 대체한 ADR: 없음

## 배경

사용자의 명시적 선택 또는 기존 결정 기록을 이관한다. 아래 대안은 기존 기록과의 대비이며 실제 벤치마크나 당시의 상세 논의를 재구성한 것이 아니다.

## 결정

Java·JavaScript·TypeScript·Python을 지원하고 Go는 제외한다. 고정 SHA의 전체 파일을 분석하며 Diff는 위치 자료로 사용한다. Tree-sitter는 구문 분석이며 타입 증명이 아니다. 규칙 정확도·문법 버전·자원 한도는 구현 후 검증한다.

## 대안

Diff 조각만 파싱하거나 구문 파싱을 전역 타입 분석으로 간주하는 방식은 채택하지 않는다.

## 영향과 한계

미해석은 NOT_EVALUATED, 누락 범위는 PARTIAL로 드러낸다. 초기 자원 수치와 Rule 38개는 측정·구현 완료가 아니다.

## 소유 문서와 검증

- [소유 문서: domain/analysis/PIPELINE.md](../../domain/analysis/PIPELINE.md)
- [소유 문서: domain/analysis/LANGUAGES.md](../../domain/analysis/LANGUAGES.md)
- [소유 문서: domain/analysis/RULE_ENGINE.md](../../domain/analysis/RULE_ENGINE.md)

문서 이관의 링크·ID·영역 매핑을 검증한다. 애플리케이션 구현·연동·성능 검증은 각 소유 문서의 테스트 기준을 적용하며 이 ADR 작성으로 완료 처리하지 않는다.
