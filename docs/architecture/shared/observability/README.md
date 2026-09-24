# Observability: 로그·추적·건강 확인

> ID: `OBSERVABILITY` · 소유: `backend/app/shared/observability` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 로그·trace·health·민감 필드 마스킹을 변경할 때

```text
shared/observability/
├─ logging.py       구조화 로그 설정
├─ redaction.py     민감 필드 제거·출력 제한
├─ middleware.py    request_id·duration·공개 오류 연결
└─ health.py        기술적 health 결과
```

로그 허용값은 trace_id, service name, route template, status, duration, opaque workspace/job/analysis ID, rule_id, 공개 error_code, 카운트다. 쿼리 문자열·request/response body·소스·Diff·토큰·private key·PR 본문·LLM Prompt/응답 원문은 기본적으로 남기지 않는다.

GitHub 숫자 ID·파일 경로·PR 제목은 사용자 데이터이므로 관측에 꼭 필요하지 않으면 제외한다. 오류 trace에 source 내용이 들어가는 Provider/Parser 예외는 안전한 code로 바꾸어 기록한다. 모델 tracing/외부 APM body capture는 기본 OFF다.

`/health/live`는 프로세스 생존, `/health/ready`는 짧은 DB 접근/필수 설정 상태를 확인한다. LLM/GitHub의 긴 호출을 health check에 넣지 않는다. health 응답에 DSN·환경 변수·의존성 내부 주소를 노출하지 않는다.

초기 관측은 구조화 stdout 로그와 DB의 Job/Analysis 상태 조회로 충분하다. Grafana/Prometheus/Kafka를 처음부터 추가하지 않는다. 기록할 핵심 지표는 queue 지연·실패/재시도 수·parse 시간·source unavailable 비율·LLM 요청/사용량이다.

테스트에는 가짜 비밀 문자열을 모든 입력 경로로 흘려보낸 뒤 로그·DB·HTTP·AI 요청에서 검출되지 않는지 검사하는 canary 테스트를 둔다. 운영 접근/보관 기준은 [보안·보관](../../operations/SECURITY_PRIVACY.md)을 따른다.
