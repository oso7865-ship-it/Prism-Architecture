# Python Rule 8개 — 초기 구현 대상

> ID: `RULES-PYTHON` · 소유: `backend/app/domain/analysis/rule/python` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: Python 전용 Rule을 구현·변경할 때

구문 관찰과 위험 가능성 안내를 분리한다. 실행·import 없이 평가하며 동명 함수 shadowing을 무시하고 built-in이라고 단정하지 않는다.

| ID | 검출 조건 | 기본 Severity / Confidence | 제한 |
|---|---|---|---|
| PY-001 | list/dict/set literal을 기본 인수로 사용 | WARNING / HIGH | 사용자 의도에 따른 공유 상태 가능 |
| PY-002 | 예외 타입 없는 bare except | WARNING / HIGH | 시스템 예외까지 포착 가능성 안내 |
| PY-003 | pass/빈 본문만 있는 except | WARNING / HIGH | 오류 삼키기 후보 |
| PY-004 | built-in으로 확인 가능한 eval 호출 | WARNING / MEDIUM | 입력의 공격자 통제 여부는 모름 |
| PY-005 | built-in으로 확인 가능한 exec 호출 | WARNING / MEDIUM | 임의 코드 실행 취약점 확정 아님 |
| PY-006 | from module import * | INFO / HIGH | 이름 공간/분석 가능성 정책 |
| PY-007 | async 함수에서 명확한 time.sleep 호출 | WARNING / HIGH | import alias 해석 가능한 경우만 |
| PY-008 | Exception/BaseException을 포괄적으로 catch | WARNING / MEDIUM | 최외곽 실패 경계에서는 의도적일 수 있음 |

같은 except에 PY-003과 PY-008이 겹치면 PY-003을 우선한다. bare except는 PY-002로 식별하고 PY-008은 명시적으로 Exception/BaseException을 쓴 경우만 해당한다. 여러 Finding이 같은 근거를 과장하지 않게 한다.

PY-007은 변수명이 sleep이라는 이유만으로 경고하지 않는다. `from time import sleep as pause`, 사용자 정의 sleep, shadowing을 구별할 fixture를 둔다. with/await/close의 전체 자원 수명 추론은 MVP에서 하지 않는다.

필수 fixture: mutable literal vs None/tuple, 의도적인 mutable cache, alias/shadowing, 예외 경계의 로깅 후 재발생, BaseException 정상 사용 사례, eval 문자열 literal와 외부 입력 구별 한계를 포함한다.
