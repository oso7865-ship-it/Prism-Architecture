# Exception: 공통 부모와 응답 변환

> ID: `EXCEPTION` · 소유: `backend/app/shared/exception` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 예외 상속·오류 응답·실패 노출을 변경할 때

```text
shared/exception/
├─ base.py           AppException·ErrorKind
├─ handlers.py       FastAPI 전역 handler 등록
└─ response.py       ErrorResponse·FieldError
```

도메인별 오류는 `domain/<owner>/exceptions.py`에 두고 AppException을 상속한다. 공통 부모와 변환만 Shared가 소유한다.

```python
from enum import StrEnum

class ErrorKind(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    INVALID_INPUT = "INVALID_INPUT"
    UNAVAILABLE = "UNAVAILABLE"

class AppException(Exception):
    def __init__(self, *, code: str, public_message: str, kind: ErrorKind):
        super().__init__(public_message)
        self.code = code
        self.public_message = public_message
        self.kind = kind
```

```python
# domain/workspace/exceptions.py
class WorkspacePermissionDenied(AppException):
    def __init__(self) -> None:
        super().__init__(code="WORKSPACE_PERMISSION_DENIED",
                         public_message="이 작업을 수행할 권한이 없습니다.",
                         kind=ErrorKind.FORBIDDEN)
```

Handler가 ErrorKind를 HTTP 상태로 바꾼다. Service는 FastAPI HTTPException·Response를 import하지 않는다. 예외 kind와 error_code는 업무 의미를 보존하되 HTTP 표현은 밖에서 결정한다.

응답 기본형은 `{error: {code, message, trace_id, field_errors?}}`다. field_errors에는 위치/허용된 메시지만 넣고 원래 input 값은 제외한다. 비인증은 401, 인가 실패는 403을 기본으로 하고 타 테넌트 리소스 노출을 줄이기 위한 404 응답은 API 정책에서 일관되게 적용한다.

예상하지 못한 오류는 일반 INTERNAL_ERROR/500으로 변환한다. DB SQL·stack trace·GitHub token·source snippet·LLM 응답 원문을 사용자에게 반환하지 않는다. 서버 로그도 비밀 마스킹 규칙을 지킨다.

Job 실패는 이 Handler를 거치지 않고 해당 domain exception을 공개 error_code로 매핑하여 저장한다. HTTP Handler가 Job 재시도 정책을 소유하지 않는다.

검증: 도메인 예외 상속, ErrorKind 변환, Pydantic validation input 마스킹, unknown error 메시지, traceback 내 비밀 출력 차단, Worker와 HTTP의 일관된 공개 code.
