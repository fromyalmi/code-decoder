from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.dependencies import get_current_user
from app.core.security import COOKIE_MAX_AGE, COOKIE_NAME, create_signed_cookie
from app.db import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest
from app.services.auth_service import (
    AccountLocked,
    EmailAlreadyExists,
    InvalidCredentials,
    login,
    signup,
)

router = APIRouter()

_INVALID_CREDENTIALS_BODY = {
    "error": {
        "code": "InvalidCredentials",
        "message": "이메일 또는 비밀번호가 틀렸어 🦜",
    }
}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup_handler(req: SignupRequest, session: Session = Depends(get_session)):
    try:
        user = signup(req, session)
    except EmailAlreadyExists:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "EmailAlreadyExists",
                    "message": "이미 사용 중인 이메일이에요.",
                }
            },
        )
    return {"id": str(user.id), "email": user.email, "nickname": user.nickname}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_handler(
    req: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
):
    try:
        user = login(req, session)
    except AccountLocked:
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "AccountLocked",
                    "message": "잠시 후 다시 시도해줘 🦜",
                }
            },
        )
    except InvalidCredentials:
        return JSONResponse(status_code=401, content=_INVALID_CREDENTIALS_BODY)

    response.set_cookie(
        key=COOKIE_NAME,
        value=create_signed_cookie(str(user.id)),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )
    return {"id": str(user.id), "email": user.email, "nickname": user.nickname}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_handler(
    response: Response,
    _: User = Depends(get_current_user),
):
    response.delete_cookie(key=COOKIE_NAME, httponly=True, secure=True, samesite="lax")
    return {}
