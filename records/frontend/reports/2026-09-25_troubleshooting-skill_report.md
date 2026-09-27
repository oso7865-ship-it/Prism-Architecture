# 작업 리포트: 트러블슈팅 기록 스킬 보강

> 작성일: 2026-09-25
> 패키징/배포일: 해당 없음
> 작업 브랜치: main
> 커밋/PR: 미커밋
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-25T15:35:09+09:00
> 구현 상태: 완료
> 구현 근거: troubleshooting-report 신설 및 인덱스·Report·복구 연결의 working-tree diff
> 로컬 검증 상태: 완료
> 로컬 검증 대상: 2757f717c12d594e748ba2e090d23900449316be 이후 이번 스킬 문서 working-tree 변경
> 로컬 검증 근거: 하네스 구조·문서·스킬·참조·최신성·개인 경로 및 strict 작업 기록 검사 종료 코드 0. 범위·제한은 §3 참조
> 병합 상태: 미수행
> 병합 대상: origin/main
> 병합 근거: 이번 변경은 로컬 미커밋 수정이며 Git 쓰기 미수행
> 배포 상태: 해당 없음
> 배포 근거: 서비스 구현을 변경하지 않는 스킬 문서 작업
> 실제 연동 상태: 해당 없음
> 실제 연동 근거: 외부 서비스 호출·운영 장애 재현을 포함하지 않음
> 작업 범위: L
> 적용 스킬: skill-scout, report-consistency, terminal-ops, troubleshooting-report
> 적용 Gate: Skill Gate, Document Gate
> 위험도: 구조
> 위험 작업 여부: 예

## 0. 작업 범위 확인

사용자의 트러블슈팅 스킬 보강 요청을 근거로 여섯 항목을 기록하는 스킬과 기존 하네스 연결을 변경한다. GateGuard §6-1의 구조 작업 근거는 해당 사용자 요청이다. 되돌릴 기준은 2757f717c12d594e748ba2e090d23900449316be. 제품 코드·DB/FK·원격 Git·배포는 변경 범위에서 제외한다.

## 1. 작업 요약

Skill Scout 판정 PASS: agent-recovery는 복구 수행, error-handling은 응답 설계, report-consistency는 최신성을 담당한다. 사후 원인 분석·실패 시도·후속 조치 인계는 별도 산출물이므로 troubleshooting-report를 추가했다. 활성 스킬은 21개다. 기존 06 Report 헤더와 게시 절차를 재사용한다.

## 2. 변경 파일

- GENERAL_HARNESS/skills/troubleshooting-report/SKILL.md: 여섯 항목·가설/사실·검증·후속 조치 형식.
- GENERAL_HARNESS/02.SKILL_INDEX.md, 06.REPORT_TEMPLATE.md, skills/agent-recovery/SKILL.md: 발견과 인계 연결.
- GENERAL_HARNESS/05.WORKING_CONTEXT.md 및 최신 포인터: 현재 수량·기록 연결.
- PROJECT_HARNESS/manifest.json: 버전 1.0.1, 미커밋 패치를 localChanges에 명시. 원본 기준 SHA는 유지.

## 3. 검증 결과

| 검증 항목 | 결과 | 근거 |
|---|---|---|
| validate-harness / validate-docs / validate-skills | PASS | 필수 구조·Markdown·스킬 21개 검사 종료 코드 0 |
| validate-references / validate-report-consistency / validate-no-personal-paths | PASS | 참조·최신 포인터·스킬 집합·개인 경로 검사 종료 코드 0 |
| validate-work-records --project-root . --reports 대상폴더 --strict --json | PASS | 현재 보고서·단계별 상태 선언 검사, findings 0 |
| git diff --check | PASS | 추적 파일 변경의 공백 오류 없음 |
| skill-creator quick_validate.py | WARN | 실행 시 PyYAML 부재(ModuleNotFoundError: yaml). 기본 및 번들 Python에서 동일. 설치하지 않았으며 이 검사 PASS를 주장하지 않음 |

스킬 frontmatter의 name/description·이름 형식은 수동 확인했다. 자동 검사는 구조만 확인하며 실제 에이전트 장기 준수 효과를 보장하지 않는다. 제품 앱 코드는 변경하지 않아 제품 테스트·CI 재실행은 범위 밖이다. 원본 최초 strict 검사의 포인터 갱신 전 WARN은 최신 포인터 게시 후 동일 검사 PASS로 해소했다.

부착 어댑터 검사(validate-project-adapter --project-root . --require-adapter --strict --json) PASS: 버전 1.0.1, 출처·로컬 변경 선언 정상.

## 4. Checklist 결과

수동 Skill Gate/Document Gate 검수: 요청의 여섯 항목, 일반 오류의 과도한 발동 방지, 가설·확정 원인 분리, 검증 범위, 미정 후속 조치, 미요청 외부 작업 금지 확인. 기록 품질 PASS와 장애 해결 완료를 분리한다.

## 5. 발견된 문제

기존 복구 출력만으로는 발생 위치·인과관계·장기 예방책을 일정한 형식으로 인계하기 어려웠다. 신규 스킬로 보완했다.

### 트러블슈팅: Vitest가 하네스 테스트를 수집해 CI 실패

- 사건 상태: 해결 검증 완료(기존 기록 기준, 이번 작업에서 재실행하지 않음)
- 원인 상태: 확인(기존 Report와 현재 설정 대조)
- 근거: [기존 개발 기반 Report](2026-09-25_foundation_report.md), 구현 커밋 e3bc636.

#### 어디서 발생했나

PRism-Frontend GitHub Actions의 Vitest 단계. 기존 기록의 성공 검증 환경은 Node 24이며 정확한 최초 발생 시각·실패 환경의 세부 버전은 미확인. 제품 테스트는 tests, 하네스 node:test 파일은 GENERAL_HARNESS 아래에 있다.

#### 어떤 문제가 있었나

제품 Vitest 테스트만 실행되어야 했으나 하네스 node:test 파일까지 수집해 CI가 실패했다. [최초 실패 run](https://github.com/oso7865-ship-it/Prism-Frontend/actions/runs/36039592514)은 기존 Report에 기록되어 있다. 영향은 개발 CI 검증 실패이며 운영 사용자 영향·지속 시간은 확인 자료가 없다. 정확한 stderr 원문은 기존 Report에 없어 인용하지 않는다.

#### 어떻게 발생했나

하네스를 포함한 프론트엔드 저장소에서 제품 범위를 제한하지 않은 Vitest 수집이 수행되어 서로 다른 테스트 실행기의 파일이 섞였다. 이번에는 오류 설정으로 되돌리는 재현을 하지 않았다. 발생 횟수는 미확인이다.

#### 왜 발생했나

직접 원인은 Vitest의 수집 범위가 제품 테스트로 제한되지 않은 점이다. 하네스에 다른 실행기용 테스트가 함께 존재한 것이 촉발 조건이다. 기존 Report의 실패 분석과 현재 vitest.config.ts의 tests/**/*.test.ts 제한을 대조했다. 추가 가설을 검증하거나 배제한 기록은 없다.

#### 어떻게 해결했나

| 순서 | 시도와 이유 | 변경 위치·내용 | 결과·증거 |
|---|---|---|---|
| 1 | 실행기별 수집 범위를 분리 | vitest.config.ts의 test.include를 tests/**/*.test.ts로 지정 | 기존 Report에 수정 후 제품 테스트 3개 및 CI 통과 기록 |

제품 테스트 파일만 Vitest가 수집하므로 하네스 테스트와의 충돌 조건을 없앴다. 이 수집 충돌에 대한 근본 수정이며, 하네스 파일을 삭제해 우회한 것은 아니다. 다른 실패한 해결 시도는 기록에 없어 만들어 적지 않는다.

검증 근거는 [수정 후 CI](https://github.com/oso7865-ship-it/Prism-Frontend/actions/runs/36039823516) 성공에 대한 기존 Report다. 타입 검사·빌드·Vitest 3개 통과가 기록되어 있다. 이번 작업은 과거 기록의 형식 적용이며 원격 run 재조회나 앱 검증 재실행을 하지 않았다. 그 CI 결과가 모든 하네스 테스트 실행까지 보증하지는 않는다.

#### 앞으로 어떻게 대응하나

| 조치 | 원인과의 연결 | 담당자 | 기한/실행 조건 | 완료 기준 | 상태 |
|---|---|---|---|---|---|
| 제품 테스트 수집 범위 명시 | 다른 실행기용 파일 혼입 방지 | PRism 프론트엔드 유지관리자 | 적용됨 | 현재 include 설정 및 기존 CI 성공 기록 | 완료 |
| 테스트 폴더 추가·실행기 변경 시 수집 범위 재검토 | 새 제품 테스트가 누락되거나 하네스 파일이 다시 혼입될 가능성 | 미정 | 테스트 경로·실행기 변경 시 | 의도한 제품 테스트 포함 및 하네스 파일 미수집 확인 | 제안 |
| 재발 시 CI job·수집 파일 목록과 설정 diff 확인 | 같은 증상과 다른 원인을 구분 | 미정 | 같은 수집 실패 재발 시 | 원인·해결·검증을 사건별 Report에 기록 | 제안 |

## 6. 미해결 항목

quick_validate.py는 PyYAML 사용 가능한 환경에서 추가 확인할 수 있다. 이번 변경의 커밋·push·공식 반영은 미수행. 원본 로컬 패치와 두 부착 사본은 같은 스킬 본문을 사용한다. 원본 반영 후 실제 새 커밋을 기준으로 사본 출처를 갱신할 수 있다.

## 7. Working Context 반영 여부

활성 스킬 수 21개로 갱신. 제품 사본에는 미커밋 수동 패치임을 기록한다. 이전 개발 기반/플로우차트 Report는 별도 작업의 증거로 유지하며 그 검증 결과를 새 검증처럼 쓰지 않는다.

## 8. 다음 작업

실제 장애 발생 시 여섯 항목으로 기록한다. 기존 업무 구현 큐는 유지한다. Git 반영 시 원본·사본의 커밋 상태와 출처를 함께 갱신한다.
