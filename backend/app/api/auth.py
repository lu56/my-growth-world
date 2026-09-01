"""认证接口"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models import ParentConfig
from app.schemas.schemas import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    config = db.query(ParentConfig).first()
    if not config or not verify_password(body.password, config.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="口令错误"
        )
    token = create_access_token(subject="parent")
    return Token(access_token=token)


@router.post("/child-login", response_model=Token)
def child_login(body: LoginRequest, db: Session = Depends(get_db)):
    """孩子登录（孩子口令）"""
    config = db.query(ParentConfig).first()
    if (
        not config
        or not config.child_password_hash
        or not verify_password(body.password, config.child_password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="口令错误"
        )
    token = create_access_token(subject="child", role="child")
    return Token(access_token=token)