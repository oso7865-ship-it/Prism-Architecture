# 계정 메뉴 정렬

- 요청: 프로필 원형·이름·화살표를 하나의 컴포넌트로 묶어 안정적으로 정렬한다.
- 범위: S, Vue polish. auth/AccountMenu.vue 추출, HomeView 연결, 관련 CSS와 공통 SVG 아이콘만 수정. 기존 dev 미커밋 변경 보존.
- 원인: summary는 이미 flex 가운데 정렬이지만 화살표가 글리프 ⌄여서 글꼴 기준선의 영향을 받는다. summary의 일반 padding으로 높이54px이며 세 요소의 크기와 클릭 영역 구분이 약하다.
- 설계: 단일44px 이상 summary 안에32px 아바타/minmax 이름/16px SVG의 grid. 이름은 한 줄·긴 이름 말줄임, 전체 이름은 접근 가능한 이름·title·펼친 패널에서 보존. 공통 파란색 토큰과 얇은 테두리. 패널은 트리거 아래8px·오른쪽 정렬, viewport 안으로 제한.
- 동작: 네이티브 details의 Enter/Space/Tab을 유지하고 Escape로 닫기·트리거 포커스 복귀를 컴포넌트에서 소유. 로그아웃 API는 HomeView에 그대로 두고 컴포넌트가 logout 이벤트를 전달. 새 API/권한/세션 변화 없음.
- 검증: 기존108회귀/타입·빌드, 실제 메뉴 열기/닫기/Escape,320/375/414/768/1280의 중심 높이·44px 클릭영역·문서/패널 넘침 실측, 전후 캡처. 로그아웃 서버 호출은 변경하지 않아 실행하지 않음.
- 적용: ui-ux-design, vue-ui-polish(polish), browser-qa, verification-loop, terminal-ops. 일반 위험.
