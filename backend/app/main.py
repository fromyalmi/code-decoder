from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AnalysisNotFound, DailyLimitExceeded, LLMFailure
from app.models import analysis as _analysis_models  # noqa: F401
from app.models import cache as _cache_models  # noqa: F401 — registers AnalysisCache in metadata
from app.models import daily_limit_log as _log_models  # noqa: F401
from app.models import key_concept as _kc_models  # noqa: F401
from app.models import line_explanation as _le_models  # noqa: F401
from app.models import reward as _reward_models  # noqa: F401
from app.preprocessing.validator import InputTooLarge
from app.routers.analyses import router as analyses_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

app = FastAPI(title="Code Decoder API")


@app.exception_handler(LLMFailure)
async def llm_failure_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "LLM_FAILURE",
                "message": "🦜 미안, 지금 좀 문제가 생겼어",
            }
        },
    )


@app.exception_handler(DailyLimitExceeded)
async def daily_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "DAILY_LIMIT_EXCEEDED",
                "message": "🦜 오늘 한도 다 썼어 — 자정에 다시 풀려!",
            }
        },
    )


@app.exception_handler(AnalysisNotFound)
async def analysis_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": "🦜 분석을 찾을 수 없어"}},
    )


@app.exception_handler(InputTooLarge)
async def input_too_large_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INPUT_TOO_LARGE",
                "message": "🦜 코드가 너무 길어 — 4,000토큰 이하로 부탁해",
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {"code": "VALIDATION_ERROR", "message": "🦜 입력값을 확인해줘"}
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "Error", "message": str(exc.detail)}},
    )


app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1")
app.include_router(analyses_router, prefix="/api/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
