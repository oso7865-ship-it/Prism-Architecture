# ADR-ARCH-004: 구현 저장소 README 게시 예외

> ID: `ADR-ARCH-004` · 소유: `ARCH` · 기준: `2026-10-06`
> 읽는 때: 구현 저장소 README 게시·문서 유입 검사를 변경할 때

- 상태: `ACCEPTED`
- 기록일: `2026-10-06`
- 근거: 사용자 “아키텍처와 프론트 백엔드에 리드미도 추가해줘, 면접관들이 본다는 생각으로”
- 대체하는 ADR: 없음. [ADR-ARCH-003](ADR-ARCH-003-central-documentation.md)의 “구현 저장소에 문서 없음” 원칙에 루트 `README.md` 하나만 예외를 둔다(ARCH-003은 유효).
- 대체한 ADR: 없음

## 배경

ADR-ARCH-003 이후 구현 저장소는 `*.md` 전체를 ignore하고 CI(`check-repository.mjs`)가 추적되는 문서를 실패 처리한다. 그 결과 GitHub에서 Prism-Backend·Prism-Frontend를 열면 README가 없어 제품이 무엇인지, 어떻게 실행하는지, 설계 근거가 어디 있는지 알 수 없다. 외부 사람(면접관 포함)이 가장 먼저 보는 곳은 구현 저장소의 첫 화면이다.

## 결정

각 구현 저장소의 **루트 `README.md` 한 파일만** Git에 올린다. `.gitignore`에 `!/README.md`를 추가하고 `check-repository.mjs`는 이름이 정확히 `README.md`인 추적 파일만 허용한다. 하위 폴더의 문서, `docs/`, `reports/`, 하네스는 기존대로 금지한다.

README는 제품 소개·아키텍처 요약·검증 방법·실행 방법·알려진 한계만 담고, 상세 설계와 결정은 Prism-Architecture로 링크한다. 설계 계약을 README에 복제하지 않는다. 개발 절차·작업 이력은 README에 두지 않는다. 이전 README는 [legacy](../../../../legacy/README.md)에 보존한다.

## 대안

- 아키텍처 저장소 README에만 설명하고 구현 저장소는 그대로 둔다: 구현 저장소를 직접 여는 사람은 여전히 안내를 받지 못한다.
- `.md` 금지 규칙을 완화한다: 상세 문서가 구현 저장소로 다시 유입되어 ARCH-003의 목적이 무너진다.

## 영향과 한계

README의 수치(테스트 수 등)는 시간이 지나면 낡는다. 작성 시점의 기록임을 문장에 밝히고 최신 상태는 CI와 아키텍처 저장소 보고서를 따른다. `restore-docs.mjs`가 복원하는 records의 구 README 사본과 내용이 다르다. 복원은 기존 파일이 있고 내용이 다르면 중단하는 기존 동작을 유지하므로, 복원 대상 목록에서 README를 제외하는 정리는 별도 작업이다.

## 소유 문서와 검증

[PACKAGE_RULES](../../PACKAGE_RULES.md)의 문서 게시 위치를 따른다. 두 구현 저장소의 `.gitignore`와 `scripts/check-repository.mjs`를 변경했고, README를 추적한 상태에서 `check-repository.mjs`가 통과함을 확인했다. 커밋·CI 실행은 이 ADR 시점에 하지 않았다.
