# 공통 Rule 10개 — 초기 구현 대상

> ID: `RULES-COMMON` · 소유: `backend/app/domain/analysis/rule/common` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 공통 Rule을 구현·변경할 때

모두 설계 제안이며 구현 완료 목록이 아니다. 결과 계약/활성화 기준은 [Rule Engine](../RULE_ENGINE.md)이 소유한다. 설정 필요한 Rule은 설정 없을 때 NOT_APPLICABLE이다.

| ID | 관찰/정책 | 기본 Severity / Confidence | 초기 동작 |
|---|---|---|---|
| COM-001 | 파일의 물리적 줄 수 > 500 | INFO / HIGH | 파일 단위 유지보수 신호 |
| COM-002 | 함수/메서드 시작~끝 span > 60줄 | WARNING / HIGH | 주석 포함 span임을 명시 |
| COM-003 | 조건/반복 중첩 깊이 > 4 | WARNING / HIGH | 블록 유형은 언어 extractor 기준 |
| COM-004 | 선언 인수 수 > 5 | WARNING / HIGH | Python self/cls 제외, 별표 가변 인수는 각 1개 |
| COM-005 | 설정에서 금지한 import 경로 | ERROR / HIGH | 확실히 해석한 import만 평가 |
| COM-006 | 설정 계층 방향 위반 | ERROR / HIGH | resolved target + layer mapping 필요 |
| COM-007 | 설정한 심볼 이름 규칙 불일치 | WARNING / HIGH | 클래스/함수별 정책 명시 |
| COM-008 | 설정한 폴더/파일 위치 불일치 | WARNING / HIGH | glob 정책만, 업무 소유권 추론 아님 |
| COM-009 | 알려진 credential 형식 패턴 일치 | CRITICAL / MEDIUM | 값은 저장/전송하지 않음 |
| COM-010 | private-key block 형식 발견 | CRITICAL / HIGH | 실제 키 유효성/노출 악용 가능성은 미검증 |

COM-009는 검증된 공급자 패턴 집합부터 시작한다. 고엔트로피 문자열 전체를 자동 비밀키라고 단정하지 않는다. COM-010과 같은 범위가 겹치면 더 구체적인 키 block Finding 하나를 남긴다.

COM-001~004는 코드 품질의 절대 판결이 아니다. 임계값과 줄 계산 방식을 설명하고 false-positive 반례를 둔다. 파일/함수 전체 관찰이므로 변경 줄 밖 근거는 CONTEXT/FILE로 표시한다.

경로 제외 설정은 소스 Rule 적용에만 기본 적용한다. Secret 검사를 끄거나 범위를 줄이는 변경은 OWNER 보안 정책에 따라 별도로 표시한다. '제외 파일이므로 안전함'을 보고하지 않는다.

필수 fixture: 지원 언어별 함수/인수/중첩, CRLF, 주석 많은 함수, 미해석 alias import, 설정 없는 Layer Rule, fake key placeholder, 실제와 유사한 비밀 형식의 마스킹 출력. 실사용 비밀키를 테스트 데이터로 사용하지 않는다.
