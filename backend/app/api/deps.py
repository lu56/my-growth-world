"""API 依赖：认证"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def require_parent(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """家长认证校验"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录"
        )
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "parent":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败"
        )
    return payload


def require_child(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """孩子认证校验"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录"
        )
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "child":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="认证失败"
        )
    return payload