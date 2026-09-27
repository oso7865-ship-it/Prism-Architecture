# 작업 리포트: DeepSeek 리뷰 하네스

> 작업 브랜치: dev (과거 작업 시점; 원래 본문 범위 참조)
> 커밋/PR: 작성 당시 미커밋; 현재 게시 상태는 reports/_LATEST.md 참조
> 작업 범위: M
> 형식 상태: legacy
> 과거 적용 스킬 기록: 미확인 (이전 본문에 남은 적용 기록만 유효)
> 적용 Gate: 기존 본문 검증 범위 참조; 새 Gate 수행을 소급 주장하지 않음
> 위험도: 일반 (기록 형식 정정; 과거 작업 위험은 본문 참조)
> 형식 정정: 2026-09-26 게시 준비 중 누락 헤더 정리. 과거 검증을 재실행한 것으로 간주하지 않음.

> 작성일: 2026-09-26 · 확인: 2026-09-26T20:25:27+09:00
> 브랜치: backend/frontend dev, architecture main · 미커밋
> 구현: 완료 · 로컬 검증: PASS, 기존 Windows 진단 WARN
> 병합/배포: 미진행 · 추가 유료 모델 호출: 0
> 범위: M · Security Gate/기존 UI 규칙 적용

## 0. 작업 범위 확인

사용자가 승인한 모델용 리뷰 하네스를 설계 후 구현했다. GENERAL_HARNESS와 별개의 제품 기능이다. 기존 호출 한도/접근 권한·소스 전송 제한 유지. DB migration/기존 결과 수정/하네스 동기화 없음.

## 구현

ADR-REVIEW-004와 소유 문서·결정/context-map을 갱신했다. review/harness의 core/checks/output 및 Java/Python/JavaScript/TypeScript Markdown을 allowlist로 읽어 실제 입력 언어만 SystemMessage에 조합한다. 저장소 코드·지침·주석은 HumanMessage 데이터다. 모델 도구 권한은 계속 없다.

문서·출력 schema·조합 revision의 digest가 prompt_version이며 현재 rh1-d9133f8d1cc6f1c1이다. 성공 result.harness에는 version/modules/system_digest만 저장한다. 원문 prompt 미보관. 전체 언어 지침을 포함한 system6087bytes로24KiB 이내. 사용자 코드 JSON24KiB 제한은 별개이며 system도 API 입력 토큰을 소비한다.

새 지적 basis=SUPPORTED/NEEDS_CONTEXT. 전자는 제공 코드 근거, 후자는 추가 확인 필요로 표시한다. NEEDS_CONTEXT+ERROR는 서버가 거부한다. 이 분류는 모델 판단이며 실행 검증과 다르다. 기존 결과는 basis/harness 없이 조회되고 기존 prompt_version도 표시한다.

## 검증

- 관련 backend31개 PASS /7.66초: 언어별 선택·신뢰 경계·digest 변경·system 한도·실제 Provider wiring(mock ChatDeepSeek)·출력 anchor/basis·DB 이력 metadata·이전 지침 Job 외부호출0.
- ruff PASS, mypy110파일 PASS.
- frontend typecheck/build PASS(51modules),38개 테스트 PASS.
- architecture validator PASS,19 ADR; 기존 긴 관계 문서 경고1개.
-7개 합성 평가 사례와 오프라인 CLI 구현. reference fixture로 schema/anchor 기대치 scorer7개 PASS. 실제 모델 출력 평가나 정확도 측정이 아니다.
- API 시작 후 ready200. 실행 전 대기/진행 Job0 확인. 프런트 개발 서버도 재실행.

## 한계·후속

실제 DeepSeek에 새 지침을 보낸 유료 평가 호출은 이번에 실행하지 않았다. 다음 수동 리뷰부터 적용된다. 같은 corpus·모델·지침 버전으로 실제 출력 여러 회를 수집해 누락/오탐/일관성/토큰을 비교하고 근거의 의미는 사람이 rubric으로 검수해야 한다.

기존 Windows native access-violation 진단이 일부 테스트에서 출력됐지만31개 완료 exit0이다. 원인 해결은 후속이다. 공개 배포·금액 예산·보관 정책·Git 게시와 하네스 동기화는 미진행.
