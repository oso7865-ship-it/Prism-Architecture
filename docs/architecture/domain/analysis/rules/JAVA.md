# Java Rule 8개 — 초기 구현 대상

> ID: `RULES-JAVA` · 소유: `backend/app/domain/analysis/rule/java` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: Java 전용 Rule을 구현·변경할 때

이 목록은 Java 컴파일/타입 검사기를 대체하지 않는다. 구문과 명시적 로컬 선언으로 확인 가능한 범위만 다룬다. [언어 경계](../LANGUAGES.md), [Rule Engine](../RULE_ENGINE.md)을 따른다.

| ID | 검출 조건 | 기본 Severity / Confidence | 제한 |
|---|---|---|---|
| JAVA-001 | 로컬에서 Optional 타입을 확인한 변수의 get 호출 | WARNING / MEDIUM | '무조건 오류'가 아닌 안전성 확인 제안; 전역 타입 미추론 |
| JAVA-002 | 필드의 명시적 Spring Autowired annotation | WARNING / HIGH | Spring annotation import/FQN 확인 |
| JAVA-003 | System.out/System.err 출력 호출 | INFO / HIGH | 프로젝트 운영 로그 정책 제안 |
| JAVA-004 | 빈 catch block | WARNING / HIGH | comment만 있는 경우도 기본 포함 |
| JAVA-005 | wildcard import | INFO / HIGH | 코드 스타일 정책 |
| JAVA-006 | 빈 statement를 body로 갖는 반복문 | WARNING / HIGH | 의도적 busy-wait일 수도 있음 |
| JAVA-007 | public static 이며 final이 아닌 필드 | WARNING / HIGH | mutable global state 후보 |
| JAVA-008 | 한쪽이 문자열 literal인 ==/!= 비교 | WARNING / MEDIUM | 의도적 참조 비교 가능, equals 필요 여부 확인 |

JAVA-001은 다른 객체의 get, shadowing, 타입 확인 실패를 검출하지 않는다. 해당 코드가 이미 isPresent 등으로 보호됐는지를 완전한 control-flow 검증 없이 단정하지 않는다. 메시지는 '직접 get 사용; 보호 조건 확인 필요'이며 '반드시 예외 발생'이 아니다.

JAVA-002의 @Autowired와 동명의 사용자 annotation을 구별하지 못하면 미평가한다. JAVA-003은 Java의 실제 System 또는 명확한 FQN 범위만 다룬다. 정확한 해석이 불가능한 경우 높은 confidence를 남기지 않는다.

필수 fixture는 정상·위반 외에도 동명 타입/메서드·이미 guard된 Optional·의도적 빈 loop·문자열 literal의 참조 비교 반례를 포함한다. Field injection과 wildcard import는 금지된 언어 문법이 아니라 선택한 품질 정책임을 표시한다.
