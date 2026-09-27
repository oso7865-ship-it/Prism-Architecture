# PRism 리뷰 품질·읽기·작업 복원 개선

> 작성일: 2026-09-27  
> 패키징/배포일: 해당 없음  
> 작업 브랜치: dev  
> 커밋/PR: 미커밋 working-tree. 기준 backend 1f9f298 / frontend fda82a5 / architecture c9275e6  
> 상태 기록 버전: 1  
> 상태 확인 시각: 2026-09-27T04:29:32+09:00  
> 구현 상태: 완료  
> 구현 근거: ADR-REVIEW-006 및 작업 계약의 세 묶음 구현. 아래 변경·검증 표 참조.  
> 로컬 검증 상태: 완료  
> 로컬 검증 대상: 위 기준 이후 review-experience working-tree, 실제 localhost API/DB/Vite  
> 로컬 검증 근거: Linux 백엔드 전체231 tests 및 후속30 tests, 프론트65 tests/타입/빌드, 실제 OAuth 복귀·근거 코드·개인 메모·반응형 확인. 검증 한계는 별도 기록.  
> 병합 상태: 미수행  
> 병합 대상: origin/main  
> 병합 근거: 이번 요청은 구현 및 서버 재개이며 main 병합하지 않음.  
> 배포 상태: 미수행  
> 배포 근거: localhost만 실행. 실제 배포는 요청 범위 밖.  
> 실제 연동 상태: 완료  
> 실제 연동 근거: 기존 GitHub OAuth 재로그인과 동일 PR 목적지 복귀, 고정 커밋 코드 조회, 실제 PostgreSQL 개인 기록 저장·새로고침 복원. 새 DeepSeek 호출은 제외.  
> 작업 범위: XL  
> 적용 스킬: terminal-ops, ui-ux-design, vue-ui-polish  
> 적용 Gate: Security Gate, DB Gate, UI/UX, 기능 회귀, 문서·작업 기록  
> 위험도: 주의. 인증 흐름·제한된 소스 조회·개인 기록 테이블 추가. 사용자 구현 위임, DB 백업 및 격리 검증 후 적용.

## 1. 결과와 범위

서버를 복구하고 사용자가 승인한 리뷰 품질, 리뷰 읽기, 작업 복원 세 묶음을 완료했다. PostgreSQL/Vite/API와 내장 runner가 로컬에서 실행 중이다. 이전 전체 감사 문서와 기존 변경은 보존했다. backend/frontend dev, architecture main을 유지하며 커밋·push·배포·하네스 원본 동기화는 하지 않았다.

| 묶음 | 반영 내용 |
|---|---|
| 리뷰 품질 | SUPPORTED 지적과 NEEDS_CONTEXT 질문을 분리 저장·표시. 양쪽 모두 평가. 단순 메서드 유사성에서 경합/쿼리 중복을 단정하지 않도록 지침 보강. 고정 HEAD 주변 코드와 관련 파일 제한 수집. |
| 읽기 | PR 개요/정적 분석/AI 리뷰/활동 탭. 요점·위치 먼저, 상세 근거/코드/개인 기록은 펼침. 신규/반복/이번 미검출 비교는 경로·제목 지문이며 해결 판정하지 않음. 과거 분류 없는 결과는 별도 안내 후 질문 영역에 원문 그대로 표시. |
| 이어가기 | 로그인 왕복에서 PR query/탭/분석 이력 및 초대 fragment 보존. 서버의 최신 RECENT/PAGE 동기화 상태·커서 복원. GitHub 이름/사용자명으로 멤버 식별. 페이지 이동 시 이전 오류 정리. Escape 닫기·초점 복귀, 방향키 탭 이동. |

새 리뷰 지침은 `rh1-7575dd7ee0d1eed5`, 정책은 `BOUNDED_CODE_V2`. 기존 결과를 재생성하지 않았다. **이번에는 유료 모델 호출 0회이며 실제 답변 정확도 향상은 아직 검증하지 않았다.** 이전 실제 평가의 내용6/7·락 문맥 오탐1건 결과는 유효한 과거 관측이다.

## 2. 설계·구현 연결

- [사전 작업 계약](../docs/work-plans/2026-09-27_review-experience.md)
- 원본 설계: architecture의 ADR-REVIEW-006, review/HTTP/schema/frontend 소유 문서, context-map·DECISIONS 갱신.
- 서버: review/context.py, feedback.py, source_view.py, policy/worker/router/model/harness, migrations/0007; PR latest sync, user/workspace 멤버 공개 프로필 계약.
- 클라이언트: PR 상세/분석 탭, ReviewIssueCard·reviewModel, AIReviewPanel/Coverage, returnLocation/router/LoginView, WorkspacePanel/HomeView, 파란색 CSS.
- API: 개인 feedback GET/PUT, 저장 결과 key로 정한 고정 SHA source GET, syncs/latest GET. 클라이언트가 임의 저장소·경로·SHA를 지정하지 못한다.

## 3. 검증 결과

| 검사 | 관측과 범위 |
|---|---|
| 백엔드 전체 | Linux Docker 격리 PostgreSQL에서 **231 passed / 44.46초 / skip 0**. GitHub/DeepSeek는 테스트 대역. 첫 실행219 pass/9 fail은 테이블 수 기대값·contents 응답 대역·422 계약 기대값을 수정 후 전체 재실행해 해소. |
| 후속 권한 검증 | source 응답 중 연결 세대 변경 시 코드 미노출/409 assertion 추가 후 관련30 tests **PASS / 13.51초**. 전체231과 중복되는 subset이며 합산한 테스트 수로 표현하지 않음. |
| Python 정적 검사 | Ruff check PASS, format144 files PASS, mypy113 files PASS. |
| 프론트 | 9파일 **65 tests PASS**, vue-tsc/Vite build PASS. SSR/단위 테스트와 실제 브라우저 확인은 구분. |
| 평가 반례 | 기존7개 + 추가3개 합성 기준 응답: 락 메서드 중복·같은 인자 쿼리 부정 사례, 명백한 0 나눗셈 긍정 사례. 모델 응답 생성 테스트는 아님. |
| 실제 OAuth 복귀 | 로그아웃 → 기존 조직 PR 깊은 링크 → GitHub 로그인 → 원래 전체 URL 복원. team/repo/pr/tab/analysis 일치. 초대 hash는 자동 테스트만 검증. |
| 실제 DB·GitHub | PR49의 고정 SHA에서 근거 주변17줄 조회. 개인 OPEN 임시 메모 저장/새로고침 복원 후 메모를 빈 값으로 정리. 사용자 코드 판단을 대신 기록하지 않음. |
| 동기화·멤버·오류 | 새로고침 후 완료30개/이전 PR 더 가져오기 유지. PP34/@사용자명 표시. 잘못된 검색 입력 오류가 다른 페이지로 이동하면 사라짐. |
| 키보드·반응형 | ArrowRight/Home으로 탭 선택·초점 일치. 메뉴 내부에서 Esc 후 summary 초점 복귀. 320/375/768/1440px에서 문서 가로 넘침 없음. 실제 휴대폰/스크린리더/200% 확대 미검증. |
| 브라우저 로그 | 최종 조회 시 수집된 warn/error 0개. 전체 네트워크 무오류 보증 아님. |

화면 검증 중 코드 줄이 가로로 이어지는 CSS 결함을 발견했다. 줄을 block으로 변경하고 코드 영역17줄/세로403px와 강조 줄을 확인했다. 수정 후 프론트65 tests/타입/빌드를 다시 통과했다.

로컬 증거는 저장소 밖 `../../audit-artifacts/2026-09-27-review-experience/`에 보관한다. `backend-corrected.xml`, `backend-source-revocation.xml`, `INDEX.md`가 이번 결과다. 06 화면은 수정 전 증거이고 07이 수정 후 증거다. 다른 PC에는 증거 폴더를 별도로 옮겨야 한다. 기존 2026-09-27 감사 캡처를 이번 성공 증거로 재사용하지 않았다.

## 4. DB·보안 확인

로컬 DB 백업 `.tools/prism-before-review-feedback.dump` 91,446 bytes를 만들고 pg_restore 목록을 확인했다. 진행 Job 0개 확인 후 0007을 적용했다. 업무17테이블, 물리 FK0 정책 유지. 격리 DB에서 새 테이블 downgrade/upgrade와 기존 review_runs 보존 검증. 롤백하면 새 피드백이 삭제되므로 실제 데이터가 쌓인 후에는 먼저 내보내야 한다.

개인 기록은 review/user/key 유일성, 상태 CHECK, 메모500자/비밀 의심 거부를 적용한다. 저장은 리뷰·팀 행 잠금으로 직렬화한다. 순차 중복 저장/수정·권한 차단을 테스트했으며 피드백 전용 동시 다중 요청 부하 실험은 하지 않았다. 다른 팀/미인증 조회 거부, 본인 기록만 반환/다음 리뷰 참고, 소스 조회 전후 접근·연결 세대 검사, no-store를 검증했다. 분석 대상 소스를 실행하지 않는다.

소스는 SHA 고정 일반 파일만 최대200KB 읽고, 메모리에서 비밀/경로/바이너리 필터를 통과한 제한된 줄만 사용한다. 모델 입력은 최대8개 변경 파일+2개 관련 파일·24KiB, 기존 호출/예산/timeout/자동 재시도 금지 유지. 관련 파일 선택은 대문자 식별자와 파일명의 일치에 의존하고 첫80줄만 보조 문맥이다. 전체 호출 관계 분석이 아니며 필터와 관련 코드 수집이 완전하지 않다. 개인정보·원문 코드·접근 토큰을 새 로그/보고서/DB에 복제하지 않았다.

## 5. 남은 경계와 다음 작업

1. 새 지침과 제한된 문맥의 실제 모델 품질·반복 안정성은 승인된 유료 평가에서 확인한다. 기존 질문 영역도 자동으로 올바른 질문이 되는 것은 아니다.
2. 회차 비교는 경로와 정규화 제목 기반이므로 표현 변경/동일 제목 충돌이 가능하다. 미검출을 수정 완료로 취급하지 않는다. 실제 두 신규 회차 결과 비교는 아직 없음.
3. 블루스크린과 기존 Windows native 예외의 근본 원인은 확인하지 못했다. 이번 DB 전체 회귀는 Linux 격리 컨테이너에서 수행했으며 Windows 환경 문제가 해결됐다는 증거는 아니다.
4. 이전 감사의 CI 밖 운영 scripts lint E501 5건, 실제 다인원/공개 HTTPS·Webhook/배포 검증은 이번 범위 밖으로 남는다. 주소·운영키·예산/알림 등 공개 운영 결정도 유지한다.
5. 구현 working-tree와 보고서는 미커밋·미푸시다. 원본 아키텍처 게시 후 consumer revision 갱신은 다음 게시 작업에서 수행한다.

## 6. 종료 시 검증

아키텍처 문서 무결성 PASS(74개 문서/296링크/22 ADR, 긴 문서 권고2건), 작업 기록 strict PASS(backend30/frontend20), 세 저장소 diff --check PASS. 추적 파일과 비무시 신규 텍스트 파일의 알려진 비밀 패턴 검사0건(architecture83/backend379/frontend222파일). 패턴 밖의 비밀이나 과거 Git 이력을 보증하지 않는다. API ready/프론트HTTP200, 실제 PostgreSQL healthy 확인. 이번 작업의 임시 테스트DB/네트워크만 종료했고 실제 개발 서비스는 유지했다.
