# AI 모델 표시·팀별 하루30회

> 작성일: 2026-09-27  
> 작업 브랜치: dev  
> 커밋/PR: 미커밋 working tree, 기존 변경 보존  
> 상태 기록 버전: 1  
> 상태 확인 시각: 2026-09-27T21:05:00+09:00  
> 구현 상태: 완료  
> 구현 근거: AIReviewPanel의 일반 모델 표시·한도 초기30, UI 회귀 갱신  
> 로컬 검증 상태: 완료  
> 로컬 검증 대상: frontend working tree  
> 로컬 검증 근거: 108 tests·vue-tsc·Vite PASS  
> 병합 상태: 미수행  
> 병합 대상: origin/main  
> 병합 근거: 요청 없음  
> 배포 상태: 미수행  
> 배포 근거: localhost 검증만 수행  
> 실제 연동 상태: 완료  
> 실제 연동 근거: 재시작된 로컬 API의 실제 응답에서 하루30회와 AI 모델 표시 확인  
> 작업 범위: M  
> 적용 스킬: verification-loop, terminal-ops  
> 적용 Gate: Verification Loop  
> 위험도: 일반. 표시 문구와 안내 값 변경.  
> 위험 작업 여부: 아니오

사용자 요청에 따라 동의·설명·제목·모델 배지·연결 실패·사용내역 안내의 DeepSeek 표기를 AI 모델/AI 서비스로 정리했다. 실제 제공자·모델의 서버 설정은 그대로다. API의 daily_limit 값을 사용하며 초기값도30으로 변경했다. 전송 데이터와 비용·초기화 시각 설명은 유지했다.

동의 문구: “변경 코드와 관련 코드 일부, 내 이전 검토 메모와 점검 요약을 AI 모델에 보내는 데 동의합니다.”

108 tests·타입/빌드 PASS. 서버가 deepseek-flash와30회를 반환하는 fixture에서 고유명 미표시·30회 표시·동의 전 실행 불가를 검증했다. 실제 PR49에서 API 이력을 다시 가져와30회 안내·동의 미선택·시작 비활성을 확인했다. 폼 전송·유료호출0. 캡처는 ../../audit-artifacts/2026-09-27-ai-daily-limit/ai-model-30-daily.png. 기존 backend/frontend dev 및 architecture main의 미커밋 변경 보존, push/배포 없음.

서버의 30번째 허용·31번째 차단과 Linux 관련18 tests 등 상세는 backend의 reports/2026-09-27_ai-daily-limit_report.md를 따른다. 직전 전체 쉬운 용어 정비는 [이전 보고서](2026-09-27_plain-language_report.md)에 보존한다. 추가 유료검증 승인50회는 backend docs/PAID_EVALUATION_AUTHORIZATION.md에서 사용0/잔여50으로 관리한다.
