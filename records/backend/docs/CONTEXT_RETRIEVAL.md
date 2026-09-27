# 고정 HEAD 문맥 수집과 선택적 리랭커

새 AI 리뷰는 `BOUNDED_CODE_V4`를 사용한다. 이전 결과는 수정하지 않는다. 변경 메서드와 import/식별자/파일 경로로 관련 구현 후보를 찾아 규칙 점수로 선택한다. 함수가 파일의80줄 뒤에 있어도 해당 구간을 수집할 수 있다. Tree-sitter는 별도 프로세스에서 구문 metadata만 읽으며 저장소 코드를 실행하지 않는다.

## 범위와 한도

2026-09-27 품질 점검에서 `./labels.js`처럼 확장자를 명시한 ESM import 후보 누락을 수정했다. 확장자 없는 기존 후보 비교와 전체 파일 경로 비교를 함께 사용한다. 당시 후보12개/관련2개·경로/비밀 검사·바이트 제한을 유지했다. 아래 표는010에서 확대된 현재 계약이다. 이는 기존 V3 검색 구현의 버그 수정이며 전체 모듈 해석을 보장하지 않는다. [품질 안정화 결과](../reports/2026-09-27_ai-quality-stabilization_report.md).

| 항목 | 제한 |
|---|---|
| 소스 | 고정 HEAD, 일반 파일, Java/Python/JS/TS 및 JSX/TSX |
| 취득 | tree 앞5,000항목, 소스당200KB, 변경8파일·관련 후보12파일, 동시 취득3 |
| 후보 | 함수 질의별 파일당4구간, 전체24구간, 구간160줄/14,000byte |
| 모델 입력 | 변경8파일·관련4파일, patch/파일 JSON16KiB·전체 코드 JSON48KiB |
| 구문 처리 | 배치당5초, 함수128/식별자256/import40/호출256/위치식별자2,048; Linux 메모리512MiB·CPU4초 |
| 전체 문맥 수집 | 20초; 실패하면 원래 안전한 diff 유지 |
| 리랭커 | loopback 고정 주소, HTTP2초·응답8KiB·재시도0; 실패하면 규칙 선택 |

변경 줄은 재정렬에서 제거하지 않는다. 짧은 함수는 함수·메서드 범위, 긴 함수는 선언부와 주변 구간을 사용한다. 긴 함수 전체·호출 그래프·타입/상속/동적 호출·alias를 완전히 해석하지 않는다. Python 상대 import, Java static import, 배럴 export와 파일명이 다른 호출부는 일부 놓칠 수 있다. 후보 생성에서 놓친 코드를 리랭커가 찾아낼 수는 없다.

비밀·제외 경로·바이너리·고정 HEAD 검사를 먼저 적용한다. 구문 metadata·질의·후보 소스는 일시 메모리만 사용하며 DB에 저장하지 않는다. 검증된 결과의 `coverage.retrieval`에 선택 방식, 후보 수, 취득 파일 수, 모델 revision/처리 시간/잘린 문서 수/실패 복귀 사유를 남긴다. 소스 누락·예산 초과·불완전 구문은 `context_notes`로 기록한다. OWNER 동의·권한·연결 세대는 유지한다. ADR-REVIEW-010에서 외부 호출 최대2회(초안+근거 검증), 회당60초/전체150초·재시도0으로 변경했다.

## 도입 결정

2026-09-28 ADR-REVIEW-010은 직접 호출 근거 보호·함수별 질의·동일 파일 구간 병합을 적용한다. 같은12사례의 근거 포함이 규칙12/12·리랭커12/12가 되어 이전 선택 회귀는 사라졌지만 규칙 대비 추가 이득이 없어 **기본 OFF**다. [최신 비교와 한계](../reports/2026-09-28_evidence-first-review_report.md)를 우선하고 아래 비교는 과거 근거로 보존한다.

2026-09-27 동일 후보12사례에서 필요한 근거 포함은 규칙12/12, 로컬 리랭커9/12였다. Java3사례가 악화되어 **리랭커 기본 OFF**를 유지한다. 실제24회 DeepSeek 비교도 품질 개선을 입증하지 못했다. [평가·검증 보고서](../reports/2026-09-27_context-reranking_report.md)를 따른다. 전용 모델 설치와 기본 활성화는 별개다.

선택한 실험 모델은 [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2)다. 영어 MS MARCO 검색 모델이며 코드 전용 학습이나 한국어 리뷰의 정확도를 보장하지 않는다. 공식 ONNX/tokenizer 데이터만 사용하며 revision/파일 크기/SHA256은 `tools/reranker/manifest.json`, 의존성은 `requirements.lock`, 기반 이미지는 Dockerfile digest로 고정했다. 모델은 약92MB이며 전체 이미지 크기와 다르다.

## 선택 기능 실행

기본 개발 환경에서는 설치·기동할 필요가 없다. 독립 clone에서 실험하려면 Docker를 준비하고 저장소 루트에서 다음을 실행한다. 최초 build만 PyPI·공식 Hugging Face 파일 다운로드가 필요하다.

```sh
docker compose -f compose.reranker.yaml up -d --build
curl http://127.0.0.1:8091/health
```

컨테이너는 non-root, read-only, CPU2개·768MiB·동시 추론1개·작은 임시 파일 영역을 사용한다. 코드/HTTP 본문 로그와 ONNX telemetry를 끈다. 요청 시 모델을 내려받지 않으며 외부 리랭커 API를 호출하지 않는다. 포트는 호스트 `127.0.0.1:8091`에만 공개한다. Docker 기본 bridge의 외부 통신을 물리적으로 차단한 구성은 아니다.

수동 실험의 `LocalReranker`는 서버 설정과 별개다. 제품에서 켜려면 품질 게이트 통과 후 서버 `.env`의 `REVIEW_RERANKER_ENABLED=true`와 API 재시작이 필요하다. **이번 평가에서는 활성화하지 않았다.** 호스트 실행 API를 위한 고정 loopback 주소이므로 API 자체를 별도 컨테이너에 배포할 때는 같은 네트워크 namespace 등 별도 설계·검증이 필요하다. 임의 외부 URL 설정은 제공하지 않는다.

```sh
docker compose -f compose.reranker.yaml stop
```

중단해도 모델 이미지가 남아 재실험할 수 있다. 제품 옵션이 ON인 상태에서 모델이 죽어도 새 리뷰는 규칙 방식으로 복귀한다. 24개 긴 후보에서 모델 자체 처리2.047초, 클라이언트 관측1.922초여서2초 한도에 근접했다. 작은4후보의78ms 관측을 최대 입력 성능으로 일반화하지 않는다.

## 평가 재현

`evals/context-retrieval/cases.json`은 측정 전에 고정한 합성12사례다. 실제 저장소·조직 코드를 사용하지 않는다. 동일 후보 digest·동일2파일 예산·변경 줄 보존을 검사하고, 근거 후보 포함과 최종 입력 포함을 분리한다. 관련 함수는100줄 뒤에 배치했다. 기대 정답은 모델 질의에 넣지 않는다.

```sh
uv run python -m scripts.evaluate_context_retrieval reports/new-local-comparison.json
```

위 명령은 실제 로컬 리랭커를 사용하고 유료 LLM 호출은0회다. 실제 모델 장애를 조용히 비교 성공으로 처리하지 않는다. 출력 파일이 이미 있으면 중단한다. 후보 일치는 유료 전송 전에 확인한다. `--allow-twenty-four-paid-calls`는12사례×2방식의 **최대24회 유료 호출**이므로 별도 예산/승인 범위에서만 붙인다. 재시도0이며 평가 호출은 제품의 Workspace 접수 한도와 별도로 센다.

평가 성공 종료는 측정 완료를 뜻하며 채택 게이트 통과가 아니다. 실패 응답은 통과율 분모에서 빼지 않는다. 질문으로 이동한 지적도 채점하고 원문 오류는 저장하지 않는다. 향후 실행은 검증 단계와 허용된 오류코드를 기록한다. 이번24회 평가의11개 `ValueError`는 이 보완 전 기록이므로 정확한 거절 사유를 복원하지 못했다. 추가 호출로 결과를 덮어쓰지 않았다.

## V4 근거 보존

변경 함수별 최대8질의를 파일 간 교대로 구성하고 직접 호출 이름과 정의가 일치한 후보를 우선 제공한다. 같은 파일의 여러 구간을 합치고 줄 번호 중복을 제거한다. 한 구간을 파일/전체 예산 내에 전부 넣지 못하면 생략하고 사유를 남긴다. 중요한 구간이 후보 한도 밖에 있거나 동적 호출이면 놓칠 수 있다. 리랭커는 선택적 보조 순위이며 기본 OFF다.

coverage.retrieval의 query_count/omitted_queries/protected_candidates/protected_missing/per_file_bytes/max_input_bytes는 수집 범위 진단이다. FUNCTION_PARTIAL/QUERY_LIMIT은 불완전 함수와 질의 한도이며 사용자 화면에 설명한다. 공개 PR 파생 평가의 정답과 의미 기준은 evals/real-pr-gold/README.md를 따른다.
