# 작업 리포트: 로그인·메인·기능 페이지 UI

> 작성일: 2026-09-26
> 패키징/배포일: 해당 없음
> 작업 브랜치: dev
> 커밋/PR: 미커밋
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-26T04:11:00+09:00
> 구현 상태: 완료
> 구현 근거: src/app, src/features/auth/session.ts, src/features/workspace, src/shared/ui의 working-tree 변경
> 로컬 검증 상태: 완료
> 로컬 검증 대상: UI 페이지 분리와 세션 처리 working-tree
> 로컬 검증 근거: npm run build PASS, npm test 4 files / 23 tests PASS, CUA 화면·DOM 확인
> 병합 상태: 미수행
> 병합 대상: origin/main
> 병합 근거: 이번 작업에서 Git 쓰기 요청 없음
> 배포 상태: 미수행
> 배포 근거: 로컬 Vite만 검증, 운영 배포 미실행
> 실제 연동 상태: 진행 중
> 실제 연동 근거: 기존 세션에서 실제 팀/연결 저장소/PR #1/리뷰 조회 성공; 로그아웃 후 OAuth 재로그인은 실패 안내, 재시도는 자동 승인 검토 차단
> 작업 범위: L
> 적용 스킬: ui-ux-design, vue-ui-polish, browser-qa, verification-loop
> 적용 Gate: UI/UX Gate, Security Gate, API Gate, Document Gate
> 위험도: 구조, 보안
> 위험 작업 여부: 예

## 0. 작업 범위 확인

사용자는 UI/UX 위치·안정감 개선에 이어 로그인 화면→메인→기능 페이지의 실제 이동을 명시했다. 프론트 dev의 기존 변경을 보존하며 Vue Router 경로와 화면 구조를 수정했다. 서버 인증·권한 정책, DB, GitHub App 권한, 하네스 동기화, Git 게시·배포는 제외했다. 세션 확인은 기존 HttpOnly refresh API와 메모리 access 토큰 계약을 사용하며 새로운 자격증명이나 권한 부여는 없다. 구조 변경 근거는 사용자의 페이지 분리 요청이다.

## 1. 작업 요약

- `/login`, `/app`, `/app/repositories`, `/app/team` 경로와 인증 전 복원 가드. 기존 루트 OAuth/저장소 callback 호환, 페이지 제목·이동 포커스 적용.
- 상단 계정, 팀 선택과 메뉴, 메인 현황, 저장소/PR 작업, 팀 설정으로 기능 배치. 관리 폼은 필요할 때 펼친다.
- 공통 아이콘/상태 배지/PR 상세 컴포넌트, 한국어 상태·빈 화면·오류 안내. 넓은 화면 목록/상세 2열, 작은 화면 1열, 키보드 포커스 및 reduced-motion.
- API 세션 만료가 갱신 후에도 계속되면 로그인 화면으로 이동. 기존 권한 조건과 위험 작업 confirm 유지.

## 2. 변경 파일

`src/app/{main.ts,router.ts,LoginView.vue,HomeView.vue,style.css}`, `src/features/auth/{api.ts,session.ts}`, `src/features/workspace/{WorkspacePanel.vue,PullRequestDetail.vue,types.ts}`, `src/shared/ui/{AppIcon.vue,StatusBadge.vue}`, `tests/{router.test.ts,workspace-api.test.ts}`. README·작업 계획·최신 포인터·Working Context를 갱신했다. 기존 Workspace 구현과 API 변경이 같은 미커밋 작업 트리에 있으므로 전체 diff를 이번 UI 작업만으로 해석하지 않는다.

## 3. 검증 결과

- 최종 `npm run build`: 타입검사와 Vite bundle PASS. `npm test`: 4 files / 23 tests PASS. 보호 URL 3개, 세션 복구, 로그인 후 메인 이동, 기존 repository callback, 복원 실패, 만료 재시도 상한 포함.
- CUA 실제 계정 세션: 메인 현황(저장소1·멤버1), 저장소 페이지, Draft PR #1 상세, 리뷰 조회 빈 상태, 팀 설정 이동·제목 포커스, 로그아웃, 비로그인 `/app/team` 접근의 로그인 redirect 확인.
- 저장소 상세 화면 320/375/414/768/1440px에서 clientWidth=scrollWidth. 로그인은 같은 폭들을 확인했으며 768px는 별도 재측정(753=753, 세로 스크롤바 제외). 1440px 로그인·PR 상세 및 375px 팀·로그인 screenshot으로 배치 확인. viewport override 원복.
- `ui-pattern-audit.mjs src`: high0/medium0/low9. 흰 카드·버튼 대비와 로그인 최소 화면높이에 대한 휴리스틱 안내. 기존 인디고/밝은 표면 설계와 로그인 콘텐츠 분리 목적이므로 유지. 일반 디자인 주의사항이며 보안·구조 WARN 없음.
- 실제 신규 OAuth 로그인은 실패 안내를 관측했다. 원인 확정 및 성공 재검증은 미수행. 두 번째 시도는 자동 승인 검토가 사용자의 수동 화면 테스트 의사를 근거로 차단했다. 우회하지 않고 사용자 직접 확인으로 남겼다.
- 다른 역할 계정·다중 팀·초대 생성/수락·역할 변경·연결 해제의 실제 쓰기 동작은 이번 UI QA에서 재실행하지 않았다. 서버 정책 검증은 기존 구현 범위이며 UI 가드는 서버 권한 검사를 대체하지 않는다.

## 4. Gate 및 트러블슈팅

Security/API: 변경 범위 PASS. 기존 로컬 API만 bearer 전송, auth 저장소 추가 없음, 렌더링은 Vue escape 사용, API 권한 조건 유지. 직접 보호 경로와 실패 세션을 테스트했다. 외부 OAuth 성공은 위 실제 연동 상태와 별개다.

라우터 테스트 최초 실행은 Vitest 설정에 Vue 변환 플러그인이 없어 `.vue` import 해석에 실패했다. 테스트는 라우팅·세션 계약을 검증하므로 페이지 컴포넌트 3개를 명시적으로 mock 처리했다. 최종 23개 전체 재실행 PASS. 실제 화면은 별도 CUA로 확인했다. UI/UX Gate는 확인한 반응형·탐색·포커스 범위 PASS; 신규 OAuth 왕복과 다중 역할 시나리오는 보류 항목이다.

## 5. 남은 작업

사용자가 GitHub 로그인을 다시 실행해 메인 진입·새로고침·저장소/팀 이동을 확인한다. 실패가 재현되면 callback의 서버 오류 분류를 비밀값 없이 조사한다. 사용자 초대 링크는 로그인 후 다시 여는 기존 제한이 있으며, OAuth를 넘는 초대 복귀는 별도 설계 대상이다. 배포 시 SPA fallback 구성 필요. 고정 SHA 분석·DeepSeek 결과 화면은 후속, 하네스 동기화는 보류한다. 커밋·푸시 없음.

문서 검증: references 103 markdown PASS, git diff --check PASS. work-records의 Gate 표기 경고는 헤더에 Security Gate 명칭을 명시해 수정했다.
