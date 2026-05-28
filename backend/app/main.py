from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.preprocessing.validator import InputTooLarge
from app.routers.analyses import router as analyses_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

app = FastAPI(title="Code Decoder API")


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
