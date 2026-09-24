# 실제 구현 대상 디렉터리 지도

> ID: `DIRECTORY-MAP` · 소유: `architecture` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 최초 scaffold·폴더 구조 변경을 수행할 때

**아래는 만들어야 할 소스 구조이며 현재 압축 파일에 실행 코드가 구현되어 있다는 뜻이 아니다.** 문서 패키지는 docs/scripts/AGENTS만 제공한다. 파일별 업무 책임은 각 패키지 README가 기준이고, 필요한 파일만 단계적으로 생성한다.

```text
prism/
├─ AGENTS.md
├─ README.md
├─ docs/architecture/                 이 문서 패키지
│  ├─ adr/                            영역별 ADR·작성 규칙·템플릿
│  └─ decisions/                      ADR 맵·미정 사항
├─ scripts/
│  ├─ context_select.py               문서 선택 도구(제공됨)
│  ├─ validate_docs.py                문서 검증 도구(제공됨)
│  └─ check_helpers.py                문서 도구 회귀 검사(제공됨)
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  ├─ bootstrap.py
│  │  ├─ workflows.py
│  │  ├─ worker.py
│  │  ├─ domain/
│  │  │  ├─ auth/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ dependencies.py
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/{request,response}.py
│  │  │  ├─ user/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/response.py
│  │  │  ├─ workspace/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ role.py
│  │  │  │  ├─ permission.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/{request,response}.py
│  │  │  ├─ repository/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ policy.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/{request,response}.py
│  │  │  ├─ pull_request/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ sync_service.py
│  │  │  │  ├─ jobs/sync_prs.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/{request,response}.py
│  │  │  ├─ analysis/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ contracts.py
│  │  │  │  ├─ status.py
│  │  │  │  ├─ jobs/run_analysis.py
│  │  │  │  ├─ pipeline.py
│  │  │  │  ├─ detector/language.py
│  │  │  │  ├─ analyzer/
│  │  │  │  │  ├─ base.py
│  │  │  │  │  ├─ java/{parser,extractor}.py
│  │  │  │  │  ├─ python/{parser,extractor}.py
│  │  │  │  │  ├─ javascript/{parser,extractor}.py
│  │  │  │  │  └─ typescript/{parser,extractor}.py
│  │  │  │  ├─ rule/
│  │  │  │  │  ├─ base.py
│  │  │  │  │  ├─ registry.py
│  │  │  │  │  └─ {common,java,python,javascript,typescript}/
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/{request,response}.py
│  │  │  ├─ review/
│  │  │  │  ├─ api.py
│  │  │  │  ├─ router.py
│  │  │  │  ├─ service.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ models.py
│  │  │  │  ├─ provider.py
│  │  │  │  ├─ policy.py
│  │  │  │  ├─ jobs/explain_findings.py
│  │  │  │  ├─ chain/explain.py
│  │  │  │  ├─ prompt/explain.py
│  │  │  │  ├─ output.py
│  │  │  │  ├─ dto.py
│  │  │  │  ├─ exceptions.py
│  │  │  │  └─ schema/{request,response}.py
│  │  │  └─ webhook/
│  │  │     ├─ router.py
│  │  │     ├─ verifier.py
│  │  │     ├─ service.py
│  │  │     ├─ repository.py
│  │  │     ├─ models.py
│  │  │     ├─ jobs/process_delivery.py
│  │  │     ├─ handler/{pull_request,installation}.py
│  │  │     ├─ dto.py
│  │  │     ├─ exceptions.py
│  │  │     └─ schema/github_event.py
│  │  └─ shared/
│  │     ├─ config/{settings,validation}.py
│  │     ├─ database/{base,engine,session,unit_of_work}.py
│  │     ├─ exception/{base,handlers,response}.py
│  │     ├─ security/{token_codec,hashing,secrets}.py
│  │     ├─ github/{client,oauth_client,installation_auth,provider_models,errors}.py
│  │     ├─ jobs/{contracts,models,store,runner,retry,registry}.py
│  │     └─ observability/{logging,redaction,middleware,health}.py
│  ├─ migrations/
│  │  ├─ env.py
│  │  └─ versions/
│  ├─ tests/{unit,integration,contract,architecture,fixtures}/
│  ├─ pyproject.toml
│  ├─ uv.lock                         uv 사용 시에만
│  ├─ alembic.ini
│  ├─ Dockerfile
│  └─ .env.example
├─ frontend/
│  ├─ src/
│  │  ├─ app/
│  │  ├─ features/{auth,workspace,repository,pull-request,analysis,review}/
│  │  └─ shared/{api,ui,types}/
│  ├─ tests/e2e/
│  ├─ package.json
│  └─ vercel.json
└─ .github/workflows/ci.yml
```

중괄호 표기는 각각의 별도 파일/폴더를 뜻한다. Python package의 `__init__.py`는 반복을 줄이기 위해 대부분 생략 표시했다. 패키지 관리 도구 선택은 구현 시 고정하며 `uv.lock`은 uv를 선택할 때만 만든다. 여러 lockfile을 혼용하지 않는다.

새 파일의 위치가 모호하면 [패키지 규칙](PACKAGE_RULES.md)을 읽고 해당 도메인 README를 수정한다. DIRECTORY_MAP은 길기 때문에 구조 변경/최초 scaffold 때만 읽는다.
