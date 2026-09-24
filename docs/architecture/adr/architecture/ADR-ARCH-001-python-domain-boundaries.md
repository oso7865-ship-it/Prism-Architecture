# ADR-ARCH-001: Python과 업무 소유권 중심 구조

> ID: `ADR-ARCH-001` · 소유: `ARCH` · 기준: `2026-09-25`
> 읽는 때: 이 영역의 결정 배경이나 대체 여부를 검토할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: D-001, D-005, C-001, C-006
- 대체하는 ADR: 없음
- 대체한 ADR: 없음

## 배경

사용자의 명시적 선택 또는 기존 결정 기록을 이관한다. 아래 대안은 기존 기록과의 대비이며 실제 벤치마크나 당시의 상세 논의를 재구성한 것이 아니다.

## 결정

Python 백엔드와 domain/shared 경계를 유지한다. 다른 도메인은 api.py로만 접근한다. Global의 실제 패키지는 Python 예약어를 피해 shared로 둔다. 같은 도메인의 Service→Repository는 정상이며 Router→Repository 직접 접근을 제한한다.

## 대안

재사용되는 업무 타입을 모두 shared로 이동하는 방식은 소유권을 흐린다. app/global은 일반 Python import 문법과 충돌한다.

## 영향과 한계

도메인 간 공개 계약과 조립 계층이 필요하다. 모듈형 모놀리스의 실행 배치는 별도 설계 기본값이며 아직 구현되지 않았다.

## 소유 문서와 검증

- [소유 문서: CORE.md](../../CORE.md)
- [소유 문서: PACKAGE_RULES.md](../../PACKAGE_RULES.md)
- [소유 문서: runtime/BOOTSTRAP.md](../../runtime/BOOTSTRAP.md)

문서 이관의 링크·ID·영역 매핑을 검증한다. 애플리케이션 구현·연동·성능 검증은 각 소유 문서의 테스트 기준을 적용하며 이 ADR 작성으로 완료 처리하지 않는다.
