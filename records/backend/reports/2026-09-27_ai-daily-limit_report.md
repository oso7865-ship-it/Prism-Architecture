# 팀 AI 리뷰 하루30회·모델 표시 변경

> 작성일: 2026-09-27  
> 작업 브랜치: dev  
> 커밋/PR: 미커밋 working tree, 기존 변경 보존  
> 상태 기록 버전: 1  
> 상태 확인 시각: 2026-09-27T21:05:00+09:00  
> 구현 상태: 완료  
> 구현 근거: 한도 기본/최대30, 로컬·예시 설정30, AI 모델 표시, ADR-REVIEW-008  
> 로컬 검증 상태: 완료  
> 로컬 검증 대상: backend/frontend working tree, architecture main working tree  
> 로컬 검증 근거: Linux 관련18 tests, frontend108 tests·타입/빌드, Ruff/format/mypy, 문서 검사 PASS  
> 병합 상태: 미수행  
> 병합 대상: origin/main  
> 병합 근거: 커밋·push·병합 요청 없음  
> 배포 상태: 미수행  
> 배포 근거: 로컬 API 재시작만 수행  
> 실제 연동 상태: 완료  
> 실제 연동 근거: API ready, 브라우저 실제 이력 응답을 다시 불러와 팀당30회·AI 모델 동의 표시 확인  
> 작업 범위: M  
> 적용 스킬: verification-loop, terminal-ops  
> 적용 Gate: Verification Loop  
> 위험도: 일반. 사용자 결정에 따른 설정·표시 문구 변경.  
> 위험 작업 여부: 아니오

## 요청과 변경

사전 계획: [ai-daily-limit](../docs/work-plans/2026-09-27_ai-daily-limit.md). 사용자는 팀당 하루30회와 DeepSeek를 화면에서 AI 모델로 표시하도록 결정했다. 이어 실제 유료 검증 최대50회를 추가 승인했다. [승인 사용 기록](../docs/PAID_EVALUATION_AUTHORIZATION.md)에 현재 사용0/잔여50을 기록했다.

| 영역 | 이전 | 이후 |
|---|---|---|
| 설정 기본/최대 | 5회/5회 | 30회/30회, 최소1 유지 |
| 로컬 env·개발/운영 예시 | AI_DAILY_LIMIT=5 | AI_DAILY_LIMIT=30 |
| 화면 한도 | API 응답값, 초기5 | API 응답값, 초기30 |
| 동의·전송 설명 | DeepSeek | AI 모델 |
| 제목·모델 배지 | DeepSeek · 코드 리뷰 / deepseek-flash | AI · 코드 리뷰 / AI 지원 |
| 연결 실패·사용내역 안내 | DeepSeek 연결/사용내역 | AI 서비스 연결/사용내역 |
| 설계 | ADR-REVIEW-007의 일5회 | ADR-REVIEW-008의 일30회; 나머지 계약 유지 |

팀 단위·UTC 접수일(한국시간 오전9시 초기화)·실패/취소 포함·동시1개·매 요청 소유자 동의·자동재시도0을 유지한다. 30회는 계정 전체 제한이 아니다. DB 스키마·사용량 초기화·제공자 설정·API 모델 정보는 변경하지 않았다. 이전 AI 답변 원문을 다시 쓰지 않았다.

## 검증

| 항목 | 결과 |
|---|---|
| Linux 테스트 | test_foundation.py + test_review.py, 18 passed/13.89초, skip0 |
| 30회 경계 | 실패2건+취소28건 접수 성공, history30건,31번째 AI_DAILY_LIMIT, FakeProvider 실제호출0 |
| 설정 범위 | 기본30,1/5/30 허용,0/31 거절 |
| 프론트 | 108 tests, vue-tsc, Vite PASS. API가 deepseek-flash를 줘도 제품 문구에 표시되지 않음,30회·동의·비용 안내 유지 |
| 정적 검사 | 변경 Python 3파일 Ruff check/format PASS, settings mypy PASS |
| 문서 | 76문서·309링크·24ADR PASS, 기존 schema 문서 길이 경고2개 유지 |
| 로컬 API | 활성 READY/LEASED Job0, PENDING/RUNNING 리뷰0 확인 후 재시작. launcher46068/server46972, /health/ready=ready |
| 실제 UI | 기존 PR49 AI 이력 새로 조회, 하루30회·한국시간 오전9시·AI 모델 동의, 동의하지 않은 시작 버튼 비활성 확인 |

DB 테스트는 키·실제 env를 마운트하지 않은 기존 Linux 테스트 이미지에서 실행했다. 포트를 열지 않은 내부 Docker network와 tmpfs 임시 PostgreSQL을 사용했고 테스트 후 이번 컨테이너·network만 제거했다. 기존 개발 DB는 그대로다. Windows DB/native 전체 회귀를 재실행하지 않았다. 이번 변경과 무관한 전체 backend277회귀는 직전 Report의 과거 증거이며 이번18개와 혼동하지 않는다.

초기 ADR 제목을 필수 항목별로 분리하여 문서 FAIL을 해소했다. Python 수정 중 혼합 줄끝2파일은 Ruff format 후 통과했다. 재시작 전 SQL의 jobs.status 오기를 jobs.state로 고쳐 읽기 확인을 완료했다. 프로세스 경로/명령줄을 확인한 로컬 API만 중단·재시작했다. 새 로그와 화면 증거는 저장소 밖 ../../audit-artifacts/2026-09-27-ai-daily-limit/에 있다.

## 판정·후속

이번 한도·표시 변경 PASS. 재시작된 실제 화면 캡처는 ai-model-30-daily.png. 새 모델 응답 생성·품질 재평가는0회다. 다음 품질 작업은 [기존 문맥·리랭커 보고서](2026-09-27_context-reranking_report.md)의 검증 거절 원인·의미 품질 과제를 이어가며 추가50회 승인 내에서 사용량을 기록한다. 리랭커 OFF 유지. backend/frontend dev, architecture main. 커밋·push·배포·원본 하네스 동기화는 하지 않았다.

최종 작업 기록 검사: backend38개/frontend25개 PASS, 세 저장소 git diff --check PASS(줄끝 안내만 있음). 최초 작업 기록 검사 위치가 workspace 상위여서 입력 경로 오류가 났고 각 저장소 CWD에서 재실행해 통과했다. 검증 명령의 초기 실패를 최종 통과로 숨기지 않는다.
