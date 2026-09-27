# 작업 리포트: AI 리뷰 근거 표시

> 작성일: 2026-09-27
> 패키징/배포일: 해당 없음
> 작업 브랜치: dev
> 커밋/PR: 미커밋
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-27T00:07:11+09:00
> 구현 상태: 완료
> 구현 근거: 작업 트리의 policy/analyzer 또는 AIReviewEvidence 변경 및 회귀 테스트
> 로컬 검증 상태: 완료
> 로컬 검증 대상: 2026-09-27 현재 작업 트리 코드
> 로컬 검증 근거: 아래3절의 테스트·타입 검사·빌드 결과. Windows clean-session과 실제 모델 평가는 별도 미완료
> 병합 상태: 미수행
> 병합 대상: origin/main
> 병합 근거: 이번 범위에 Git 게시/병합 없음
> 배포 상태: 미수행
> 배포 근거: 로컬 개발 변경이며 공개 배포 없음
> 실제 연동 상태: 미수행
> 실제 연동 근거: 새 버전 DeepSeek 유료 호출 승인이 대기 중이며 UI 검증은 SSR
> 작업 범위: L
> 적용 스킬: terminal-ops, ui-ux-design
> 적용 Gate: Security Gate, UI/UX Gate
> 위험도: 구조
> 위험 작업 여부: 예

## 0. 작업 범위 확인

사용자의 남은 작업1~3번 지시. 작업 계약은 백엔드 docs/work-plans/2026-09-26_evidence-rules-windows.md. backend/frontend dev, architecture main을 확인했다. 기준 커밋은 backend93b8bcc, frontend1650120, architecture cac51a0. 원본 하네스 동기화·배포·게임 종료·외부 설치는 제외한다. 사용자 승인 범위와 모델 품질/Windows 환경 한계를 별도 기록한다.

## 1. 작업 요약

AIReviewEvidence에 발생 조건/예상 결과/미확인 전제/근거 줄 링크를 표시한다. 신규 필드는 optional로 과거 리뷰를 보존하고 Vue 텍스트 보간을 사용한다. 미평가 BINDING_UNRESOLVED 안내와 홈의 고정23규칙 문구를 정리했다.

## 2. 변경 파일

정책·하네스/분석기와 테스트, 또는 AIReviewEvidence/AIReviewPanel/AnalysisPanel/WorkspacePanel 및 테스트. 아키텍처 원본에 ADR-REVIEW-005, context-map/DECISIONS/소유 문서를 동기화했다. 신규 ADR은 미게시이며 architecture.json은 마지막 게시 revision을 유지한다.

## 3. 검증 결과

40 tests PASS, vue-tsc 및 Vite build PASS/54 modules. SSR로 과거 필드 없음·HTML escaping·고정HEAD 줄 링크를 확인했다. 실제 로그인한 브라우저에서 새 리뷰 표시·반응형은 미검증이다.

Terminal Ops: 각 저장소 CWD에서 기존 Python/npm 검증을 실행했다. 새 설치/삭제는 없다. 프론트 최초 sandbox 검증은 esbuild 상위 폴더 접근 거부로 실패했고, 정상 권한 재실행에서 test/build 모두exit0. 최초 새 규칙 테스트의 TypeScript class Function 오탐을 type_identifier 검사로 수정했고 동일 suite가 통과했다. broad except도 문자열 부분검색에서 AST 타입 검사로 수정해 유사 문자열 오탐을 막았다. 실패한 시도를 숨기지 않는다.

## 4. Checklist 결과

입력 근거 anchor/변경 줄/basis 일관성 PASS. 과거 결과 호환/HTML 비실행 PASS. 정적6규칙 위반2·정상2·유사정상과 미평가/위치/메시지 PASS. 권한/반출 범위·자동재시도0 유지 및 민감정보 미출력 Security Gate 검수. 사용자 코드 실행 없음. 실제 모델 품질/깨끗한 Windows 세션은 미완료로 구분한다.

UI 설계: 리뷰를 읽는 팀 멤버가 근거와 전제를 구분하는 것이 목표다. 기존 카드·파랑 토큰·ai-prose를 유지하고 근거 줄만 줄바꿈 가능한 링크로 추가한다. 실제 sourceLink 사용, 링크 새 창 rel 보호, 텍스트 레이블/브라우저 키보드 포커스를 유지한다. 새 로딩/네트워크 동작은 없고 기존 상태 경로를 유지한다. 과거 필드는 표시하지 않는다. 시각 실측은 미수행이라 UI Gate 관측 범위 WARN이다.

## 5. 발견된 문제

### 트러블슈팅: Windows 테스트 중 native 진단 재발

- 사건 상태: 조사 중
- 원인 상태: 확인(직전 발생 모듈), 이번 실행의 instruction 주소는 미측정
- 관련 Report: backend reports/2026-09-26_recheck-publish_report.md

#### 어디서 발생했나

Windows Python3.12/Psycopg/pytest, 별도 prism_test 임시 스키마. 2026-09-27 KST. 최종 결과는 backend reports/2026-09-27_evidence-windows-final.json.

#### 어떤 문제가 있었나

208테스트는 통과했지만 native access violation 진단2회가 있었다. 프로세스 exit0은 clean-session 성공 증거가 아니다.

#### 어떻게 발생했나

새 자식 프로세스에서 전체 pytest를 실행하고 테스트 전후 GetModuleHandleW로 npggNT64.des만 조회했다. 시작 false, 종료 true로 실행 중 외부 모듈 로드가 확인됐다. DB 연결 문자열과 raw 로그는 저장하지 않았다.

#### 왜 발생했나

직전 vectored exception 관측은 npggNT64.des+0x2769를 특정했다. 이번 실행도 모듈과 진단이 함께 관측됐으나 instruction 주소를 다시 측정하지 않았으므로 동일 결함이라고 새로 입증한 것은 아니다. 공급업체 내부 동작은 미확인이다.

#### 어떻게 해결했나

모듈이 없는 새 세션 비교를 시도했지만 테스트 중 로드되어 완료하지 못했다. GameGuard/게임 종료·우회·삭제·TLS 설정 변경·진단 숨김은 없다. test 성공과 환경 결함의 해결을 구분한다.

#### 앞으로 어떻게 대응하나

사용자가 게임을 정상 종료하고 필요하면 재부팅한 뒤 해당 모듈이 로드되지 않는 세션에서 scripts/check_windows_regression.py를 새 출력 경로로 실행한다. TEST_DATABASE_URL은 별도 _test DB만 허용한다. 완료 기준은 전후 모듈없음·native진단0·전체test통과다. 담당: 사용자/개발자, 실행 조건: 깨끗한 세션, 상태: 대기.

## 6. 미해결 항목

새 근거 계약은 추가 승인 후 백엔드 실제7호출, 구조7/7·내용6/7. UI 실제 브라우저 검증과는 별개다. 실제 결과의 시각 검수는 후속이며 SSR을 브라우저 검수로 표현하지 않는다.

## 7. Working Context 반영 여부

검증 후 reports/_LATEST.md 및 Working Context를 이번 기록으로 연결한다. 과거 게시/CI 성공은 이전 커밋의 이력이며 이번 변경을 게시한 것으로 표현하지 않는다.

## 8. 다음 작업

백엔드 유료7회 평가·수동 검수는 수행했고 내용6/7로 오탐1건이 남았다. clean Windows 재검증은 위 절차를 따른다. 커밋/푸시·main병합/배포는 이번에 하지 않는다.

## 로컬 적용

진행 Job0을 확인하고 기존 PRism API 프로세스만 재시작했다. 새 launcher31044, /health/ready200 확인. 읽기 전용 사전 조회는 처음 잘못된 Windows 이벤트 루프 및 Job의 status 컬럼을 사용해 실패했으며, 프로젝트 loop_factory와 실제 Job.state를 사용한 조회에서0을 확인한 뒤 재시작했다. DB/로그에 비밀값을 기록하지 않았다. 추가 유료 호출과 Git 게시 없음.

추가 승인 후의 최신 모델 평가 결과는 백엔드 동일 날짜 Report를 따른다. 이 문서의 기존 승인 대기/호출 없음은 승인 전 관측이다. 프론트 코드 변경/새 브라우저 검증 없음.
